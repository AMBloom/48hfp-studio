"""Unit tests for Sprint 6.6 (TUI Bug Fixes & Reactive State Patches)."""

from unittest.mock import patch
import pytest

from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.screens_constraints import (
    DirectorialVisionScreen,
    LogisticalConstraintScreen,
)
from studio.screens_library import ConstraintLibraryScreen
from studio.tui import StudioApp
from studio.workspace import RecipePane


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_recipe_pane_css_overflow_fix():
    """Verify RecipePane DEFAULT_CSS has overflow-x: hidden; and width: 100%; on #recipe-content."""
    css = RecipePane.DEFAULT_CSS
    assert "#recipe-content" in css
    assert "width: 100%;" in css
    assert "overflow-x: hidden;" in css


def test_constraint_library_css_width_fix():
    """Verify ConstraintLibraryScreen DEFAULT_CSS has width: 95vw; and max-width: 140; on #library-dialog."""
    css = ConstraintLibraryScreen.DEFAULT_CSS
    assert "#library-dialog" in css
    assert "width: 95vw;" in css
    assert "max-width: 140;" in css


def test_screens_constraints_css_vertical_scroll_height():
    """Verify LogisticalConstraintScreen and DirectorialVisionScreen DEFAULT_CSS have VerticalScroll height: 1fr;."""
    log_css = LogisticalConstraintScreen.DEFAULT_CSS
    dir_css = DirectorialVisionScreen.DEFAULT_CSS

    assert "VerticalScroll" in log_css
    assert "height: 1fr;" in log_css

    assert "VerticalScroll" in dir_css
    assert "height: 1fr;" in dir_css


@pytest.mark.anyio
async def test_tui_reactive_state_reload_on_callbacks(tmp_path):
    """Verify update_profile and update_draw reload from disk to guarantee object identity change."""
    profile_file = tmp_path / ".48hfp_profile.yaml"
    draw_file = tmp_path / ".48hfp_draw.json"

    loaded_profile = TeamProfile(
        team_name="Reloaded Team",
        admin_username="reloaded_admin",
        location="New York",
    )
    loaded_draw = FridayDraw(
        genre_1="Sci-Fi",
        genre_2="Comedy",
        character_name="Dr. Reload",
        character_trait="Curious",
        required_prop="Flashlight",
        required_line="Let's try again.",
    )

    with patch("studio.utils.profile_store.get_profile_path", return_value=profile_file), patch(
        "studio.utils.draw_store.get_draw_path", return_value=draw_file
    ), patch(
        "studio.tui.load_profile", return_value=loaded_profile
    ), patch(
        "studio.tui.load_draw", return_value=loaded_draw
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Trigger update_profile
            dummy_profile = TeamProfile(team_name="Dummy", admin_username="dummy", location="Test City")
            app.update_profile(dummy_profile)
            await pilot.pause()

            assert app.app_profile == loaded_profile
            assert app.app_profile.team_name == "Reloaded Team"

            # Trigger update_draw
            dummy_draw = FridayDraw(
                genre_1="Horror",
                genre_2="Drama",
                character_name="Dummy",
                character_trait="Trait",
                required_prop="Prop",
                required_line="Line",
            )
            app.update_draw(dummy_draw)
            await pilot.pause()

            assert app.app_draw == loaded_draw
            assert app.app_draw.genre_1 == "Sci-Fi"
