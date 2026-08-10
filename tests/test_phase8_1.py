"""Unit tests for Phase 8, Sprint 8.1 - Persistent Project Setup architecture."""

from pathlib import Path
import pytest
from typer.testing import CliRunner

from studio.cli import app
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.models.treatment import (
    FestivalComplianceChecklist,
    NarrativeSynopsis,
    TitleAndLogline,
    TreatmentOutput,
)
from studio.tui import HeaderHUD, NavigationSidebar
from studio.utils.constraint_store import get_constraints_base_dir, save_logistical_constraint
from studio.utils.draw_store import get_draw_path, save_draw
from studio.utils.global_state import (
    clear_active_workspace,
    get_active_workspace,
    get_global_state_path,
    get_workspace_root,
    set_active_workspace,
)
from studio.utils.profile_store import get_profile_path, save_profile
from studio.utils.treatment_store import save_treatment_output

runner = CliRunner()


@pytest.fixture(autouse=True)
def clean_global_state(tmp_path, monkeypatch):
    """Fixture ensuring a isolated global_state file and workspace for every test."""
    dummy_state_file = tmp_path / "global_state.yaml"
    monkeypatch.setattr("studio.utils.global_state.GLOBAL_STATE_FILE", dummy_state_file)
    monkeypatch.setattr("studio.utils.global_state.GLOBAL_STATE_DIR", tmp_path)
    clear_active_workspace()
    yield
    clear_active_workspace()


def test_global_state_management(tmp_path):
    """Verify set_active_workspace, get_active_workspace, clear_active_workspace, and get_workspace_root."""
    assert get_active_workspace() is None
    assert get_workspace_root() == Path.cwd()

    ws_dir = tmp_path / "test_film_project"
    ws_dir.mkdir()

    set_active_workspace(ws_dir)
    assert get_active_workspace() == ws_dir.resolve()
    assert get_workspace_root() == ws_dir.resolve()

    clear_active_workspace()
    assert get_active_workspace() is None
    assert get_workspace_root() == Path.cwd()


def test_stores_path_resolution_with_active_workspace(tmp_path):
    """Verify profile, draw, constraint, and treatment stores resolve relative to active workspace."""
    ws_dir = tmp_path / "active_short_film"
    ws_dir.mkdir()
    set_active_workspace(ws_dir)

    # Test profile store pathing
    p_path = get_profile_path()
    assert p_path == ws_dir / "profile.yaml"

    profile = TeamProfile(
        team_name="Workspace Team", admin_username="director", location="Los Angeles, CA"
    )
    saved_p = save_profile(profile)
    assert saved_p == ws_dir / "profile.yaml"
    assert saved_p.exists()

    # Test draw store pathing
    d_path = get_draw_path()
    assert d_path == ws_dir / "draw.yaml"

    draw = FridayDraw(
        genre_1="Sci-Fi",
        genre_2="Comedy",
        character_name="Alex",
        character_trait="Clumsy",
        required_prop="Laser Pointer",
        required_line="Where is the button?",
    )
    saved_d = save_draw(draw)
    assert saved_d == ws_dir / "draw.yaml"
    assert saved_d.exists()

    # Test constraint store pathing
    c_base = get_constraints_base_dir()
    assert c_base == ws_dir / "constraints"

    # Test treatment store pathing
    treatment = TreatmentOutput(
        title_and_logline=TitleAndLogline(
            title="Space Fiasco",
            genre_blend="Sci-Fi / Comedy",
            logline="A clumsy astronaut loses the ship keys.",
        ),
        synopsis=NarrativeSynopsis(
            act_1_setup="Act 1",
            act_2_escalation="Act 2",
            act_3_climax_resolution="Act 3",
            thematic_arc="Theme",
        ),
        character_roster=[],
        scene_breakdown=[],
        dialogue_snippets=[],
        compliance_checklist=FestivalComplianceChecklist(
            verbatim_line_verified=True,
            prop_usage_verified=True,
            character_linkage_verified=True,
            pacing_runtime_verified=True,
            compliance_notes="OK",
        ),
    )
    saved_t = save_treatment_output(treatment)
    assert saved_t.parent == ws_dir / "outputs"
    assert saved_t.exists()


def test_cli_workspace_commands(tmp_path):
    """Verify 48hfp workspace init, status, and switch CLI subcommands."""
    ws_path = tmp_path / "my_48hfp_project"

    # Test workspace init
    result = runner.invoke(app, ["workspace", "init", str(ws_path)])
    assert result.exit_code == 0
    assert "Initialized new project workspace" in result.output
    assert ws_path.exists()
    assert (ws_path / "constraints" / "logistical").exists()
    assert (ws_path / "outputs").exists()
    assert get_active_workspace() == ws_path.resolve()

    # Test workspace status when active
    result_status = runner.invoke(app, ["workspace", "status"])
    assert result_status.exit_code == 0
    assert "Active Project Workspace" in result_status.output
    assert "my_48hfp_project" in result_status.output

    # Test workspace switch to new dir
    ws_path2 = tmp_path / "second_film"
    ws_path2.mkdir()
    result_switch = runner.invoke(app, ["workspace", "switch", str(ws_path2)])
    assert result_switch.exit_code == 0
    assert "Switched active workspace" in result_switch.output
    assert get_active_workspace() == ws_path2.resolve()

    # Test workspace switch to non-existent dir
    result_fail = runner.invoke(app, ["workspace", "switch", str(tmp_path / "non_existent")])
    assert result_fail.exit_code != 0
    assert "Target workspace directory does not exist" in result_fail.output


def test_tui_workspace_hud_rendering(tmp_path):
    """Verify HeaderHUD and NavigationSidebar render active workspace context."""
    ws_dir = tmp_path / "TUI_Project"
    ws_dir.mkdir()
    set_active_workspace(ws_dir)

    hud = HeaderHUD()
    rendered_hud = hud.render()
    assert "Workspace: TUI_Project" in rendered_hud

    sidebar = NavigationSidebar()
    assert sidebar is not None

