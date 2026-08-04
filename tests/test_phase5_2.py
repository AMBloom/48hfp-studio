"""Unit tests for Sprint 5.2 (State-Aware Root Helper)."""

from unittest.mock import patch
from typer.testing import CliRunner
from studio.cli import app

runner = CliRunner()


def test_root_helper_stage_1_no_profile():
    """Verify Stage 1 panel rendering when no profile exists."""
    with patch("studio.cli.profile_exists", return_value=False):
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "What's Next? (Stage 1: Setup)" in result.output
        assert "You haven't configured your team yet." in result.output
        assert "python main.py config setup" in result.output


def test_root_helper_stage_2_profile_no_draw():
    """Verify Stage 2 panel rendering when profile exists but no draw exists."""
    with patch("studio.cli.profile_exists", return_value=True), patch(
        "studio.cli.draw_exists", return_value=False
    ):
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "What's Next? (Stage 2: Kickoff Draw)" in result.output
        assert "Your team is configured" in result.output
        assert "Friday" in result.output
        assert "draw wizard" in result.output
        assert "python main.py config setup" in result.output


def test_root_helper_stage_3_profile_and_draw():
    """Verify Stage 3 panel rendering when both profile and draw exist."""
    with patch("studio.cli.profile_exists", return_value=True), patch(
        "studio.cli.draw_exists", return_value=True
    ):
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "What's Next? (Stage 3: Ready for Generation)" in result.output
        assert "All systems go" in result.output
        assert "python main.py generate" in result.output
        assert "python main.py constraints" in result.output
        assert "python main.py draw reset" in result.output


def test_subcommand_bypasses_root_helper():
    """Verify subcommands (e.g. info) bypass root helper logic."""
    with patch("studio.cli.profile_exists", return_value=False):
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "System Information" in result.output
        assert "What's Next? (Stage 1: Setup)" not in result.output
