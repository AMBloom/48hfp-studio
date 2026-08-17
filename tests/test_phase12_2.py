"""Comprehensive unit and integration tests for Sprint 12.2: Navigation & View State."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from textual.widgets import Button, Static

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
from studio.screens_screenplay import ScreenplayWorkspace, highlight_fountain_lines
from studio.screens_shotlist import ShotListWorkspace
from studio.screens_storyboard import StoryboardsWorkspace
from studio.tui import NavigationSidebar, StudioApp
from studio.workspace import RecipePane, StudioWorkspace


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def sample_profile() -> TeamProfile:
    return TeamProfile(
        team_name="Cyber Directors",
        admin_username="alex_admin",
        location="San Francisco, CA",
        active_genre_rule="Hard Sci-Fi only",
    )


@pytest.fixture
def sample_draw() -> FridayDraw:
    return FridayDraw(
        genre_1="Sci-Fi",
        genre_2="Heist",
        character_name="Sam Taylor",
        character_trait="Quantum Physicist",
        character_gender="Non-Binary",
        required_prop="Silver Chronometer",
        required_line="We are out of time.",
    )


@pytest.fixture
def sample_treatment(sample_draw) -> TreatmentOutput:
    return TreatmentOutput(
        title_and_logline=TitleAndLogline(
            title="Chronos Protocol",
            genre_blend="Sci-Fi / Heist",
            logline="A physicist races against time to stop a temporal collapse.",
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
            act_1_setup="Sam invents a temporal device.",
            act_2_escalation="Agents try to steal the chronometer.",
            act_3_climax_resolution="Sam stabilizes the chronometer.",
            thematic_arc="Acceptance of destiny.",
        ),
        scene_breakdown=[
            SceneBreakdownItem(
                scene_number=1,
                heading="INT. LAB - NIGHT",
                location="Lab",
                time_of_day="NIGHT",
                characters_present=["Sam Taylor"],
                action_summary="Sam inspects the device.",
                props_used=["Silver Chronometer"],
            )
        ],
        dialogue_snippets=[
            DialogueSnippetItem(
                character="Sam Taylor",
                line="We are out of time.",
                is_required_line=True,
                context_notes="Whispered in panic.",
            )
        ],
        compliance_checklist=FestivalComplianceChecklist(
            verbatim_line_verified=True,
            prop_usage_verified=True,
            character_linkage_verified=True,
            pacing_runtime_verified=True,
            compliance_notes="All constraints verified.",
        ),
    )


@pytest.fixture
def sample_shotlist() -> ShotListBase:
    return ShotListBase(
        title="Chronos Protocol",
        shots=[
            ShotItem(
                shot_number=1,
                scene_number="1",
                location="INT. LAB - NIGHT",
                setup="Setup 1",
                shot_size="Close-up (CU)",
                camera_angle="Eye Level",
                camera_movement="Static",
                equipment="Tripod",
                lens="50mm",
                frame_rate="24fps",
                description="Sam checks the chronometer display.",
                cast=["Sam"],
                time_estimate_mins=15,
                notes="Capture glowing LED readout",
            ),
            ShotItem(
                shot_number=2,
                scene_number="1",
                location="INT. LAB - NIGHT",
                setup="Setup 1",
                shot_size="Wide Shot (WS)",
                camera_angle="High Angle",
                camera_movement="Pan Right",
                equipment="Dolly",
                lens="24mm",
                frame_rate="24fps",
                description="The lab equipment flashes erratically.",
                cast=["Sam"],
                time_estimate_mins=20,
                notes="Wide lighting setup",
            ),
        ],
    )


# ----------------------------------------------------------------------
# 1. Fountain Syntax Highlighting & Pagination Tests
# ----------------------------------------------------------------------

def test_fountain_syntax_highlighting_dialogue_state() -> None:
    """Test stateful dialogue highlighting (bold green) following characters and parentheticals."""
    lines = [
        "EXT. LAB - NIGHT",
        "",
        "SAM TAYLOR",
        "(whispering)",
        "We are out of time.",
        "The chronometer is failing.",
        "",
        "Sam rushes across the room.",
        "",
        "FADE OUT:",
    ]

    styled_text = highlight_fountain_lines(lines)
    plain = styled_text.plain
    assert "EXT. LAB - NIGHT" in plain
    assert "SAM TAYLOR" in plain
    assert "(whispering)" in plain
    assert "We are out of time." in plain
    assert "The chronometer is failing." in plain
    assert "Sam rushes across the room." in plain
    assert "FADE OUT:" in plain

    # Check styled spans
    styles = [span.style for span in styled_text.spans]
    assert "bold cyan" in styles
    assert "bold yellow" in styles
    assert "italic magenta" in styles
    assert "bold green" in styles


def test_fountain_pagination_visual_wrapping_and_explicit_breaks() -> None:
    """Test visual pagination wrapping lines > 68 chars and handling explicit '===' page breaks."""
    long_line = "A" * 150  # wraps into multiple lines
    script_with_break = f"INT. ROOM - DAY\n\n{long_line}\n\n===\n\nEXT. ROOFTOP - NIGHT\n\nFinal showdown."

    workspace = ScreenplayWorkspace()
    workspace.fountain_text = script_with_break

    pages = workspace._paginate_fountain()
    assert len(pages) == 2
    assert any("INT. ROOM - DAY" in line for line in pages[0])
    assert any("EXT. ROOFTOP - NIGHT" in line for line in pages[1])


def test_fountain_pagination_line_threshold() -> None:
    """Test automatic page boundary after exceeding LINES_PER_PAGE (52 lines)."""
    lines = [f"Line {i} of action description." for i in range(1, 65)]
    script = "\n".join(lines)

    workspace = ScreenplayWorkspace()
    workspace.fountain_text = script

    pages = workspace._paginate_fountain()
    assert len(pages) == 2
    assert len(pages[0]) <= 52


# ----------------------------------------------------------------------
# 2. NavigationSidebar & View State Integration Tests
# ----------------------------------------------------------------------

def test_navigation_sidebar_initial_state() -> None:
    """Test NavigationSidebar view buttons and initial active_view state."""
    sidebar = NavigationSidebar()
    assert sidebar.active_view == "treatment"
    sidebar.active_view = "screenplay"
    assert sidebar.active_view == "screenplay"


@pytest.mark.anyio
async def test_tui_four_workspace_views_mounted() -> None:
    """Verify that all 4 workspace views are mounted and present in DOM."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            treatment_ws = app.query_one("#main-workspace", StudioWorkspace)
            screenplay_ws = app.query_one("#screenplay-workspace", ScreenplayWorkspace)
            shotlist_ws = app.query_one("#shotlist-workspace", ShotListWorkspace)
            storyboard_ws = app.query_one("#storyboard-workspace", StoryboardsWorkspace)

            assert treatment_ws is not None
            assert screenplay_ws is not None
            assert shotlist_ws is not None
            assert storyboard_ws is not None

            # Initial view is treatment: only treatment workspace is visible
            assert treatment_ws.display is True
            assert screenplay_ws.display is False
            assert shotlist_ws.display is False
            assert storyboard_ws.display is False


