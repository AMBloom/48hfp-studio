"""Unit tests for Sprint 5.4 (v2.0 Roadmap & Textual Scaffolding)."""

from unittest.mock import patch
import pytest
from typer.testing import CliRunner

from studio.cli import app
from studio.tui import StudioApp, HeaderHUD, NavigationSidebar, StudioWorkspace

runner = CliRunner()


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_studio_app_initialization():
    """Verify StudioApp instantiates with correct title and attributes."""
    app_instance = StudioApp()
    assert app_instance.TITLE == "48HFP-Studio v2.0"


@pytest.mark.anyio
async def test_studio_app_run_test():
    """Verify StudioApp mounts widgets inside active app test driver."""
    app_instance = StudioApp()
    async with app_instance.run_test() as pilot:
        header = app_instance.query_one(HeaderHUD)
        sidebar = app_instance.query_one(NavigationSidebar)
        workspace = app_instance.query_one(StudioWorkspace)

        assert header is not None
        assert sidebar is not None
        assert workspace is not None
        assert "🎬 48HFP-Studio v2.0" in header.render()


def test_cli_root_launches_studio_app():
    """Verify CLI root command calls StudioApp.run()."""
    with patch("studio.cli.StudioApp.run") as mock_run:
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        mock_run.assert_called_once()


def test_cli_subcommands_bypass_tui():
    """Verify subcommands like info and prompt bypass TUI launch."""
    with patch("studio.cli.StudioApp.run") as mock_run:
        result_info = runner.invoke(app, ["info"])
        assert result_info.exit_code == 0
        assert "System Information" in result_info.output
        mock_run.assert_not_called()

    with patch("studio.cli.StudioApp.run") as mock_run:
        result_prompt = runner.invoke(app, ["--help"])
        assert result_prompt.exit_code == 0
        assert "48HFP-Studio" in result_prompt.output
        mock_run.assert_not_called()
