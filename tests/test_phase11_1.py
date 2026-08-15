"""Tests for Phase 11, Sprint 11.1: StudioBinder Shot Lists."""

from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from studio.models.draw import create_default_draw
from studio.models.profile import TeamProfile
from studio.models.shotlist import ShotItem, ShotListBase
from studio.utils.asset_store import (
    get_next_shotlist_version_number,
    list_saved_shotlists,
    load_shotlist_csv,
    save_shotlist_csv,
)
from studio.utils.prompt_builder import PromptBuilder


def test_shotlist_models():
    """Test Pydantic schema validation for ShotItem and ShotListBase."""
    shot1 = ShotItem(
        shot_number=1,
        scene_number="INT. CLOCK SHOP - NIGHT",
        location="Clock Shop Interior",
        setup="Setup A - Main Counter",
        shot_size="MCU",
        camera_movement="Static",
        cast=["Arthur", "Elena"],
        description="Arthur inspects the ancient grandfather clock.",
    )

    shot2 = ShotItem(
        shot_number=2,
        scene_number="1",
        location="Clock Shop Interior",
        setup="Setup B - Close-up on Dial",
        shot_size="ECU",
        camera_movement="Dolly In",
        cast=["Arthur"],
        description="Extreme close-up of the clock hands moving backwards.",
    )

    shotlist = ShotListBase(title="The Midnight Pendulum", shots=[shot1, shot2])

    assert shotlist.title == "The Midnight Pendulum"
    assert len(shotlist.shots) == 2
    assert shotlist.shots[0].shot_number == 1
    assert shotlist.shots[1].shot_size == "ECU"
    assert "Elena" in shotlist.shots[0].cast


def test_asset_store_csv_export_import():
    """Test saving ShotListBase to CSV via pandas and reading it back."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        assets_dir = tmp_path / "assets"

        # Verify assets_dir does not exist initially
        assert not assets_dir.exists()

        shot1 = ShotItem(
            shot_number=1,
            scene_number="INT. CLOCK SHOP - NIGHT",
            location="Clock Shop",
            setup="Setup A",
            shot_size="WS",
            camera_movement="Pan Right",
            cast=["Arthur"],
            description="Wide shot of the dusty shop.",
        )
        shotlist = ShotListBase(title="Clockwork", shots=[shot1])

        # Test version numbering on missing dir
        ver1 = get_next_shotlist_version_number(assets_dir)
        assert ver1 == 1

        # Test save (must auto-create assets_dir)
        saved_file = save_shotlist_csv(shotlist, title="Clockwork", assets_dir=assets_dir)
        assert saved_file.exists()
        assert assets_dir.exists()
        assert "shotlist_v01_Clockwork_" in saved_file.name

        # Test next version
        ver2 = get_next_shotlist_version_number(assets_dir)
        assert ver2 == 2

        # Test list_saved_shotlists
        saved_items = list_saved_shotlists(assets_dir=assets_dir)
        assert len(saved_items) == 1
        assert saved_items[0]["version"] == "v01"
        assert saved_items[0]["title"] == "Clockwork"

        # Test load_shotlist_csv
        loaded_rows = load_shotlist_csv(saved_file)
        assert len(loaded_rows) == 1
        assert loaded_rows[0]["Shot"] == "1"
        assert loaded_rows[0]["Scene"] == "INT. CLOCK SHOP - NIGHT"
        assert loaded_rows[0]["Location"] == "Clock Shop"
        assert loaded_rows[0]["Shot Size"] == "WS"
        assert loaded_rows[0]["Camera Movement"] == "Pan Right"
        assert loaded_rows[0]["Cast"] == "Arthur"
        assert loaded_rows[0]["Description"] == "Wide shot of the dusty shop."


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_prompt_builder_compile_shotlist_prompt():
    """Test compile_shotlist_prompt outputs complete StudioBinder directives."""
    fountain_script = "INT. CLOCK SHOP - NIGHT\n\nARTHUR inspects the pendulum."
    profile = TeamProfile(
        admin_username="test_admin",
        team_name="Clockwork Cinema",
        location="Portland",
    )
    draw = create_default_draw()

    prompt = PromptBuilder.compile_shotlist_prompt(
        screenplay_text=fountain_script,
        profile=profile,
        draw=draw,
    )

    assert "STUDIOBINDER SHOT LIST BREAKDOWN DIRECTIVE" in prompt
    assert "SOURCE SCREENPLAY (.FOUNTAIN)" in prompt
    assert "ARTHUR inspects the pendulum." in prompt
    assert "shot_number" in prompt
    assert "camera_movement" in prompt
    assert "Clockwork Cinema" in prompt


@patch("studio.inference.genai.Client")
def test_generate_shotlist_inference(mock_genai_client):
    """Test InferenceEngine.generate_shotlist returns structured ShotListBase."""
    from studio.inference import InferenceEngine

    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance

    expected_shotlist = ShotListBase(
        title="Test Film",
        shots=[
            ShotItem(
                shot_number=1,
                scene_number="1",
                location="Studio",
                setup="A",
                shot_size="CU",
                camera_movement="Static",
                cast=["Hero"],
                description="Close up on hero.",
            )
        ],
    )

    mock_response = MagicMock()
    mock_response.parsed = expected_shotlist
    mock_client_instance.models.generate_content.return_value = mock_response

    result = InferenceEngine.generate_shotlist(
        prompt="Test Prompt", api_key="fake-key-123"
    )

    assert isinstance(result, ShotListBase)
    assert result.title == "Test Film"
    assert len(result.shots) == 1
    assert result.shots[0].shot_size == "CU"


@pytest.mark.anyio
async def test_tui_shotlist_workspace():
    """Test ShotListWorkspace widget rendering and view integration in Textual TUI."""
    from studio.screens_shotlist import ShotListWorkspace
    from studio.tui import StudioApp

    app = StudioApp()
    async with app.run_test() as pilot:
        shot1 = ShotItem(
            shot_number=1,
            scene_number="SCENE 1",
            location="Warehouse",
            setup="Setup A",
            shot_size="MS",
            camera_movement="Dolly",
            cast=["Detective"],
            description="Medium shot of detective.",
        )
        test_shotlist = ShotListBase(title="Noir City", shots=[shot1])

        # Set shotlist data and switch view
        app.current_shotlist_data = test_shotlist
        app.action_switch_to_shotlist_view()
        await pilot.pause()

        assert app.active_view == "shotlist"
        sl_workspace = app.query_one("#shotlist-workspace", ShotListWorkspace)
        assert sl_workspace.display is True

        # Click Back to Screenplay button
        await pilot.click("#btn_back_to_screenplay")
        await pilot.pause()

        assert app.active_view == "screenplay"