@pytest.mark.anyio
async def test_tui_view_switching_via_hotkeys() -> None:
    """Test switching workspace views using hotkeys 1, 2, 3, and 4."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            treatment_ws = app.query_one("#main-workspace", StudioWorkspace)
            screenplay_ws = app.query_one("#screenplay-workspace", ScreenplayWorkspace)
            shotlist_ws = app.query_one("#shotlist-workspace", ShotListWorkspace)
            storyboard_ws = app.query_one("#storyboard-workspace", StoryboardsWorkspace)

            # Press '2' -> Screenplay
            await pilot.press("2")
            assert app.active_view == "screenplay"
            assert treatment_ws.display is False
            assert screenplay_ws.display is True
            assert shotlist_ws.display is False
            assert storyboard_ws.display is False

            # Press '3' -> Shot List
            await pilot.press("3")
            assert app.active_view == "shotlist"
            assert treatment_ws.display is False
            assert screenplay_ws.display is False
            assert shotlist_ws.display is True
            assert storyboard_ws.display is False

            # Press '4' -> Storyboards
            await pilot.press("4")
            assert app.active_view == "storyboards"
            assert treatment_ws.display is False
            assert screenplay_ws.display is False
            assert shotlist_ws.display is False
            assert storyboard_ws.display is True

            # Press '1' -> Back to Treatment
            await pilot.press("1")
            assert app.active_view == "treatment"
            assert treatment_ws.display is True
            assert screenplay_ws.display is False
            assert shotlist_ws.display is False
            assert storyboard_ws.display is False


@pytest.mark.anyio
async def test_tui_view_switching_via_sidebar_buttons() -> None:
    """Test switching views by clicking NavigationSidebar buttons."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            sidebar = app.query_one(NavigationSidebar)

            # Click Screenplay button
            btn_screenplay = sidebar.query_one("#btn_nav_screenplay")
            await pilot.click(btn_screenplay)
            assert app.active_view == "screenplay"

            # Click Shot List button
            btn_shotlist = sidebar.query_one("#btn_nav_shotlist")
            await pilot.click(btn_shotlist)
            assert app.active_view == "shotlist"

            # Click Storyboards button
            btn_storyboards = sidebar.query_one("#btn_nav_storyboards")
            await pilot.click(btn_storyboards)
            assert app.active_view == "storyboards"

            # Click Treatment button
            btn_treatment = sidebar.query_one("#btn_nav_treatment")
            await pilot.click(btn_treatment)
            assert app.active_view == "treatment"


