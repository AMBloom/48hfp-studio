"""Unit and integration tests for Phase 10 (Sprints 10.1 & 10.2): The Screenplay Engine."""

from pathlib import Path
from unittest.mock import patch
import pytest
from textual.widgets import Button

from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.models.treatment import (
    FestivalComplianceChecklist,
    NarrativeSynopsis,
    TitleAndLogline,
    TreatmentOutput,
)
from studio.screens_load import LoadDraftsScreen
from studio.screens_screenplay import ScreenplayWorkspace, highlight_fountain_lines
from studio.tui import StudioApp
from studio.utils.global_state import clear_active_workspace, set_active_workspace
from studio.utils.prompt_builder import PromptBuilder
from studio.utils.screenplay_store import (
    clean_fountain_text,
    get_next_screenplay_version_number,
    list_saved_screenplays,
    list_saved_treatments,
    save_screenplay_output,
)


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
            title="The Clockmaker",
            genre_blend="Sci-Fi / Drama",
            logline="A clockmaker discovers a device that alters time.",
        ),
        synopsis=NarrativeSynopsis(
            act_1_setup="Setup act 1",
            act_2_escalation="Escalation act 2",
            act_3_climax_resolution="Climax act 3",
            thematic_arc="Time and Regret",
        ),
        character_roster=[],
        scene_breakdown=[],
        dialogue_snippets=[],
        compliance_checklist=FestivalComplianceChecklist(
            verbatim_line_verified=True,
            prop_usage_verified=True,
            character_linkage_verified=True,
            pacing_runtime_verified=True,
            compliance_notes="Compliant",
        ),
    )


SAMPLE_FOUNTAIN_SCRIPT = """INT. CLOCK SHOP - NIGHT

An ancient pendulum swings with a heavy TICK-TOCK.

ARTHUR (60s) polishes a brass gear with a velvet cloth.

ARTHUR
(whispering)
The gears never lie.

CUT TO:

EXT. DOCKS - DAY

Rain pours over the empty wooden pier.
"""


def test_clean_fountain_text() -> None:
    """Verify clean_fountain_text strips accidental markdown code fence wrappers."""
    raw_1 = "```fountain\nINT. SHOP - DAY\n```"
    assert clean_fountain_text(raw_1) == "INT. SHOP - DAY"

    raw_2 = "```\nEXT. DOCKS - NIGHT\nLine 2\n```"
    assert clean_fountain_text(raw_2) == "EXT. DOCKS - NIGHT\nLine 2"

    raw_3 = "INT. STREET - DAY"
    assert clean_fountain_text(raw_3) == "INT. STREET - DAY"


def test_compile_screenplay_prompt(dummy_treatment) -> None:
    """Verify compile_screenplay_prompt includes Fountain directives, treatment JSON, and rules at bottom."""
    draw = FridayDraw(
        genre_1="Sci-Fi",
        genre_2="Drama",
        character_name="Arthur Pendelton",
        character_trait="Clockmaker",
        required_prop="Pocket Watch",
        required_line="Time is on our side.",
    )
    prompt = PromptBuilder.compile_screenplay_prompt(
        treatment=dummy_treatment,
        draw=draw,
    )

    assert "SCREENPLAY GENERATION DIRECTIVE (.FOUNTAIN FORMAT)" in prompt
    assert "The Clockmaker" in prompt
    assert "FOUNTAIN FORMATTING DIRECTIVES & STRICT OUTPUT RULES" in prompt
    assert "8. IMMUTABLE FESTIVAL RULES" in prompt
    # Recency effect check: rules section at bottom
    assert prompt.strip().endswith("================================================================================")


def test_screenplay_store_save_and_list(tmp_path: Path) -> None:
    """Verify screenplay saving to screenplays/script_vXX_... and metadata listing."""
    ws_dir = tmp_path / "test_screenplay_ws"
    ws_dir.mkdir()
    set_active_workspace(ws_dir)

    sp_dir = ws_dir / "screenplays"
    assert get_next_screenplay_version_number(sp_dir) == 1

    saved_path_1 = save_screenplay_output(SAMPLE_FOUNTAIN_SCRIPT, title="The Clockmaker", screenplays_dir=sp_dir)
    assert saved_path_1.exists()
    assert "script_v01_The_Clockmaker_" in saved_path_1.name
    assert saved_path_1.suffix == ".fountain"

    assert get_next_screenplay_version_number(sp_dir) == 2

    saved_path_2 = save_screenplay_output(SAMPLE_FOUNTAIN_SCRIPT, title="The Clockmaker", screenplays_dir=sp_dir)
    assert "script_v02_The_Clockmaker_" in saved_path_2.name

    scripts = list_saved_screenplays(sp_dir)
    assert len(scripts) == 2
    assert scripts[0]["version"] in ["v01", "v02"]
    assert scripts[0]["title"] == "The Clockmaker"


def test_fountain_line_highlighting() -> None:
    """Verify highlight_fountain_lines applies styles for scene headings, characters, parentheticals."""
    lines = [
        "INT. CLOCK SHOP - NIGHT",
        "ARTHUR",
        "(whispering)",
        "The gears never lie.",
        "CUT TO:",
    ]
    styled_text = highlight_fountain_lines(lines)

    # Convert to string / spans check
    plain = styled_text.plain
    assert "INT. CLOCK SHOP - NIGHT" in plain
    assert "ARTHUR" in plain
    assert "(whispering)" in plain
    assert "CUT TO:" in plain


