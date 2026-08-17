"""Comprehensive Unit & Integration Test Suite for Sprint 12.1: Workspace Encapsulation & Output Refactor."""

from datetime import datetime
from pathlib import Path
import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input

from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.models.shotlist import ShotItem, ShotListBase
from studio.models.treatment import (
    CharacterRosterItem,
    DialogueSnippetItem,
    FestivalComplianceChecklist,
    NarrativeSynopsis,
    SceneBreakdownItem,
    TitleAndLogline,
    TreatmentOutput,
)
from studio.screens_workspace import WorkspaceManagerScreen
from studio.utils.asset_store import (
    get_next_shotlist_version_number,
    list_saved_shotlists,
    save_shotlist_csv,
    save_storyboard_image,
)
from studio.utils.global_state import get_workspace_root, set_active_workspace
from studio.utils.profile_store import save_profile
from studio.utils.prompt_builder import PromptBuilder
from studio.utils.screenplay_store import (
    get_next_screenplay_version_number,
    list_saved_screenplays,
    list_saved_treatments,
    save_screenplay_output,
)
from studio.utils.treatment_store import (
    get_next_version_number,
    save_treatment_output,
)


def create_sample_treatment(title: str = "The Last Clockmaker") -> TreatmentOutput:
    return TreatmentOutput(
        title_and_logline=TitleAndLogline(
            title=title,
            genre_blend="Sci-Fi / Film Noir",
            logline="A renegade horologist discovers a timepiece that freezes reality.",
        ),
        character_roster=[
            CharacterRosterItem(
                name="Arthur Pendelton",
                actor_or_traits="Cynical master watchmaker",
                role="Protagonist",
                is_required_character=True,
            ),
            CharacterRosterItem(
                name="Elena Cross",
                actor_or_traits="Temporal detective",
                role="Antagonist",
                is_required_character=False,
            ),
        ],
        synopsis=NarrativeSynopsis(
            act_1_setup="Arthur works in his dusty repair shop.",
            act_2_escalation="Elena storms in demanding the artifact.",
            act_3_climax_resolution="Arthur activates the clock and vanishes.",
            thematic_arc="Acceptance of inevitable time.",
        ),
        scene_breakdown=[
            SceneBreakdownItem(
                scene_number=1,
                heading="INT. CLOCK SHOP - NIGHT",
                location="Clock Shop",
                time_of_day="NIGHT",
                characters_present=["Arthur Pendelton"],
                props_used=["Antique Pocket Watch"],
                action_summary="Arthur solders a bronze gear into an ornate pocket watch.",
            )
        ],
        dialogue_snippets=[
            DialogueSnippetItem(
                character="Arthur Pendelton",
                line="Time waits for no one.",
                is_required_line=True,
                context_notes="Whispered into the shadows.",
            )
        ],
        compliance_checklist=FestivalComplianceChecklist(
            verbatim_line_verified=True,
            prop_usage_verified=True,
            character_linkage_verified=True,
            pacing_runtime_verified=True,
            compliance_notes="100% compliant with 48HFP rules.",
        ),
    )


