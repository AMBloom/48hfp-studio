"""Unit tests for Sprint 6.3 (In-TUI Treatment Generator & Split-Pane Workspace)."""

from pathlib import Path
from unittest.mock import patch
import pytest

from studio.inference import InferenceError
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.models.treatment import (
    CharacterRosterItem,
    DialogueSnippetItem,
    FestivalComplianceChecklist,
    NarrativeSynopsis,
    SceneBreakdownItem,
    TitleAndLogline,
    TreatmentOutput,
)
from studio.tui import StudioApp
from studio.workspace import OutputPane, RecipePane, StudioWorkspace
from textual.widgets import Button, LoadingIndicator, Markdown


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def sample_profile():
    return TeamProfile(
        team_name="Cyber Directors",
        admin_username="alex_admin",
        location="San Francisco, CA",
        active_logistical_constraint="Indie Micro-Budget",
        active_creative_constraint="Film Noir Directorial",
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


@pytest.fixture
def sample_treatment():
    return TreatmentOutput(
        title_and_logline=TitleAndLogline(
            title="CHRONO SHIFT",
            genre_blend="Sci Fi / Heist",
            logline="A physicist steals a time displacement device before sunset.",
        ),
        character_roster=[
            CharacterRosterItem(
                name="Sam Taylor",
                actor_or_traits="Quantum Physicist",
                role="Protagonist",
                is_required_character=True,
            )
        ],
        synopsis=NarrativeSynopsis(
            act_1_setup="Sam discovers the device in the vault.",
            act_2_escalation="Security guards isolate the lab.",
            act_3_climax_resolution="Sam activates the chronometer and escapes.",
            thematic_arc="Time is a resource to be mastered.",
        ),
        scene_breakdown=[
            SceneBreakdownItem(
                scene_number=1,
                heading="INT. VAULT - NIGHT",
                location="Lab Vault",
                time_of_day="NIGHT",
                characters_present=["Sam Taylor"],
                action_summary="Sam unlocks the chronometer case.",
                props_used=["Silver Chronometer"],
            )
        ],
        dialogue_snippets=[
            DialogueSnippetItem(
                character="Sam Taylor",
                line="We are out of time.",
                is_required_line=True,
                context_notes="Whispered in total darkness.",
            )
        ],
        compliance_checklist=FestivalComplianceChecklist(
            verbatim_line_verified=True,
            prop_usage_verified=True,
            character_linkage_verified=True,
            pacing_runtime_verified=True,
            compliance_notes="All 48HFP constraints verified.",
        ),
    )


@pytest.mark.anyio
async def test_workspace_rendering(sample_profile, sample_draw):
    """Verify rendering of StudioWorkspace, RecipePane, and OutputPane with profile/draw reactives."""
    with patch("studio.tui.load_profile", return_value=sample_profile), patch(
        "studio.tui.load_draw", return_value=sample_draw
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            workspace = app.query_one(StudioWorkspace)
            recipe_pane = workspace.query_one(RecipePane)
            output_pane = workspace.query_one(OutputPane)

            assert workspace.profile == sample_profile
            assert workspace.draw == sample_draw
            assert recipe_pane.profile == sample_profile
            assert recipe_pane.draw == sample_draw

            # Check markdown widget initialized with welcome text
            md_widget = output_pane.query_one("#treatment-markdown", Markdown)
            assert md_widget is not None
            assert md_widget.display is True

            # Check loading indicator is hidden initially
            loader = output_pane.query_one("#treatment-loading", LoadingIndicator)
            assert loader.display is False


@pytest.mark.anyio
async def test_action_generate_treatment_success(sample_profile, sample_draw, sample_treatment, tmp_path):
    """Verify background worker executes inference, saves treatment file, and updates markdown reactive state."""
    saved_file = tmp_path / "treatment_v01.md"

    with patch("studio.tui.load_profile", return_value=sample_profile), patch(
        "studio.tui.load_draw", return_value=sample_draw
    ), patch(
        "studio.tui.InferenceEngine.generate_treatment", return_value=sample_treatment
    ) as mock_inference, patch(
        "studio.tui.save_treatment_output", return_value=saved_file
    ) as mock_save:
        app = StudioApp()
        async with app.run_test() as pilot:
            # Trigger generation action
            app.action_generate_treatment()

            # Pause pilot to allow worker thread to complete and push main thread callback
            await pilot.pause()

            mock_inference.assert_called_once()
            mock_save.assert_called_once()

            # Verify reactive state updated with markdown content
            assert app.is_generating is False
            assert "CHRONO SHIFT" in app.current_markdown
            assert str(saved_file) in app.current_markdown


@pytest.mark.anyio
async def test_action_generate_treatment_inference_error(sample_profile, sample_draw):
    """Verify InferenceError in worker thread surfaces error markdown and notification without crashing app."""
    with patch("studio.tui.load_profile", return_value=sample_profile), patch(
        "studio.tui.load_draw", return_value=sample_draw
    ), patch(
        "studio.tui.InferenceEngine.generate_treatment",
        side_effect=InferenceError("Missing GEMINI_API_KEY environment variable."),
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            app.action_generate_treatment()
            await pilot.pause()

            assert app.is_generating is False
            assert "Generation Failed" in app.current_markdown
            assert "Missing GEMINI_API_KEY" in app.current_markdown


@pytest.mark.anyio
async def test_generate_button_event_trigger(sample_profile, sample_draw, sample_treatment, tmp_path):
    """Verify clicking #btn_generate_treatment triggers action_generate_treatment worker."""
    saved_file = tmp_path / "treatment_v01.md"

    with patch("studio.tui.load_profile", return_value=sample_profile), patch(
        "studio.tui.load_draw", return_value=sample_draw
    ), patch(
        "studio.tui.InferenceEngine.generate_treatment", return_value=sample_treatment
    ), patch("studio.tui.save_treatment_output", return_value=saved_file):
        app = StudioApp()
        async with app.run_test() as pilot:
            # Click generate treatment button in RecipePane
            await pilot.click("#btn_generate_treatment")
            await pilot.pause()

            assert app.is_generating is False
            assert "CHRONO SHIFT" in app.current_markdown
