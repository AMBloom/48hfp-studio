"""Unit tests for Sprint 6.4 (In-TUI Constraint Library Management CRUD)."""

from unittest.mock import patch
import pytest
from studio.models.constraints import DirectorialVision, LogisticalConstraint
from studio.models.profile import TeamProfile
from studio.screens_constraints import (
    DirectorialVisionScreen,
    LogisticalConstraintScreen,
)
from studio.screens_library import ConstraintLibraryScreen
from studio.tui import NavigationSidebar, StudioApp
from studio.utils.constraint_store import (
    save_directorial_vision,
    save_logistical_constraint,
)
from textual.widgets import Button, Input, TextArea


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def sample_profile():
    return TeamProfile(
        team_name="Cyber Directors",
        admin_username="alex_admin",
        location="San Francisco, CA",
        active_logistical_constraint=None,
        active_directorial_vision=None,
    )


@pytest.mark.anyio
async def test_logistical_constraint_screen_submit(tmp_path):
    """Verify LogisticalConstraintScreen form submission, persistence, and result dismissal."""
    constraints_dir = tmp_path / "constraints"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir):
        app = StudioApp()
        async with app.run_test() as pilot:
            screen = LogisticalConstraintScreen()
            result_container = []

            app.push_screen(screen, callback=lambda res: result_container.append(res))
            await pilot.pause()

            screen.query_one("#name", Input).value = "warehouse_night"
            screen.query_one("#description", Input).value = "Abandoned industrial warehouse at night"
            screen.query_one("#locations", Input).value = "Warehouse, Industrial, Night"
            screen.query_one("#sub_locations", Input).value = "Loading Dock, Boiler Room"
            screen.query_one("#location_details", TextArea).text = "Echoey acoustics with harsh overhead spotlights"
            screen.query_one("#available_set_dressing", TextArea).text = "Heavy keyring\nSecurity uniform"

            await pilot.click("#save_logistical_btn")
            await pilot.pause()

            assert len(result_container) == 1
            saved = result_container[0]
            assert isinstance(saved, LogisticalConstraint)
            assert saved.name == "warehouse_night"
            assert "Warehouse" in saved.locations
            assert "Boiler Room" in saved.sub_locations
            assert "Heavy keyring" in saved.available_set_dressing

            saved_file = constraints_dir / "logistical" / "warehouse_night.yaml"
            assert saved_file.exists()


@pytest.mark.anyio
async def test_logistical_constraint_screen_cancel():
    """Verify LogisticalConstraintScreen dismisses returning None when canceled."""
    app = StudioApp()
    async with app.run_test() as pilot:
        screen = LogisticalConstraintScreen()
        result_container = []

        app.push_screen(screen, callback=lambda res: result_container.append(res))
        await pilot.pause()

        await pilot.click("#cancel_logistical_btn")
        await pilot.pause()

        assert len(result_container) == 1
        assert result_container[0] is None


@pytest.mark.anyio
async def test_directorial_vision_screen_submit(tmp_path):
    """Verify DirectorialVisionScreen form submission, persistence, and result dismissal."""
    constraints_dir = tmp_path / "constraints"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir):
        app = StudioApp()
        async with app.run_test() as pilot:
            screen = DirectorialVisionScreen()
            result_container = []

            app.push_screen(screen, callback=lambda res: result_container.append(res))
            await pilot.pause()

            screen.query_one("#name", Input).value = "neo_noir_noir"
            screen.query_one("#description", Input).value = "Gritty urban thriller"
            screen.query_one("#visual_economy", TextArea).text = "Sharp, rhythmic cuts with voiceover monologues"
            screen.query_one("#lighting_color", TextArea).text = "High contrast shadows with neon reflections"
            screen.query_one("#audio_landscape", TextArea).text = "Ambient acoustic score"

            await pilot.click("#save_directorial_btn")
            await pilot.pause()

            assert len(result_container) == 1
            saved = result_container[0]
            assert isinstance(saved, DirectorialVision)
            assert saved.name == "neo_noir_noir"
            assert "High contrast" in saved.lighting_color

            saved_file = constraints_dir / "directorial" / "neo_noir_noir.yaml"
            assert saved_file.exists()