@pytest.mark.anyio
async def test_screenplay_workspace_pagination_and_back_button() -> None:
    """Verify ScreenplayWorkspace 50-line pagination and [← Back to Treatment] button behavior."""
    # Generate 120 lines
    lines = [f"Line {i}" for i in range(1, 121)]
    fountain_text = "\n".join(lines)

    app = StudioApp()
    async with app.run_test(size=(120, 40)) as pilot:
        sp_ws = app.query_one("#screenplay-workspace", ScreenplayWorkspace)
        sp_ws.fountain_text = fountain_text
        await pilot.pause()

        assert sp_ws.total_pages == 3  # 120 lines / 50 = 2.4 -> 3 pages
        assert sp_ws.current_page == 1

        # Test Page Down button
        btn_down = sp_ws.query_one("#btn_page_down", Button)
        btn_down.press()
        await pilot.pause()
        assert sp_ws.current_page == 2

        btn_down.press()
        await pilot.pause()
        assert sp_ws.current_page == 3
        assert btn_down.disabled is True

        # Test Page Up button
        btn_up = sp_ws.query_one("#btn_page_up", Button)
        btn_up.press()
        await pilot.pause()
        assert sp_ws.current_page == 2

        # Switch to screenplay view first
        app.action_switch_to_screenplay_view()
        await pilot.pause()
        assert app.active_view == "screenplay"

        # Press [← Back to Treatment]
        btn_back = sp_ws.query_one("#btn_back_to_treatment", Button)
        btn_back.press()
        await pilot.pause()
        assert app.active_view == "treatment"


@pytest.mark.anyio
async def test_action_generate_screenplay_flow(tmp_path: Path, dummy_treatment) -> None:
    """Verify action_generate_screenplay flow, worker execution, file saving, and view switching."""
    ws_dir = tmp_path / "screenplay_gen_ws"
    ws_dir.mkdir()
    set_active_workspace(ws_dir)

    app = StudioApp()
    async with app.run_test(size=(120, 40)) as pilot:
        app.current_treatment_obj = dummy_treatment
        await pilot.pause()

        mock_fountain_response = SAMPLE_FOUNTAIN_SCRIPT

        with patch("studio.inference.InferenceEngine.generate_screenplay", return_value=mock_fountain_response):
            # Click Generate Screenplay button
            btn_gen_sp = app.query_one("#btn_generate_screenplay", Button)
            btn_gen_sp.press()
            await pilot.pause()

            # Verify view switched to screenplay view
            assert app.active_view == "screenplay"
            assert app.current_screenplay_text == SAMPLE_FOUNTAIN_SCRIPT

            # Verify saved .fountain file in screenplays/
            sp_dir = ws_dir / "screenplays"
            assert sp_dir.exists()
            fountain_files = list(sp_dir.glob("script_v*.fountain"))
            assert len(fountain_files) == 1
            assert "script_v01_The_Clockmaker_" in fountain_files[0].name
            assert "INT. CLOCK SHOP - NIGHT" in fountain_files[0].read_text(encoding="utf-8")


@pytest.mark.anyio
async def test_load_drafts_modal_flow(tmp_path: Path) -> None:
    """Verify LoadDraftsScreen listing, draft selection, and loading into app views."""
    ws_dir = tmp_path / "load_drafts_ws"
    ws_dir.mkdir()
    set_active_workspace(ws_dir)

    # Save a treatment and a screenplay
    outputs_dir = ws_dir / "outputs"
    outputs_dir.mkdir()
    treatment_file = outputs_dir / "treatment_v01_Test_Treatment_20260812_120000.md"
    treatment_file.write_text("# TEST TREATMENT\nLogline: A test logline.", encoding="utf-8")

    screenplays_dir = ws_dir / "screenplays"
    screenplays_dir.mkdir()
    screenplay_file = screenplays_dir / "script_v01_Test_Screenplay_20260812_120000.fountain"
    screenplay_file.write_text("INT. TEST SCENE - DAY\n\nJOHN\nHello.", encoding="utf-8")

    app = StudioApp()
    async with app.run_test(size=(120, 40)) as pilot:
        app.action_open_load_drafts()
        await pilot.pause()

        assert isinstance(app.screen, LoadDraftsScreen)

        # Simulate callback loading treatment draft
        result_treatment = {
            "type": "treatment",
            "path": str(treatment_file),
            "content": treatment_file.read_text(),
            "title": "treatment_v01_Test_Treatment",
        }
        app.on_load_draft_selected(result_treatment)
        await pilot.pause()

        assert app.active_view == "treatment"
        assert "# TEST TREATMENT" in app.current_markdown

        # Simulate callback loading screenplay draft
        result_screenplay = {
            "type": "screenplay",
            "path": str(screenplay_file),
            "content": screenplay_file.read_text(),
            "title": "script_v01_Test_Screenplay",
        }
        app.on_load_draft_selected(result_screenplay)
        await pilot.pause()

        assert app.active_view == "screenplay"
        assert "INT. TEST SCENE - DAY" in app.current_screenplay_text
