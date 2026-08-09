"""Unit and integration tests for Sprint 7.0 (The Tri-Split Constraint Architecture)."""

from unittest.mock import patch
import pytest

from studio.models.constraints import (
    ConstraintType,
    DirectorialVision,
    IdeaSeed,
    LogisticalConstraint,
    ThematicFramework,
)
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.screens_constraints import (
    DirectorialVisionScreen,
    IdeaSeedScreen,
    LogisticalConstraintScreen,
    ThematicFrameworkScreen,
)
from studio.screens_library import ConstraintLibraryScreen
from studio.tui import StudioApp
from studio.utils.constraint_store import (
    delete_directorial_vision,
    delete_idea_seed,
    delete_logistical_constraint,
    delete_thematic_framework,
    list_directorial_visions,
    list_idea_seeds,
    list_logistical_constraints,
    list_thematic_frameworks,
    load_directorial_vision,
    load_idea_seed,
    load_logistical_constraint,
    load_thematic_framework,
    save_directorial_vision,
    save_idea_seed,
    save_logistical_constraint,
    save_thematic_framework,
    seed_default_constraints,
)
from studio.utils.prompt_builder import PromptBuilder
from textual.widgets import Button, Input, TabbedContent, TextArea


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def sample_profile():
    return TeamProfile(
        team_name="Tri-Split Team",
        admin_username="director_lead",
        location="Los Angeles, CA",
        active_logistical_constraint="interior_indie_crew",
        active_directorial_vision="a24_slow_burn",
        active_thematic_framework="existential_dread",
        active_idea_seed="late_night_visitor",
    )


def test_models_and_slug_validation():
    """Verify tri-split constraint models validate slugs and update timestamps."""
    dv = DirectorialVision(
        name="Noir Visuals ",
        description="High contrast noir",
        visual_economy="Static shots",
        lighting_color="Chiaroscuro",
        audio_landscape="Jazz solos",
    )
    assert dv.name == "noir_visuals"
    assert dv.visual_economy == "Static shots"

    tf = ThematicFramework(
        name="  Identity Quest ",
        core_philosophy="Who am I?",
        emotional_arc="Disillusionment to acceptance",
        world_rules="No magic allowed",
    )
    assert tf.name == "identity_quest"
    assert tf.core_philosophy == "Who am I?"

    ids = IdeaSeed(
        name=" Mysterious Box ",
        inciting_incident="A box arrives",
        complications="It hums loudly",
        ending_targets="It opens automatically",
    )
    assert ids.name == "mysterious_box"
    assert ids.inciting_incident == "A box arrives"

    assert ConstraintType.LOGISTICAL == "logistical"
    assert ConstraintType.DIRECTORIAL == "directorial"
    assert ConstraintType.THEMATIC == "thematic"
    assert ConstraintType.IDEA == "idea"


def test_constraint_store_crud(tmp_path):
    """Verify full CRUD operations for DirectorialVision, ThematicFramework, and IdeaSeed."""
    constraints_dir = tmp_path / "constraints"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir):
        # 1. Directorial Vision CRUD
        dv = DirectorialVision(name="indie_mood", visual_economy="Slow pans", lighting_color="Warm gold", audio_landscape="Acoustic guitar")
        save_directorial_vision(dv)

        loaded_dv = load_directorial_vision("indie_mood")
        assert loaded_dv is not None
        assert loaded_dv.visual_economy == "Slow pans"
        assert len(list_directorial_visions()) == 1

        assert delete_directorial_vision("indie_mood") is True
        assert load_directorial_vision("indie_mood") is None
        assert len(list_directorial_visions()) == 0

        # 2. Thematic Framework CRUD
        tf = ThematicFramework(name="redemption_arc", core_philosophy="Forgiveness", emotional_arc="Guilt to peace", world_rules="Strict realism")
        save_thematic_framework(tf)

        loaded_tf = load_thematic_framework("redemption_arc")
        assert loaded_tf is not None
        assert loaded_tf.core_philosophy == "Forgiveness"
        assert len(list_thematic_frameworks()) == 1

        assert delete_thematic_framework("redemption_arc") is True
        assert load_thematic_framework("redemption_arc") is None

        # 3. Idea Seed CRUD
        idea = IdeaSeed(name="time_capsule", inciting_incident="Found capsule", complications="Missing key", ending_targets="Twist reveal")
        save_idea_seed(idea)

        loaded_idea = load_idea_seed("time_capsule")
        assert loaded_idea is not None
        assert loaded_idea.inciting_incident == "Found capsule"
        assert len(list_idea_seeds()) == 1

        assert delete_idea_seed("time_capsule") is True
        assert load_idea_seed("time_capsule") is None


