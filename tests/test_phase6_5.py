"""Unit tests for Sprint 6.5 (Form Expansions, UX Polish, and API Persistence)."""

import json
import os
from unittest.mock import MagicMock, patch
import pytest
from studio.inference import InferenceEngine, InferenceError
from studio.models.constraints import LogisticalConstraint
from studio.models.profile import TeamProfile
from studio.screens import ApiSettingsScreen, ProfileSetupScreen
from studio.screens_library import ConstraintLibraryScreen
from studio.tui import NavigationSidebar, StudioApp
from studio.utils.constraint_store import save_logistical_constraint
from textual.widgets import Button, DataTable, Input, Select


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
        active_creative_constraint=None,
    )


@pytest.mark.anyio
async def test_api_settings_screen_save_and_env_persistence(tmp_path, monkeypatch):
    """Verify ApiSettingsScreen saves credentials to .env file and updates os.environ."""
    env_file = tmp_path / ".env"
    monkeypatch.chdir(tmp_path)

    app = StudioApp()
    async with app.run_test() as pilot:
        screen = ApiSettingsScreen()
        result_container = []

        app.push_screen(screen, callback=lambda res: result_container.append(res))
        await pilot.pause()

        screen.query_one("#api_key", Input).value = "AIzaSyTEST_SECRET_KEY_12345"
        screen.query_one("#gemini_model", Select).value = "gemini-3.5-flash"

        screen.query_one("#save_api_settings_btn", Button).press()
        await pilot.pause()

        assert len(result_container) == 1
        res = result_container[0]
        assert res["api_key"] == "AIzaSyTEST_SECRET_KEY_12345"
        assert res["model"] == "gemini-3.5-flash"

        assert os.environ.get("GEMINI_API_KEY") == "AIzaSyTEST_SECRET_KEY_12345"
        assert os.environ.get("GEMINI_MODEL") == "gemini-3.5-flash"

        assert env_file.exists()
        env_content = env_file.read_text()
        assert "GEMINI_API_KEY" in env_content
        assert "AIzaSyTEST_SECRET_KEY_12345" in env_content


@pytest.mark.anyio
async def test_profile_setup_screen_dynamic_roster_and_removal(tmp_path):
    """Verify ProfileSetupScreen dynamic roster addition, removal, and profile save."""
    profile_file = tmp_path / ".48hfp_profile.yaml"

    with patch("studio.utils.profile_store.get_profile_path", return_value=profile_file):
        app = StudioApp()
        async with app.run_test() as pilot:
            screen = ProfileSetupScreen()
            result_container = []

            app.push_screen(screen, callback=lambda res: result_container.append(res))
            await pilot.pause()

            screen.query_one("#team_name", Input).value = "Indie Roster Team"
            screen.query_one("#admin_username", Input).value = "roster_admin"
            screen.query_one("#location", Input).value = "Austin, TX"

            # Add Member 1: Director -> Alice
            screen.query_one("#roster_role", Select).value = "Director"
            screen.query_one("#roster_member_name", Input).value = "Alice Director"
            screen.action_add_member()
            await pilot.pause()

            # Add Member 2: Gaffer / Grip -> Bob
            screen.query_one("#roster_role", Select).value = "Gaffer / Grip"
            screen.query_one("#roster_member_name", Input).value = "Bob Grip"
            screen.action_add_member()
            await pilot.pause()

            table = screen.query_one("#roster_table", DataTable)
            assert table.row_count == 2

            # Remove Alice
            table.move_cursor(row=0)
            await pilot.pause()
            screen.action_remove_selected_member()
            await pilot.pause()

            assert table.row_count == 1

            # Save Profile
            screen.query_one("#save_profile_btn", Button).press()
            await pilot.pause()

            assert len(result_container) == 1
            saved = result_container[0]
            assert saved.team_name == "Indie Roster Team"
            assert "Director" not in saved.roles
            assert "Gaffer / Grip" in saved.roles
            assert "Bob Grip" in saved.roles["Gaffer / Grip"]


@pytest.mark.anyio
async def test_constraint_library_focus_persistence(tmp_path, sample_profile):
    """Verify ConstraintLibraryScreen selection persistence when clicking buttons that steal focus."""
    constraints_dir = tmp_path / "constraints"
    profile_file = tmp_path / ".48hfp_profile.yaml"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir), patch(
        "studio.utils.profile_store.get_profile_path", return_value=profile_file
    ):
        log_c = LogisticalConstraint(name="warehouse_set", description="Night warehouse shoot")
        save_logistical_constraint(log_c)

        app = StudioApp()
        async with app.run_test() as pilot:
            screen = ConstraintLibraryScreen(sample_profile)
            result_container = []

            app.push_screen(screen, callback=lambda res: result_container.append(res))
            await pilot.pause()

            log_table = screen.query_one("#logistical_table", DataTable)
            log_table.focus()
            row_idx = log_table.get_row_index("warehouse_set")
            log_table.move_cursor(row=row_idx)
            await pilot.pause()

            # Click Set Active button (which steals focus from log_table to button)
            screen.query_one("#btn_set_active", Button).press()
            await pilot.pause()

            assert sample_profile.active_logistical_constraint == "warehouse_set"

            # Click Delete Selected button
            screen.query_one("#btn_delete_selected", Button).press()
            await pilot.pause()

            assert sample_profile.active_logistical_constraint is None
            deleted_file = constraints_dir / "logistical" / "warehouse_set.yaml"
            assert not deleted_file.exists()


def test_inference_engine_retry_on_transient_error(monkeypatch):
    """Verify InferenceEngine retries on 503 transient errors and succeeds on subsequent attempt."""
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "title_and_logline": {
            "title": "Test Title",
            "genre_blend": "Drama / Sci-Fi",
            "logline": "A test logline."
        },
        "character_roster": [],
        "synopsis": {
            "act_1_setup": "Act 1 setup text.",
            "act_2_escalation": "Act 2 escalation text.",
            "act_3_climax_resolution": "Act 3 climax text.",
            "thematic_arc": "Thematic arc text."
        },
        "scene_breakdown": [],
        "dialogue_snippets": [],
        "compliance_checklist": {
            "verbatim_line_verified": True,
            "prop_usage_verified": True,
            "character_linkage_verified": True,
            "pacing_runtime_verified": True,
            "compliance_notes": "All checks passed."
        }
    })
    mock_response.parsed = None

    attempts = {"count": 0}

    def mock_generate_content(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise Exception("503 Service Unavailable: Overloaded endpoint")
        return mock_response

    mock_client.models.generate_content = mock_generate_content

    with patch("studio.inference.genai.Client", return_value=mock_client), patch("time.sleep"):
        res = InferenceEngine.generate_treatment("Test prompt")
        assert attempts["count"] == 3
        assert res.title_and_logline.title == "Test Title"


@pytest.mark.anyio
async def test_navigation_sidebar_rendering():
    """Verify NavigationSidebar renders clean action buttons and status header."""
    app = StudioApp()
    async with app.run_test() as pilot:
        sidebar = app.query_one(NavigationSidebar)
        assert sidebar.query_one("#btn_profile_modal", Button) is not None
        assert sidebar.query_one("#btn_draw_modal", Button) is not None
        assert sidebar.query_one("#btn_library_modal", Button) is not None
        assert sidebar.query_one("#btn_settings_modal", Button) is not None
