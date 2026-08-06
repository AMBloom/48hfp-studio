"""Unit tests for Sprint 5.2 / Sprint 5.4 Root Callback Integration."""

from unittest.mock import patch
from typer.testing import CliRunner
from studio.cli import app

runner = CliRunner()


def test_root_command_launches_studio_app():
    """Verify root command instantiates and runs StudioApp TUI."""
    with patch("studio.cli.StudioApp.run") as mock_run:
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert mock_run.called


def test_subcommand_bypasses_root_helper():
    """Verify subcommands (e.g. info) bypass TUI launch."""
    with patch("studio.cli.profile_exists", return_value=False):
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "System Information" in result.output
