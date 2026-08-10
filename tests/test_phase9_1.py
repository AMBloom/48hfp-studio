"""Unit and integration tests for Phase 9, Sprint 9.1: Treatment Revision Engine."""

from pathlib import Path
from unittest.mock import patch
import pytest
from textual.widgets import Button, TextArea

from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.models.treatment import (
    FestivalComplianceChecklist,
    NarrativeSynopsis,
    TitleAndLogline,
    TreatmentOutput,
)
from studio.tui import StudioApp
from studio.utils.global_state import clear_active_workspace, set_active_workspace
from studio.utils.prompt_builder import PromptBuilder
from studio.workspace import OutputPane, RevisionPane


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


@pytest.fixture
def dummy_treatment():
    return TreatmentOutput(
        title_and_logline=TitleAndLogline(
            title="Night Call",
            genre_blend="Film Noir / Mystery",
            logline="A detective takes a late-night phone call that changes everything.",
        ),
        synopsis=NarrativeSynopsis(
            act_1_setup="Act 1 setup",
            act_2_escalation="Act 2 escalation",
            act_3_climax_resolution="Act 3 resolution",
            thematic_arc="Truth vs Illusion",
        ),
        character_roster=[],
        scene_breakdown=[],
        dialogue_snippets=[],
        compliance_checklist=FestivalComplianceChecklist(
            verbatim_line_verified=True,
            prop_usage_verified=True,
            character_linkage_verified=True,
            pacing_runtime_verified=True,
            compliance_notes="Fully compliant",
        ),
    )


def test_compile_revision_prompt_recency_effect_and_token_conservation(dummy_treatment) -> None:
    """Verify that compile_revision_prompt places Immutable Festival Rules at the absolute bottom

    and enforces stateless single-draft payload (stripping prior revision blocks).
    """
    draw = FridayDraw(
        genre_1="Film Noir",
        genre_2="Mystery",
        character_name="Sam",
        character_trait="Detective",
        required_prop="Rotary Phone",
        required_line="The clock is ticking.",
    )
    original_prompt = PromptBuilder.compile_system_prompt(draw=draw)

    # 1. Verify Immutable Rules are at the absolute bottom of the original prompt
    rules_marker = "8. IMMUTABLE FESTIVAL RULES"
    assert rules_marker in original_prompt

    # Compile revision prompt
    notes = "Make the ending darker and set scene 2 at the docks."
    rev_prompt = PromptBuilder.compile_revision_prompt(
        current_treatment=dummy_treatment,
        notes=notes,
        original_prompt=original_prompt,
        draw=draw,
    )

    # 2. Verify structure order: Previous Draft JSON -> Revision Notes -> Immutable Rules
    json_marker = "Below is the SINGLE MOST RECENT DRAFT"
    notes_marker = "FILMMAKER REVISION NOTES / CHANGE REQUESTS:"

    pos_json = rev_prompt.find(json_marker)
    pos_notes = rev_prompt.find(notes_marker)
    pos_rules = rev_prompt.find(rules_marker)

    assert pos_json != -1, "Draft JSON section missing"
    assert pos_notes != -1, "Revision notes missing"
    assert pos_rules != -1, "Immutable rules section missing"

    assert pos_json < pos_notes < pos_rules, (
        "Prompt hierarchy order violated! Expected JSON -> Notes -> Immutable Rules (at bottom)"
    )

    # Verify Immutable Festival Rules remain anchored at the absolute bottom
    assert rev_prompt.strip().endswith("================================================================================")
    assert any(rules_marker in line for line in rev_prompt.splitlines()[-25:])

    # 3. Verify Stateless Token Conservation: Re-revising strips prior revision blocks
    notes_2 = "Add a plot twist at the midpoint."
    rev_prompt_2 = PromptBuilder.compile_revision_prompt(
        current_treatment=dummy_treatment,
        notes=notes_2,
        original_prompt=rev_prompt,  # Pass the ALREADY REVISED prompt
        draw=draw,
    )

    # Count occurrences of draft header - MUST be exactly 1
    assert rev_prompt_2.count(json_marker) == 1, (
        "Token conservation failed: multiple revision draft blocks accumulated!"
    )
    assert notes in rev_prompt  # First prompt had notes 1
    assert notes not in rev_prompt_2  # Second prompt replaced notes 1 with notes 2
    assert notes_2 in rev_prompt_2


@pytest.mark.anyio
async def test_revision_pane_visibility_toggling(dummy_treatment) -> None:
    """Verify that RevisionPane is hidden when current_treatment_obj is None and visible when populated."""
    app = StudioApp()
    async with app.run_test(size=(120, 40)) as pilot:
        output_pane = app.query_one(OutputPane)
        rev_pane = app.query_one(RevisionPane)

        # Initially no treatment generated -> RevisionPane must be hidden
        assert app.current_treatment_obj is None
        await pilot.pause()
        assert rev_pane.display is False

        # Populate current_treatment_obj -> RevisionPane must become visible
        app.current_treatment_obj = dummy_treatment
        await pilot.pause()
        assert rev_pane.display is True


@pytest.mark.anyio
async def test_action_revise_treatment_flow(tmp_path: Path, dummy_treatment) -> None:
    """Verify full action_revise_treatment execution, version incrementing (v01 -> v02), and TUI updates."""
    ws_dir = tmp_path / "revision_film_project"
    ws_dir.mkdir()
    set_active_workspace(ws_dir)

    app = StudioApp()
    async with app.run_test(size=(120, 40)) as pilot:
        # Set initial treatment v01
        app.current_treatment_obj = dummy_treatment
        app.current_prompt_text = "Original System Prompt"
        await pilot.pause()

        rev_pane = app.query_one(RevisionPane)
        notes_input = rev_pane.query_one("#revision_notes_input", TextArea)
        notes_input.text = "Make the ending darker."

        # Create revised treatment mock return
        revised_treatment = dummy_treatment.model_copy(deep=True)
        revised_treatment.title_and_logline.title = "Night Call Dark Edition"

        with patch("studio.inference.InferenceEngine.generate_treatment", return_value=revised_treatment):
            # Click submit revision
            btn_submit = rev_pane.query_one("#btn_submit_revision", Button)
            btn_submit.press()
            await pilot.pause()

            # Verify updated state
            assert app.current_treatment_obj.title_and_logline.title == "Night Call Dark Edition"
            assert notes_input.text == ""  # Input cleared after submission

            # Verify saved version output file created in workspace outputs/
            outputs_dir = ws_dir / "outputs"
            assert outputs_dir.exists()
            output_files = list(outputs_dir.glob("treatment_v*.md"))
            assert len(output_files) == 1
            assert "treatment_v01_" in output_files[0].name
            assert "Night_Call_Dark_Edition" in output_files[0].name
