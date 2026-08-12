"""Unit and integration tests for Phase 8, Sprint 8.4: Test Isolation & TUI Workspace Manager."""

from pathlib import Path
import pytest
from textual.widgets import Button, Input

from studio.screens_workspace import WorkspaceManagerScreen
from studio.tui import HeaderHUD, NavigationSidebar, StudioApp
from studio.utils.global_state import clear_active_workspace, get_active_workspace, set_active_workspace


@pytest.fixture(autouse=True)
def clean_global_state(tmp_path, monkeypatch):
    """Fixture ensuring an isolated global_state file and workspace for every test."""
    dummy_state_file = tmp_path / "global_state.yaml"
    monkeypatch.setattr("studio.utils.global_state.GLOBAL_STATE_FILE", dummy_state_file)
    monkeypatch.setattr("studio.utils.global_state.GLOBAL_STATE_DIR", tmp_path)
    clear_active_workspace()
    yield
    clear_active_workspace()


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_workspace_manager_screen_instantiation() -> None:
    """Test WorkspaceManagerScreen modal instantiation."""
    modal = WorkspaceManagerScreen()
    assert modal is not None


def test_workspace_sidebar_button_order() -> None:
    """Test NavigationSidebar button order and IDs."""
    sidebar = NavigationSidebar()
    buttons = list(sidebar.compose())
    button_ids = [b.id for b in buttons if isinstance(b, Button)]

    expected_ids = [
        "btn_profile_modal",
        "btn_workspace_modal",
        "btn_load_drafts",
        "btn_quiz_modal",
        "btn_library_modal",
        "btn_draw_modal",
        "btn_settings_modal",
    ]
    assert button_ids == expected_ids


@pytest.mark.anyio
async def test_workspace_manager_submission(tmp_path: Path) -> None:
    """Test WorkspaceManagerScreen path submission, workspace initialization, and constraint seeding."""
    target_ws = tmp_path / "new_film_workspace"

    app = StudioApp()
    async with app.run_test(size=(120, 40)) as pilot:
        screen = WorkspaceManagerScreen()
        app.push_screen(screen)
        await pilot.pause()

        # Input target path
        input_widget = screen.query_one("#workspace_path_input", Input)
        input_widget.value = str(target_ws)

        # Submit workspace via action
        screen.action_submit_workspace()
        await pilot.pause()


        # Verify active workspace updated and seeded
        assert get_active_workspace() == target_ws.resolve()
        assert (target_ws / "constraints" / "logistical").exists()
        assert (target_ws / "constraints" / "directorial").exists()

        # Verify HeaderHUD displays new workspace
        hud = app.query_one(HeaderHUD)
        assert "Workspace: new_film_workspace" in hud.render()
