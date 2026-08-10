"""Unit tests for Sprint 6.1 (Live Widget Binding & Real-Time Profile/Draw Sync)."""

from unittest.mock import patch
import pytest
from studio.models.profile import TeamProfile
from studio.models.draw import FridayDraw
from studio.tui import StudioApp, HeaderHUD, NavigationSidebar, StudioWorkspace
from studio.workspace import RecipePane
from textual.widgets import Button, Static



@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def sample_profile():
    return TeamProfile(
        team_name="Cyber Directors",
        admin_username="alex_admin",
        location="San Francisco, CA",
        active_logistical_constraint="SF Locations",
        active_directorial_vision="Sci-Fi Toolkit",
    )


@pytest.fixture
def sample_draw():
    return FridayDraw(
        genre_1="Sci Fi",
        genre_2="Heist",
        character_name="Sam Taylor",
        character_trait="Quantum Physicist",
        character_gender="Non-Binary",
        required_prop="Silver Chronometer",
        required_line="We are out of time.",
    )


@pytest.mark.anyio
async def test_studio_app_on_mount_initialization(sample_profile, sample_draw):
    """Verify StudioApp.on_mount loads profile and draw stores into reactive properties."""
    with patch("studio.tui.load_profile", return_value=sample_profile), patch(
        "studio.tui.load_draw", return_value=sample_draw
    ):
        app = StudioApp()
        async with app.run_test():
            assert app.app_profile == sample_profile
            assert app.app_draw == sample_draw

            workspace = app.query_one(StudioWorkspace)
            header = app.query_one(HeaderHUD)

            assert workspace.draw == sample_draw
            assert header.profile == sample_profile


@pytest.mark.anyio
async def test_reactive_watchers_propagation(sample_profile, sample_draw):
    """Verify state changes on StudioApp propagate down to child widgets via watchers."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test():
            workspace = app.query_one(StudioWorkspace)
            header = app.query_one(HeaderHUD)

            assert workspace.draw is None

            # Mutate reactive state on parent app
            app.app_profile = sample_profile
            app.app_draw = sample_draw

            assert workspace.draw == sample_draw
            assert header.profile == sample_profile


@pytest.mark.anyio
async def test_sidebar_dynamic_rendering(sample_profile):
    """Verify NavigationSidebar renders navigation buttons."""
    app = StudioApp()
    async with app.run_test():
        sidebar = app.query_one(NavigationSidebar)
        btn_ids = [b.id for b in sidebar.query(Button)]
        assert "btn_workspace_modal" in btn_ids
        assert "btn_profile_modal" in btn_ids



@pytest.mark.anyio
async def test_workspace_dynamic_rendering(sample_draw):
    """Verify StudioWorkspace dynamic content when draw is set vs None."""
    app = StudioApp()
    async with app.run_test():
        workspace = app.query_one(StudioWorkspace)
        recipe = workspace.query_one(RecipePane)
        recipe_static = recipe.query_one("#recipe-content", Static)

        workspace.draw = None
        workspace.update_content()
        assert "NO DRAW RECORDED" in str(recipe_static.render())

        workspace.draw = sample_draw
        workspace.update_content()
        assert "ACTIVE FRIDAY DRAW" in str(recipe_static.render())
        assert "Sci Fi" in str(recipe_static.render())
        assert "Heist" in str(recipe_static.render())
        assert "Sam Taylor" in str(recipe_static.render())
        assert "Silver Chronometer" in str(recipe_static.render())
        assert "We are out of time." in str(recipe_static.render())