def test_seed_default_constraints(tmp_path):
    """Verify seed_default_constraints generates 4 starter sets when directories are empty."""
    constraints_dir = tmp_path / "constraints"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir):
        p_log, p_dir, p_them, p_idea = seed_default_constraints()

        assert p_log is not None and p_log.exists()
        assert p_dir is not None and p_dir.exists()
        assert p_them is not None and p_them.exists()
        assert p_idea is not None and p_idea.exists()

        assert len(list_logistical_constraints()) == 1
        assert len(list_directorial_visions()) == 12
        assert len(list_thematic_frameworks()) == 12
        assert len(list_idea_seeds()) == 1


def test_prompt_builder_compiles_all_four_constraint_sets(sample_profile):
    """Verify PromptBuilder includes all 4 constraint set sections in compiled system prompt."""
    draw = FridayDraw(
        genre_1="Drama",
        genre_2="Mystery",
        character_name="Morgan Reed",
        character_trait="Detective",
        character_gender="Female",
        required_prop="Magnifying Glass",
        required_line="Follow the clues.",
    )

    dv = DirectorialVision(name="a24_slow_burn", visual_economy="Long static takes", lighting_color="Warm tones", audio_landscape="Synth drones")
    tf = ThematicFramework(name="existential_dread", core_philosophy="Tension through silence", emotional_arc="Subtle escalation", world_rules="Domestic realism")
    idea = IdeaSeed(name="late_night_visitor", inciting_incident="Unplanned reunion", complications="Lost key", ending_targets="Surprise forgiveness")
    log = LogisticalConstraint(name="interior_indie_crew", description="Indoor shoot setup", locations=["Interior", "Apartment"])

    prompt = PromptBuilder.compile_system_prompt(
        draw=draw,
        profile=sample_profile,
        logistical=log,
        directorial=dv,
        thematic=tf,
        idea=idea,
    )

    assert "1. GLOBAL PRODUCTION TEAM STATE & RESOURCES" in prompt
    assert "2. ACTIVE DIRECTORIAL VISION" in prompt
    assert "a24_slow_burn" in prompt
    assert "Long static takes" in prompt

    assert "3. ACTIVE THEMATIC FRAMEWORK" in prompt
    assert "existential_dread" in prompt
    assert "Tension through silence" in prompt

    assert "4. ACTIVE IDEA SEED" in prompt
    assert "late_night_visitor" in prompt
    assert "Unplanned reunion" in prompt

    assert "5. ACTIVE LOGISTICAL CONSTRAINT SET" in prompt
    assert "interior_indie_crew" in prompt


