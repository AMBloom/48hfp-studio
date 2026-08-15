"""Unit tests for Phase 4 (Inference Engine, Output Versioning, and CLI Integration)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from typer.testing import CliRunner

from studio.cli import app
from studio.inference import InferenceEngine, InferenceError
from studio.models.treatment import (
    CharacterRosterItem,
    DialogueSnippetItem,
    FestivalComplianceChecklist,
    NarrativeSynopsis,
    SceneBreakdownItem,
    TitleAndLogline,
    TreatmentOutput,
)
from studio.utils.treatment_store import (
    convert_treatment_to_markdown,
    get_next_version_number,
    sanitize_filename_part,
    save_treatment_output,
)

runner = CliRunner()


def create_sample_treatment() -> TreatmentOutput:
    """Helper fixture to create a valid TreatmentOutput instance."""
    return TreatmentOutput(
        title_and_logline=TitleAndLogline(
            title="The Midnight Ticking",
            genre_blend="Film Noir / Single Room Movie",
            logline="A weary clockmaker must decode a hidden sequence in an antique watch before midnight.",
        ),
        character_roster=[
            CharacterRosterItem(
                name="Alex Vance",
                actor_or_traits="Clockmaker / Obsessive",
                role="Protagonist",
                is_required_character=True,
            )
        ],
        synopsis=NarrativeSynopsis(
            act_1_setup="Alex receives a mysterious watch.",
            act_2_escalation="The watch begins ticking backwards.",
            act_3_climax_resolution="Alex discovers the hidden truth.",
            thematic_arc="Obsession leads to revelation.",
        ),
        scene_breakdown=[
            SceneBreakdownItem(
                scene_number=1,
                heading="INT. CLOCK SHOP - NIGHT",
                location="Clock Shop",
                time_of_day="NIGHT",
                characters_present=["Alex Vance"],
                action_summary="Alex examines the watch under a warm lamp.",
                props_used=["An antique brass pocket watch"],
            )
        ],
        dialogue_snippets=[
            DialogueSnippetItem(
                character="Alex Vance",
                line="We only have five minutes left.",
                is_required_line=True,
                context_notes="Spoken with urgency as the clock approaches midnight.",
            )
        ],
        compliance_checklist=FestivalComplianceChecklist(
            verbatim_line_verified=True,
            prop_usage_verified=True,
            character_linkage_verified=True,
            pacing_runtime_verified=True,
            compliance_notes="All 48HFP requirements fully satisfied.",
        ),
    )


def test_sanitize_filename_part():
    """Verify string sanitization for safe filename usage."""
    assert sanitize_filename_part("Warehouse Studio / Lot B") == "Warehouse_Studio_Lot_B"
    assert sanitize_filename_part("  Complex #1 @ Night!  ") == "Complex_1_Night"
    assert sanitize_filename_part("") == "Unconstrained"


def test_empty_directory_fallback_and_version_increment(tmp_path: Path):
    """Verify Guardrail 3 (Empty directory fallback) and version increment logic."""
    empty_dir = tmp_path / "outputs"

    # Non-existent directory should return 1
    assert get_next_version_number(empty_dir) == 1

    empty_dir.mkdir()
    # Empty directory should safely fallback to 1 (no ValueError)
    assert get_next_version_number(empty_dir) == 1

    # Create dummy treatment files
    (empty_dir / "treatment_v01_Default_Default_20260803_120000.md").write_text("v1")
    assert get_next_version_number(empty_dir) == 2

    (empty_dir / "treatment_v02_Default_Default_20260803_130000.md").write_text("v2")
    assert get_next_version_number(empty_dir) == 3


def test_save_treatment_output_zero_padding_and_safe_write(tmp_path: Path):
    """Verify Guardrails 1, 2, and Safe-Write non-overwriting behavior."""
    treatment = create_sample_treatment()

    # Guardrail 2: Version zero-padding (v01)
    file_path_1 = save_treatment_output(treatment, outputs_dir=tmp_path)
    assert file_path_1.exists()
    assert "treatment_v01_" in file_path_1.name
    content_1 = file_path_1.read_text(encoding="utf-8")
    assert "THE MIDNIGHT TICKING" in content_1
    assert "We only have five minutes left." in content_1

    # Second save should automatically increment to v02 without overwriting v01
    file_path_2 = save_treatment_output(treatment, outputs_dir=tmp_path)
    assert file_path_2.exists()
    assert "treatment_v02_" in file_path_2.name
    assert file_path_1.exists()  # Ensure v01 was NOT overwritten


def test_convert_treatment_to_markdown():
    """Verify Pydantic model conversion to 6-section Markdown layout."""
    treatment = create_sample_treatment()
    md = convert_treatment_to_markdown(treatment)

    assert "# THE MIDNIGHT TICKING" in md
    assert "## 1. FILM TITLE & LOGLINE" in md
    assert "## 2. CHARACTER ROSTER & CASTING" in md
    assert "## 3. NARRATIVE SYNOPSIS & THEMATIC ARC" in md
    assert "## 4. SCENE-BY-SCENE BREAKDOWN" in md
    assert "## 5. SAMPLE DIALOGUE SNIPPETS" in md
    assert "## 6. FESTIVAL COMPLIANCE CHECKLIST" in md
    assert "[x] **Verbatim Line Verified:** True" in md


def test_inference_engine_missing_api_key():
    """Verify error raised when GEMINI_API_KEY is unconfigured."""
    with patch.dict(os.environ, {}, clear=True):
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

        with pytest.raises(InferenceError, match="Missing GEMINI_API_KEY"):
            InferenceEngine.generate_treatment("Test Prompt")


def test_inference_engine_successful_generation():
    """Verify InferenceEngine with mocked Gemini client response."""
    sample_treatment = create_sample_treatment()

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = sample_treatment
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key"}):
        with patch("google.genai.Client", return_value=mock_client):
            result = InferenceEngine.generate_treatment("Test System Prompt")
            assert result.title_and_logline.title == "The Midnight Ticking"


def test_inference_engine_model_resolution():
    """Verify default model gemini-3.6-flash, GEMINI_MODEL env var, and explicit parameter override."""
    sample_treatment = create_sample_treatment()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = sample_treatment
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key"}, clear=True):
        with patch("google.genai.Client", return_value=mock_client):
            # 1. Default model resolution
            InferenceEngine.generate_treatment("Test Prompt")
            assert mock_client.models.generate_content.call_args.kwargs["model"] == "gemini-3.7-flash"

    # 2. Environment variable fallback
    with patch.dict(
        os.environ,
        {"GEMINI_API_KEY": "fake_test_key", "GEMINI_MODEL": "gemini-3.6-pro-env"},
        clear=True,
    ):
        with patch("google.genai.Client", return_value=mock_client):
            InferenceEngine.generate_treatment("Test Prompt")
            assert mock_client.models.generate_content.call_args.kwargs["model"] == "gemini-3.6-pro-env"

    # 3. Explicit parameter override (CLI --model precedence over GEMINI_MODEL env)
    with patch.dict(
        os.environ,
        {"GEMINI_API_KEY": "fake_test_key", "GEMINI_MODEL": "gemini-3.6-pro-env"},
        clear=True,
    ):
        with patch("google.genai.Client", return_value=mock_client):
            InferenceEngine.generate_treatment("Test Prompt", model_name="gemini-3.6-ultra-cli")
            assert mock_client.models.generate_content.call_args.kwargs["model"] == "gemini-3.6-ultra-cli"


def test_cli_generate_dry_run():
    """Verify 48hfp generate --dry-run CLI command."""
    result = runner.invoke(app, ["generate", "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN MODE ACTIVE" in result.output
    assert "IMMUTABLE FESTIVAL RULES" in result.output


def test_cli_generate_missing_api_key():
    """Verify 48hfp generate exits gracefully on missing API key."""
    with patch.dict(os.environ, {}, clear=True):
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 1
        assert "Missing GEMINI_API_KEY" in result.output
