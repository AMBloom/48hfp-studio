"""Unit tests for Phase 11 Sprint 11.2 - Engine Upgrade & Pre-Vis Storyboarding."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from studio.inference import InferenceEngine, InferenceError
from studio.models.constraints import DirectorialVision
from studio.models.shotlist import ShotItem
from studio.screens import ApiSettingsScreen
from studio.screens_shotlist import ShotListWorkspace
from studio.utils.asset_store import save_storyboard_image
from studio.utils.prompt_builder import PromptBuilder


def test_default_model_upgrade():
    """Verify DEFAULT_MODEL is gemini-3.7-flash."""
    assert InferenceEngine.DEFAULT_MODEL == "gemini-3.7-flash"


def test_api_settings_screen_choices():
    """Verify ApiSettingsScreen features gemini-3.7-flash as default choice."""
    choice_keys = [choice[1] for choice in ApiSettingsScreen.MODEL_CHOICES]
    assert "gemini-3.7-flash" in choice_keys
    assert ApiSettingsScreen.MODEL_CHOICES[0][1] == "gemini-3.7-flash"


def test_compile_storyboard_prompt():
    """Verify compile_storyboard_prompt formats 16:9 monochrome constraints and shot details correctly."""
    shot = ShotItem(
        shot_number=1,
        scene_number="1A",
        location="INT. DINER - NIGHT",
        setup="Setup 1 - Counter High Angle",
        shot_size="MCU",
        camera_movement="Pan Right",
        cast=["ALEX", "MAYA"],
        description="Alex passes the envelope to Maya across the greasy counter.",
    )
    vision = DirectorialVision(
        name="neo_noir_high_contrast",
        description="Neo-Noir High Contrast",
        lighting_color="Chiaroscuro high-contrast shadows with harsh practical overhead tungsten key lights.",
    )

    prompt = PromptBuilder.compile_storyboard_prompt(shot, directorial_vision=vision)

    assert "STORYBOARD PRE-VIS SKETCH DIRECTIVE" in prompt
    assert "Aspect Ratio: 16:9 widescreen cinematic composition." in prompt
    assert "Monochrome, black and white grayscale pencil storyboard sketch." in prompt
    assert "STRICT NEGATIVE CONSTRAINTS" in prompt
    assert "Shot Number: 1" in prompt
    assert "Scene Number / Heading: 1A" in prompt
    assert "INT. DINER - NIGHT" in prompt
    assert "ALEX, MAYA" in prompt
    assert "Chiaroscuro high-contrast shadows" in prompt


def test_save_storyboard_image(tmp_path: Path):
    """Verify save_storyboard_image creates zero-padded shot files in storyboards directory."""
    dummy_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR..."
    saved_file = save_storyboard_image(
        image_bytes=dummy_bytes,
        shot_number=3,
        scene_number="12-B",
        storyboards_dir=tmp_path,
    )

    assert saved_file.exists()
    assert saved_file.name == "shot_003_scene_12-B.png"
    assert saved_file.read_bytes() == dummy_bytes



@patch("studio.inference.genai.Client")
def test_generate_storyboard_image_success(mock_client_cls):
    """Verify generate_storyboard_image calls Gemini client with 16:9 aspect ratio and returns bytes."""
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    mock_part = MagicMock()
    mock_part.inline_data.data = b"FAKE_PNG_BYTES"
    mock_cand = MagicMock()
    mock_cand.content.parts = [mock_part]
    mock_response = MagicMock()
    mock_response.candidates = [mock_cand]

    mock_client.models.generate_content.return_value = mock_response

    result_bytes = InferenceEngine.generate_storyboard_image(
        prompt="Test storyboard prompt",
        api_key="TEST_API_KEY",
    )

    assert result_bytes == b"FAKE_PNG_BYTES"
    mock_client.models.generate_content.assert_called_once()
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-3.1-flash-lite-image"
    assert call_kwargs["contents"] == "Test storyboard prompt"
    assert call_kwargs["config"].response_modalities == ["IMAGE"]
    assert call_kwargs["config"].image_config.aspect_ratio == "16:9"


@patch("studio.inference.genai.Client")
def test_generate_storyboard_image_missing_key(mock_client_cls, monkeypatch):
    """Verify generate_storyboard_image raises InferenceError when API key is missing."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(InferenceError, match="Missing GEMINI_API_KEY"):
        InferenceEngine.generate_storyboard_image(
            prompt="Test prompt",
            api_key=None,
        )


def test_shotlist_workspace_watch_is_generating_storyboards():
    """Verify ShotListWorkspace watch_is_generating_storyboards toggles button state and label."""
    workspace = ShotListWorkspace()
    mock_btn = MagicMock()

    def mock_query_one(selector, expected_type):
        if selector == "#btn_generate_storyboards":
            return mock_btn
        raise Exception("Not found")

    workspace.query_one = mock_query_one

    workspace.watch_is_generating_storyboards(True)
    assert mock_btn.disabled is True
    assert mock_btn.label == "⏳ Generating..."

    workspace.watch_is_generating_storyboards(False)
    assert mock_btn.disabled is False
    assert mock_btn.label == "🖼️ Generate Storyboards"