@pytest.mark.anyio
async def test_directorial_and_thematic_screens(tmp_path):
    """Verify DirectorialVisionScreen and ThematicFrameworkScreen submit modal forms."""
    constraints_dir = tmp_path / "constraints"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir):
        app = StudioApp()
        async with app.run_test() as pilot:
            # Directorial Screen
            dir_screen = DirectorialVisionScreen()
            dir_res = []
            app.push_screen(dir_screen, callback=lambda res: dir_res.append(res))
            await pilot.pause()

            dir_screen.query_one("#name", Input).value = "techno_thriller"
            dir_screen.query_one("#description", Input).value = "Fast paced tech vision"
            dir_screen.query_one("#visual_economy", TextArea).text = "Rapid cuts"
            dir_screen.query_one("#lighting_color", TextArea).text = "Neon cyan"
            dir_screen.query_one("#audio_landscape", TextArea).text = "Cyberpunk audio"

            await pilot.click("#save_directorial_btn")
            await pilot.pause()

            assert len(dir_res) == 1
            assert dir_res[0].name == "techno_thriller"

            # Thematic Screen
            them_screen = ThematicFrameworkScreen()
            them_res = []
            app.push_screen(them_screen, callback=lambda res: them_res.append(res))
            await pilot.pause()

            them_screen.query_one("#name", Input).value = "artificial_ethics"
            them_screen.query_one("#description", Input).value = "AI morality"
            them_screen.query_one("#core_philosophy", TextArea).text = "Can machines feel?"
            them_screen.query_one("#emotional_arc", TextArea).text = "Doubt to empathy"
            them_screen.query_one("#world_rules", TextArea).text = "Near future tech"

            await pilot.click("#save_thematic_btn")
            await pilot.pause()

            assert len(them_res) == 1
            assert them_res[0].name == "artificial_ethics"


@pytest.mark.anyio
async def test_idea_seed_screen(tmp_path):
    """Verify IdeaSeedScreen submit modal form."""
    constraints_dir = tmp_path / "constraints"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir):
        app = StudioApp()
        async with app.run_test() as pilot:
            idea_screen = IdeaSeedScreen()
            idea_res = []
            app.push_screen(idea_screen, callback=lambda res: idea_res.append(res))
            await pilot.pause()

            idea_screen.query_one("#name", Input).value = "stolen_hard_drive"
            idea_screen.query_one("#description", Input).value = "Drive heist"
            idea_screen.query_one("#inciting_incident", TextArea).text = "Drive is missing"
            idea_screen.query_one("#complications", TextArea).text = "Password encrypted"
            idea_screen.query_one("#ending_targets", TextArea).text = "Decrypted reveal"

            await pilot.click("#save_idea_btn")
            await pilot.pause()

            assert len(idea_res) == 1
            assert idea_res[0].name == "stolen_hard_drive"


@pytest.mark.anyio
async def test_constraint_library_tab_switching_and_activation(tmp_path, sample_profile):
    """Verify ConstraintLibraryScreen populates all 4 tabs and supports activation across categories."""
    constraints_dir = tmp_path / "constraints"
    profile_file = tmp_path / ".48hfp_profile.yaml"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir), patch(
        "studio.utils.profile_store.get_profile_path", return_value=profile_file
    ):
        seed_default_constraints()

        app = StudioApp()
        async with app.run_test() as pilot:
            library_screen = ConstraintLibraryScreen(sample_profile)
            app.push_screen(library_screen)
            await pilot.pause()

            tabbed = library_screen.query_one("#library_tabs", TabbedContent)
            assert tabbed is not None

            # Switch to Directorial Vision tab
            tabbed.active = "tab_directorial"
            await pilot.pause()

            assert library_screen._get_active_category() == "directorial"

            # Set active on directorial tab
            dir_table = library_screen.query_one("#directorial_table")
            dir_table.focus()
            row_idx = dir_table.get_row_index("wes_anderson")
            dir_table.move_cursor(row=row_idx)
            await pilot.pause()

            library_screen.query_one("#btn_set_active", Button).press()
            await pilot.pause()

            assert sample_profile.active_directorial_vision == "wes_anderson"

            # Switch to Thematic tab
            tabbed.active = "tab_thematic"
            await pilot.pause()

            assert library_screen._get_active_category() == "thematic"

            # Set active on thematic tab
            them_table = library_screen.query_one("#thematic_table")
            them_table.focus()
            row_idx = them_table.get_row_index("wes_anderson")
            them_table.move_cursor(row=row_idx)
            await pilot.pause()

            library_screen.query_one("#btn_set_active", Button).press()
            await pilot.pause()

            assert sample_profile.active_thematic_framework == "wes_anderson"