@pytest.mark.anyio
async def test_tui_in_memory_view_state_preservation() -> None:
    """Test that switching views preserves state across workspaces in memory."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            # Set state in screenplay
            sample_script = "INT. LAB - NIGHT\n\nSAM\nHello world."
            app.current_screenplay_text = sample_script
            screenplay_ws = app.query_one("#screenplay-workspace", ScreenplayWorkspace)
            assert screenplay_ws.fountain_text == sample_script

            # Switch back and forth
            await pilot.press("1")
            assert app.active_view == "treatment"
            await pilot.press("2")
            assert app.active_view == "screenplay"

            # Verify text is preserved
            assert screenplay_ws.fountain_text == sample_script


# ----------------------------------------------------------------------
# 3. Empty State CTAs and Toolbar Back Button Flow Tests
# ----------------------------------------------------------------------

@pytest.mark.anyio
async def test_screenplay_empty_state_and_back_button(sample_treatment) -> None:
    """Test Screenplay workspace empty state CTA and back button navigation."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            app.current_treatment_obj = sample_treatment
            await pilot.press("2")  # Switch to Screenplay
            screenplay_ws = app.query_one("#screenplay-workspace", ScreenplayWorkspace)

            # Check back button switches view back to treatment
            btn_back = screenplay_ws.query_one("#btn_back_to_treatment")
            await pilot.click(btn_back)
            assert app.active_view == "treatment"

            # Switch back to screenplay and click empty state CTA
            await pilot.press("2")
            btn_cta = screenplay_ws.query_one("#btn_empty_generate_screenplay")
            with patch.object(app, "action_generate_screenplay") as mock_gen:
                btn_cta.press()
                await pilot.pause()
                assert mock_gen.called


@pytest.mark.anyio
async def test_shotlist_empty_state_and_back_button() -> None:
    """Test Shot List workspace empty state CTA and back button navigation."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            app.current_screenplay_text = "INT. LAB - NIGHT\n\nSAM\nTest script."
            await pilot.press("3")  # Switch to Shot List
            shotlist_ws = app.query_one("#shotlist-workspace", ShotListWorkspace)

            # Check back button switches view to screenplay
            btn_back = shotlist_ws.query_one("#btn_back_to_screenplay")
            await pilot.click(btn_back)
            assert app.active_view == "screenplay"

            # Switch back to shot list and click empty state CTA
            await pilot.press("3")
            btn_cta = shotlist_ws.query_one("#btn_empty_generate_shotlist")
            with patch.object(app, "action_generate_shotlist") as mock_gen:
                btn_cta.press()
                await pilot.pause()
                assert mock_gen.called


@pytest.mark.anyio
async def test_storyboards_empty_state_and_back_button(sample_shotlist) -> None:
    """Test Storyboards workspace empty state CTA and back button navigation."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            app.current_shotlist_obj = sample_shotlist
            await pilot.press("4")  # Switch to Storyboards
            sb_ws = app.query_one("#storyboard-workspace", StoryboardsWorkspace)

            # Check back button switches view to shot list
            btn_back = sb_ws.query_one("#btn_back_to_shotlist")
            await pilot.click(btn_back)
            assert app.active_view == "shotlist"

            # Switch back to storyboards and click empty state CTA
            await pilot.press("4")
            btn_cta = sb_ws.query_one("#btn_empty_generate_storyboards")
            with patch.object(app, "action_generate_storyboards") as mock_gen:
                btn_cta.press()
                await pilot.pause()
                assert mock_gen.called


# ----------------------------------------------------------------------
# 4. RecipePane Dynamic Refresh Tests
# ----------------------------------------------------------------------

@pytest.mark.anyio
async def test_recipe_pane_dynamic_refresh_on_updates(sample_profile, sample_draw) -> None:
    """Test RecipePane dynamically updates its rendered content when update_profile/draw is called."""
    with patch("studio.tui.load_profile", return_value=None), patch(
        "studio.tui.load_draw", return_value=None
    ):
        app = StudioApp()
        async with app.run_test() as pilot:
            recipe_pane = app.query_one(RecipePane)

            # Initially unconfigured / no draw
            assert recipe_pane.profile is None
            assert recipe_pane.draw is None

            # Update profile
            app.update_profile(sample_profile)
            await pilot.pause()
            assert recipe_pane.profile == sample_profile
            updated_prof_text = str(recipe_pane.query_one("#recipe-content", Static).render())
            assert "Cyber Directors" in updated_prof_text

            # Update draw
            app.update_draw(sample_draw)
            await pilot.pause()
            assert recipe_pane.draw == sample_draw
            updated_draw_text = str(recipe_pane.query_one("#recipe-content", Static).render())
            assert "Sci-Fi" in updated_draw_text
            assert "Sam Taylor" in updated_draw_text