@pytest.mark.anyio
async def test_directorial_vision_screen_cancel():
    """Verify DirectorialVisionScreen dismisses returning None when canceled."""
    app = StudioApp()
    async with app.run_test() as pilot:
        screen = DirectorialVisionScreen()
        result_container = []

        app.push_screen(screen, callback=lambda res: result_container.append(res))
        await pilot.pause()

        await pilot.click("#cancel_directorial_btn")
        await pilot.pause()

        assert len(result_container) == 1
        assert result_container[0] is None


@pytest.mark.anyio
async def test_constraint_library_screen_rendering_and_set_active(tmp_path, sample_profile):
    """Verify ConstraintLibraryScreen list rendering, set active action, and profile updates."""
    constraints_dir = tmp_path / "constraints"
    profile_file = tmp_path / ".48hfp_profile.yaml"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir), patch(
        "studio.utils.profile_store.get_profile_path", return_value=profile_file
    ):
        # Pre-seed one logistical and directorial set
        log_c = LogisticalConstraint(name="studio_soundstage", description="Controlled soundstage environment")
        dir_c = DirectorialVision(name="cyberpunk_fever", description="Futuristic dystopian energy")
        save_logistical_constraint(log_c)
        save_directorial_vision(dir_c)

        app = StudioApp()
        async with app.run_test() as pilot:
            screen = ConstraintLibraryScreen(sample_profile)
            result_container = []

            app.push_screen(screen, callback=lambda res: result_container.append(res))
            await pilot.pause()

            # Verify tables rendered seeded constraints
            log_table = screen.query_one("#logistical_table")
            dir_table = screen.query_one("#directorial_table")

            assert log_table.row_count >= 1
            assert dir_table.row_count >= 1

            # Click Set Active on logistical table
            log_table.focus()
            row_idx = log_table.get_row_index("studio_soundstage")
            log_table.move_cursor(row=row_idx)
            await pilot.pause()
            screen.query_one("#btn_set_active", Button).press()
            await pilot.pause()

            assert sample_profile.active_logistical_constraint == "studio_soundstage"

            # Close library modal
            await pilot.press("escape")
            await pilot.pause()

            assert len(result_container) == 1
            assert result_container[0].active_logistical_constraint == "studio_soundstage"


@pytest.mark.anyio
async def test_constraint_library_delete(tmp_path, sample_profile):
    """Verify deleting a constraint set removes file from disk and clears active profile reference."""
    constraints_dir = tmp_path / "constraints"
    profile_file = tmp_path / ".48hfp_profile.yaml"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir), patch(
        "studio.utils.profile_store.get_profile_path", return_value=profile_file
    ):
        log_c = LogisticalConstraint(name="temp_to_delete", description="Temporary set")
        save_logistical_constraint(log_c)
        sample_profile.active_logistical_constraint = "temp_to_delete"

        app = StudioApp()
        async with app.run_test() as pilot:
            screen = ConstraintLibraryScreen(sample_profile)

            app.push_screen(screen)
            await pilot.pause()

            log_table = screen.query_one("#logistical_table")
            log_table.focus()
            row_idx = log_table.get_row_index("temp_to_delete")
            log_table.move_cursor(row=row_idx)
            await pilot.pause()

            screen.query_one("#btn_delete_selected", Button).press()
            await pilot.pause()

            # Verify file was deleted and profile active pointer cleared
            deleted_file = constraints_dir / "logistical" / "temp_to_delete.yaml"
            assert not deleted_file.exists()
            assert sample_profile.active_logistical_constraint is None


@pytest.mark.anyio
async def test_tui_integration_library_trigger():
    """Verify StudioApp constraint library action pushes ConstraintLibraryScreen modal."""
    app = StudioApp()
    async with app.run_test() as pilot:
        sidebar = app.query_one(NavigationSidebar)
        assert len(app.screen_stack) == 1

        # Press key 'l' to trigger Constraint Library modal
        await pilot.press("l")
        await pilot.pause()

        assert len(app.screen_stack) == 2
        assert isinstance(app.screen, ConstraintLibraryScreen)

        # Escape to dismiss
        await pilot.press("escape")
        await pilot.pause()

        assert len(app.screen_stack) == 1