def create_sample_shotlist(title: str = "The Last Clockmaker") -> ShotListBase:
    return ShotListBase(
        title=title,
        shots=[
            ShotItem(
                shot_number=1,
                scene_number="1",
                location="Clock Shop",
                setup="Benchtop",
                shot_size="CU",
                camera_movement="Static",
                cast=["Arthur Pendelton"],
                description="Close-up of Arthur working on the watch gear.",
            ),
            ShotItem(
                shot_number=2,
                scene_number="1",
                location="Clock Shop",
                setup="Doorway",
                shot_size="WS",
                camera_movement="Pan Right",
                cast=["Elena Cross"],
                description="Wide shot of the door kicking open in the rain.",
            ),
        ],
    )


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_encapsulated_treatment_save(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify treatments default to projects/<Clean_Title>/treatment_vXX.md and auto-increment."""
    set_active_workspace(tmp_path)
    treatment = create_sample_treatment(title="The Last Clockmaker")

    path1 = save_treatment_output(treatment)
    expected_dir = tmp_path / "projects" / "The_Last_Clockmaker"
    assert path1.parent == expected_dir
    assert path1.name == "treatment_v01.md"
    assert path1.exists()

    path2 = save_treatment_output(treatment)
    assert path2.parent == expected_dir
    assert path2.name == "treatment_v02.md"
    assert path2.exists()


def test_legacy_treatment_save_explicit_outputs_dir(tmp_path: Path) -> None:
    """Verify legacy explicit outputs_dir parameter continues to write flat timestamped filenames."""
    set_active_workspace(tmp_path)
    legacy_dir = tmp_path / "custom_outputs"
    treatment = create_sample_treatment(title="Midnight Runner")

    saved_path = save_treatment_output(treatment, outputs_dir=legacy_dir)
    assert saved_path.parent == legacy_dir
    assert saved_path.name.startswith("treatment_v01_Midnight_Runner_")
    assert saved_path.suffix == ".md"


def test_fountain_metadata_injection_and_encapsulation(tmp_path: Path) -> None:
    """Verify screenplay saving prepends Fountain metadata headers and saves to projects/<Title>/script_vXX.fountain."""
    set_active_workspace(tmp_path)
    profile = TeamProfile(team_name="Cybernetic Cinema", admin_username="neo", location="Neo Tokyo")
    save_profile(profile, tmp_path / "profile.yaml")

    raw_script = "INT. CLOCK SHOP - NIGHT\n\nArthur fixes the gears.\n\nARTHUR\nTime is ticking."
    path1 = save_screenplay_output(raw_script, title="The Last Clockmaker")

    expected_dir = tmp_path / "projects" / "The_Last_Clockmaker"
    assert path1.parent == expected_dir
    assert path1.name == "script_v01.fountain"
    assert path1.exists()

    content = path1.read_text(encoding="utf-8")
    today_str = datetime.now().strftime("%Y-%m-%d")
    assert "Title: The Last Clockmaker" in content
    assert "Author: Cybernetic Cinema" in content
    assert f"Draft date: {today_str}" in content
    assert "INT. CLOCK SHOP - NIGHT" in content

    # Second save should increment to script_v02.fountain
    path2 = save_screenplay_output(raw_script, title="The Last Clockmaker")
    assert path2.name == "script_v02.fountain"

    # Pre-existing Title header should not duplicate
    script_with_header = "Title: Custom Script\nAuthor: Jane Doe\n\nEXT. STREET - DAY"
    path3 = save_screenplay_output(script_with_header, title="The Last Clockmaker")
    content3 = path3.read_text(encoding="utf-8")
    assert content3.count("Title:") == 1


def test_legacy_screenplay_save(tmp_path: Path) -> None:
    """Verify screenplay saving with explicit screenplays_dir writes flat format."""
    set_active_workspace(tmp_path)
    legacy_dir = tmp_path / "screenplays"
    raw_script = "INT. ROOM - DAY\n\nAction."

    saved_path = save_screenplay_output(raw_script, title="Neon City", screenplays_dir=legacy_dir)
    assert saved_path.parent == legacy_dir
    assert saved_path.name.startswith("script_v01_Neon_City_")
    assert saved_path.suffix == ".fountain"


def test_compile_screenplay_prompt_negative_constraint() -> None:
    """Verify compile_screenplay_prompt includes negative prompt constraints regarding title metadata."""
    treatment = create_sample_treatment("Chrono Rift")
    prompt = PromptBuilder.compile_screenplay_prompt(treatment)

    assert "DO NOT write Title, Author, or Draft date title page metadata headers" in prompt
    assert "Begin your response directly with the first scene heading" in prompt


def test_encapsulated_shotlist_and_storyboard_save(tmp_path: Path) -> None:
    """Verify shot list CSV and storyboard images save into projects/<Clean_Title>/."""
    set_active_workspace(tmp_path)
    shotlist = create_sample_shotlist(title="The Last Clockmaker")

    # Shot list CSV
    csv_path1 = save_shotlist_csv(shotlist, title="The Last Clockmaker")
    expected_dir = tmp_path / "projects" / "The_Last_Clockmaker"
    assert csv_path1.parent == expected_dir
    assert csv_path1.name == "shotlist_v01.csv"
    assert csv_path1.exists()

    csv_path2 = save_shotlist_csv(shotlist, title="The Last Clockmaker")
    assert csv_path2.name == "shotlist_v02.csv"

    # Storyboard Image
    dummy_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    img_path = save_storyboard_image(
        image_bytes=dummy_bytes,
        shot_number=1,
        scene_number="1",
        title="The Last Clockmaker",
    )
    assert img_path.parent == expected_dir / "images"
    assert img_path.name == "shot_001_scene_1.png"
    assert img_path.exists()
    assert img_path.read_bytes() == dummy_bytes


def test_dual_discovery_listing_functions(tmp_path: Path) -> None:
    """Verify list_saved_treatments, list_saved_screenplays, and list_saved_shotlists scan both legacy and encapsulated directories."""
    set_active_workspace(tmp_path)

    # 1. Create legacy flat files
    legacy_outputs = tmp_path / "outputs"
    legacy_outputs.mkdir(parents=True, exist_ok=True)
    legacy_t = legacy_outputs / "treatment_v01_LegacyFilm_20260816_100000.md"
    legacy_t.write_text("# LEGACY TREATMENT", encoding="utf-8")

    legacy_scripts = tmp_path / "screenplays"
    legacy_scripts.mkdir(parents=True, exist_ok=True)
    legacy_s = legacy_scripts / "script_v01_Legacy_Film_20260816_100500.fountain"
    legacy_s.write_text("INT. OLD - DAY", encoding="utf-8")

    legacy_assets = tmp_path / "assets"
    legacy_assets.mkdir(parents=True, exist_ok=True)
    legacy_sl = legacy_assets / "shotlist_v01_Legacy_Film_20260816_101000.csv"
    legacy_sl.write_text("Shot,Scene,Location,Setup,Shot Size,Camera Movement,Cast,Description\n1,1,Room,A,CU,Pan,Bob,Desc", encoding="utf-8")

    # 2. Create encapsulated project files
    proj_dir = tmp_path / "projects" / "Modern_Masterpiece"
    proj_dir.mkdir(parents=True, exist_ok=True)
    enc_t = proj_dir / "treatment_v01.md"
    enc_t.write_text("# MODERN TREATMENT", encoding="utf-8")

    enc_s = proj_dir / "script_v01.fountain"
    enc_s.write_text("INT. NEW - NIGHT", encoding="utf-8")

    enc_sl = proj_dir / "shotlist_v01.csv"
    enc_sl.write_text("Shot,Scene,Location,Setup,Shot Size,Camera Movement,Cast,Description\n1,1,Studio,B,WS,Static,Alice,Look", encoding="utf-8")

    # Test Treatments Dual Discovery
    treatments = list_saved_treatments()
    t_titles = [t["title"] for t in treatments]
    assert len(treatments) == 2
    assert "Modern Masterpiece" in t_titles
    assert "LegacyFilm" in t_titles

    # Test Screenplays Dual Discovery
    screenplays = list_saved_screenplays()
    s_titles = [s["title"] for s in screenplays]
    assert len(screenplays) == 2
    assert "Modern Masterpiece" in s_titles
    assert "Legacy Film" in s_titles

    # Test Shotlists Dual Discovery
    shotlists = list_saved_shotlists()
    sl_titles = [sl["title"] for sl in shotlists]
    assert len(shotlists) == 2
    assert "Modern Masterpiece" in sl_titles
    assert "Legacy Film" in sl_titles


@pytest.mark.anyio
async def test_workspace_manager_screen_modal(tmp_path: Path) -> None:
    """Test simplified WorkspaceManagerScreen modal input and submission."""
    test_ws = tmp_path / "new_production_workspace"

    class TestApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Input(id="dummy")

    app = TestApp()
    async with app.run_test() as pilot:
        modal = WorkspaceManagerScreen()
        app.push_screen(modal)
        await pilot.pause()

        # Check input exists and simulate setting a new path
        input_widget = modal.query_one("#workspace_path_input", Input)
        input_widget.value = str(test_ws)
        await pilot.pause()

        # Trigger submission
        modal.action_submit_workspace()
        await pilot.pause()

        assert get_workspace_root() == test_ws.resolve()
        assert test_ws.exists()
        assert (test_ws / "constraints").exists()
