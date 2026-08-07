"""Unit tests for Sprint 6.2 (In-TUI Friday Draw Wizard & Profile Setup Modals)."""

from unittest.mock import patch
import pytest
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.screens import DrawWizardScreen, ProfileSetupScreen
from studio.tui import HeaderHUD, NavigationSidebar, StudioApp, StudioWorkspace
from textual.widgets import Input, Select


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def sample_profile():
    return TeamProfile(
        team_name="Cyber Directors",
        admin_username="alex_admin",
        location="San Francisco, CA",
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
async def test_draw_wizard_screen_submit(tmp_path):
    """Verify DrawWizardScreen form completion, persistence call, and result dismissal."""
    test_draw_file = tmp_path / ".48hfp_draw.yaml"

    with patch("studio.utils.draw_store.get_draw_path", return_value=test_draw_file):
        app = StudioApp()
        async with app.run_test() as pilot:
            screen = DrawWizardScreen()
            
            # Dismiss result holder
            result_container = []

            def on_dismiss(result):
                result_container.append(result)

            app.push_screen(screen, callback=on_dismiss)
            await pilot.pause()

            # Fill in form fields
            screen.query_one("#character_name", Input).value = "Jordan Vance"
            screen.query_one("#character_trait", Input).value = "Stunt Performer"
            screen.query_one("#character_gender", Input).value = "Non-Binary"
            screen.query_one("#required_prop", Input).value = "Neon Helmet"
            screen.query_one("#required_line", Input).value = "Watch this move."

            # Click save button
            await pilot.click("#save_draw_btn")
            await pilot.pause()

            assert len(result_container) == 1
            saved_draw = result_container[0]
            assert isinstance(saved_draw, FridayDraw)
            assert saved_draw.character_name == "Jordan Vance"
            assert saved_draw.character_trait == "Stunt Performer"
            assert saved_draw.required_prop == "Neon Helmet"
            assert saved_draw.required_line == "Watch this move."
            assert test_draw_file.exists()


@pytest.mark.anyio
async def test_draw_wizard_screen_fallback(tmp_path):
    """Verify DrawWizardScreen automatically applies fallback choices for blank form fields."""
    test_draw_file = tmp_path / ".48hfp_draw.yaml"

    with patch("studio.utils.draw_store.get_draw_path", return_value=test_draw_file):
        app = StudioApp()
        async with app.run_test() as pilot:
            screen = DrawWizardScreen()
            result_container = []

            app.push_screen(screen, callback=lambda res: result_container.append(res))
            await pilot.pause()

            # Click save without filling inputs (triggers create_default_draw fallbacks)
            await pilot.click("#save_draw_btn")
            await pilot.pause()

            assert len(result_container) == 1
            saved_draw = result_container[0]
            assert isinstance(saved_draw, FridayDraw)
            assert len(saved_draw.character_name) > 0
            assert len(saved_draw.character_trait) > 0
            assert len(saved_draw.required_prop) > 0
            assert len(saved_draw.required_line) > 0


@pytest.mark.anyio
async def test_draw_wizard_screen_cancel():
    """Verify DrawWizardScreen dismisses returning None when canceled."""
    app = StudioApp()
    async with app.run_test() as pilot:
        screen = DrawWizardScreen()
        result_container = []

        app.push_screen(screen, callback=lambda res: result_container.append(res))
        await pilot.pause()

        await pilot.click("#cancel_draw_btn")
        await pilot.pause()

        assert len(result_container) == 1
        assert result_container[0] is None


@pytest.mark.anyio
async def test_profile_setup_screen_submit(tmp_path):
    """Verify ProfileSetupScreen form entry, profile creation, saving, and dismissal."""
    test_profile_file = tmp_path / ".48hfp_profile.yaml"

    with patch("studio.utils.profile_store.get_profile_path", return_value=test_profile_file):
        app = StudioApp()
        async with app.run_test() as pilot:
            screen = ProfileSetupScreen()
            result_container = []

            app.push_screen(screen, callback=lambda res: result_container.append(res))
            await pilot.pause()

            screen.query_one("#team_name", Input).value = "Apex Cinema"
            screen.query_one("#admin_username", Input).value = "apex_admin"
            screen.query_one("#location", Input).value = "Austin, TX"

            await pilot.click("#save_profile_btn")
            await pilot.pause()

            assert len(result_container) == 1
            saved_profile = result_container[0]
            assert isinstance(saved_profile, TeamProfile)
            assert saved_profile.team_name == "Apex Cinema"
            assert saved_profile.admin_username == "apex_admin"
            assert saved_profile.location == "Austin, TX"
            assert test_profile_file.exists()


@pytest.mark.anyio
async def test_profile_setup_screen_cancel():
    """Verify ProfileSetupScreen dismisses returning None when canceled."""
    app = StudioApp()
    async with app.run_test() as pilot:
        screen = ProfileSetupScreen()
        result_container = []

        app.push_screen(screen, callback=lambda res: result_container.append(res))
        await pilot.pause()

        await pilot.click("#cancel_profile_btn")
        await pilot.pause()

        assert len(result_container) == 1
        assert result_container[0] is None


@pytest.mark.anyio
async def test_tui_integration_callbacks_and_reactivity(sample_profile, sample_draw):
    """Verify StudioApp modal launch callbacks dynamically update app state and UI components."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            sidebar = app.query_one(NavigationSidebar)
            workspace = app.query_one(StudioWorkspace)
            header = app.query_one(HeaderHUD)

            assert app.app_profile is None
            assert app.app_draw is None

            # Test profile setup callback
            app.update_profile(sample_profile)
            await pilot.pause()

            assert app.app_profile == sample_profile
            assert sidebar.profile == sample_profile
            assert header.profile == sample_profile

            # Test draw wizard callback
            app.update_draw(sample_draw)
            await pilot.pause()

            assert app.app_draw == sample_draw
            assert workspace.draw == sample_draw
            assert header.draw == sample_draw
