"""Comprehensive automated unit and integration tests for Sprint 13.1.

Validates:
1. Data models: IdeaSeed.max_actors, VisualProfile, CharacterRosterItem.visual_profile, TeamProfile cast migration.
2. TUI screens: CastMemberScreen modal dialog, ProfileSetupScreen 7-column cast table, IdeaSeedScreen max_actors.
3. Constraint store: Seeding of new logistical setups (Diner, Park, Sedan, Laundromat) and Idea Seeds (Package, Deadline, Confessor).
4. Prompt compiler: Inclusion of visual attributes, max_actors constraint, and schema directives.
"""

from pathlib import Path
from typing import Dict, List, Optional
import pytest
from pydantic import ValidationError

from studio.models.constraints import IdeaSeed, LogisticalConstraint
from studio.models.profile import TeamProfile
from studio.models.treatment import (
    CharacterRosterItem,
    DialogueSnippetItem,
    FestivalComplianceChecklist,
    NarrativeSynopsis,
    SceneBreakdownItem,
    TitleAndLogline,
    TreatmentOutput,
    VisualProfile,
)
from studio.screens import CastMemberScreen, ProfileSetupScreen
from studio.screens_constraints import IdeaSeedScreen
from studio.tui import StudioApp
from studio.utils.constraint_store import (
    load_idea_seed,
    load_logistical_constraint,
    seed_default_constraints,
)
from studio.utils.global_state import clear_active_workspace, set_active_workspace
from studio.utils.prompt_builder import PromptBuilder


@pytest.fixture(autouse=True)
def clean_global_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Fixture ensuring an isolated global_state file and workspace for every test."""
    dummy_state_file = tmp_path / "global_state.yaml"
    monkeypatch.setattr("studio.utils.global_state.GLOBAL_STATE_FILE", dummy_state_file)
    monkeypatch.setattr("studio.utils.global_state.GLOBAL_STATE_DIR", tmp_path)
    clear_active_workspace()
    yield
    clear_active_workspace()


# ==============================================================================
# 1. DATA MODEL TESTS
# ==============================================================================


def test_idea_seed_max_actors_field():
    """Verify max_actors defaults to None, accepts positive ints, and rejects <= 0."""
    seed_default = IdeaSeed(
        name="test_default",
        inciting_incident="Incident",
        complications="Complication",
        ending_targets="Ending",
    )
    assert seed_default.max_actors is None

    seed_with_limit = IdeaSeed(
        name="test_limited",
        inciting_incident="Incident",
        complications="Complication",
        ending_targets="Ending",
        max_actors=3,
    )
    assert seed_with_limit.max_actors == 3

    with pytest.raises(ValidationError):
        IdeaSeed(
            name="test_invalid",
            inciting_incident="Incident",
            complications="Complication",
            ending_targets="Ending",
            max_actors=0,
        )

    with pytest.raises(ValidationError):
        IdeaSeed(
            name="test_negative",
            inciting_incident="Incident",
            complications="Complication",
            ending_targets="Ending",
            max_actors=-2,
        )


def test_visual_profile_and_character_roster_item():
    """Verify VisualProfile default initialization, custom values, and integration in CharacterRosterItem."""
    vp_default = VisualProfile()
    assert vp_default.ethnicity == "Unspecified"
    assert vp_default.hair == "Unspecified"
    assert vp_default.build == "Unspecified"
    assert vp_default.visual_anchor == "None"

    vp_custom = VisualProfile(
        ethnicity="East Asian",
        hair="Sharp jet-black bob",
        build="Athletic / Lean",
        visual_anchor="Scarlet red beret",
    )
    assert vp_custom.ethnicity == "East Asian"
    assert vp_custom.hair == "Sharp jet-black bob"
    assert vp_custom.build == "Athletic / Lean"
    assert vp_custom.visual_anchor == "Scarlet red beret"

    # CharacterRosterItem with default VisualProfile
    item_default = CharacterRosterItem(
        name="Officer Marcus",
        role="Protagonist",
        actor_or_traits="Cynical Detective",
    )
    assert item_default.visual_profile is not None
    assert item_default.visual_profile.ethnicity == "Unspecified"

    # CharacterRosterItem with custom VisualProfile
    item_custom = CharacterRosterItem(
        name="Elena Vance",
        role="Antagonist",
        actor_or_traits="Master Mind",
        visual_profile=vp_custom,
    )
    assert item_custom.visual_profile.visual_anchor == "Scarlet red beret"

    # Verify TreatmentOutput deserialization with VisualProfile
    treatment = TreatmentOutput(
        title_and_logline=TitleAndLogline(
            title="The Red Beret",
            genre_blend="Mystery / Thriller",
            logline="A detective tracks a phantom.",
        ),
        character_roster=[item_custom],
        synopsis=NarrativeSynopsis(
            act_1_setup="Setup",
            act_2_escalation="Escalation",
            act_3_climax_resolution="Climax",
            thematic_arc="Obsession",
        ),
        scene_breakdown=[
            SceneBreakdownItem(
                scene_number=1,
                heading="INT. DINER - NIGHT",
                location="Diner",
                time_of_day="NIGHT",
                characters_present=["Elena Vance"],
                action_summary="Elena waits by the window.",
                props_used=["Coffee mug"],
            )
        ],
        dialogue_snippets=[
            DialogueSnippetItem(
                character="Elena Vance",
                line="We don't have much time.",
                context_notes="Urgent delivery",
            )
        ],
        compliance_checklist=FestivalComplianceChecklist(
            verbatim_line_verified=True,
            prop_usage_verified=True,
            character_linkage_verified=True,
            pacing_runtime_verified=True,
            compliance_notes="Fully compliant.",
        ),
    )
    dumped = treatment.model_dump()
    assert dumped["character_roster"][0]["visual_profile"]["visual_anchor"] == "Scarlet red beret"


def test_team_profile_cast_migration_validator():
    """Verify TeamProfile migrates legacy cast dictionaries seamlessly."""
    legacy_data = {
        "team_name": "Indie Filmmakers",
        "admin_username": "sarah",
        "location": "Austin, TX",
        "cast": [
            {
                "name": "Jordan Cole",
                "age_range": "30s",
                "gender": "Male",
                "physicality": "Tall and wiry",
            }
        ],
    }
    profile = TeamProfile.model_validate(legacy_data)
    actor = profile.cast[0]
    assert actor["name"] == "Jordan Cole"
    assert actor["age_range"] == "30s"
    assert actor["gender"] == "Male"
    assert actor["ethnicity"] == "Unspecified"
    assert actor["hair"] == "Unspecified"
    assert actor["build"] == "Unspecified"
    assert actor["visual_anchor"] == "None"
    assert actor["physicality"] == "Tall and wiry"


# ==============================================================================
# 2. PRE-SEEDED CONTENT EXPANSION TESTS
# ==============================================================================


def test_seed_new_logistical_constraints(tmp_path: Path):
    """Verify all 4 new logistical constraints are seeded with clean, generic set dressing."""
    set_active_workspace(tmp_path)
    seed_default_constraints()

    new_slugs = [
        "late_night_diner_coffee_shop",
        "public_park",
        "stationary_sedan",
        "the_laundromat",
    ]

    for slug in new_slugs:
        c = load_logistical_constraint(slug)
        assert c is not None, f"Logistical constraint '{slug}' was not seeded!"
        assert len(c.locations) > 0
        assert len(c.sub_locations) > 0
        assert len(c.available_set_dressing) > 0

    # Ensure no specific real-world car brand in public_park or public_park_sports_court
    park = load_logistical_constraint("public_park")
    assert park is not None
    for dressing in park.available_set_dressing:
        assert "Honda" not in dressing
        assert "2022" not in dressing

    sports_park = load_logistical_constraint("public_park_sports_court")
    assert sports_park is not None
    for dressing in sports_park.available_set_dressing:
        assert "Honda" not in dressing
        assert "2022" not in dressing


def test_seed_new_idea_seeds(tmp_path: Path):
    """Verify all 4 idea seeds are seeded including the 3 new ones with max_actors."""
    set_active_workspace(tmp_path)
    seed_default_constraints()

    expected_seeds = {
        "late_night_visitor": 2,
        "misdirected_package": 2,
        "expired_deadline": 3,
        "uninvited_confessor": 2,
    }

    for name, expected_max in expected_seeds.items():
        seed = load_idea_seed(name)
        assert seed is not None, f"Idea seed '{name}' was not seeded!"
        assert seed.max_actors == expected_max
        assert len(seed.inciting_incident) > 0
        assert len(seed.complications) > 0
        assert len(seed.ending_targets) > 0


# ==============================================================================
# 3. PROMPT COMPILER ENHANCEMENT TESTS
# ==============================================================================


def test_prompt_builder_cast_visual_profiles_and_max_actors():
    """Verify PromptBuilder renders detailed cast visual attributes, max_actors, and visual schema directives."""
    profile = TeamProfile(
        team_name="Cinematic Vision",
        admin_username="alex",
        location="Portland, OR",
        cast=[
            {
                "name": "Maya Lin",
                "age_range": "20s",
                "gender": "Female",
                "ethnicity": "East Asian",
                "hair": "Sharp jet-black bob",
                "build": "Slender",
                "visual_anchor": "Scarlet red beret",
            }
        ],
    )
    idea = IdeaSeed(
        name="misdirected_package",
        description="Parcel at wrong doorstep.",
        inciting_incident="Delivery arrives unannounced.",
        complications="Sender wants it back immediately.",
        ending_targets="A difficult choice.",
        max_actors=2,
    )

    prompt = PromptBuilder.compile_system_prompt(
        draw=None,
        profile=profile,
        idea=idea,
    )

    # Verify cast visual profile details in prompt
    assert "Maya Lin" in prompt
    assert "Ethnicity: East Asian" in prompt
    assert "Hair: Sharp jet-black bob" in prompt
    assert "Build: Slender" in prompt
    assert "Signature Visual Anchor: Scarlet red beret" in prompt

    # Verify max_actors constraint in prompt
    assert "Maximum Recommended Actors / Cast Size: 2" in prompt
    assert "centered around at most 2 key actors" in prompt

    # Verify Visual Profile in Output Formatting directive
    assert "provide a complete Visual Profile" in prompt
    assert "signature visual anchor" in prompt


# ==============================================================================
# 4. TUI SCREEN TESTS
# ==============================================================================


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_cast_member_screen_modal(tmp_path: Path):
    """Test CastMemberScreen modal form input and submission."""
    set_active_workspace(tmp_path)
    app = StudioApp()

    async with app.run_test() as pilot:
        screen = CastMemberScreen()
        app.push_screen(screen)
        await pilot.pause()

        # Fill in all form fields
        screen.query_one("#member_name").value = "Alex Mercer"
        screen.query_one("#member_age").value = "30s"
        screen.query_one("#member_gender").value = "Non-Binary"
        screen.query_one("#member_ethnicity").value = "Hispanic/Latino"
        screen.query_one("#member_hair").value = "Wavy brown"
        screen.query_one("#member_build").value = "Athletic"
        screen.query_one("#member_anchor").value = "Aviator sunglasses"

        screen.action_save()
        await pilot.pause()


@pytest.mark.anyio
async def test_profile_setup_screen_cast_table(tmp_path: Path):
    """Test ProfileSetupScreen mounts 7-column cast table and loads cast members properly."""
    set_active_workspace(tmp_path)
    initial_profile = TeamProfile(
        team_name="Cyber Directors",
        admin_username="chris",
        location="Chicago, IL",
        cast=[
            {
                "name": "Jordan",
                "age_range": "40s",
                "gender": "Male",
                "ethnicity": "Black",
                "hair": "Buzz cut",
                "build": "Stocky",
                "visual_anchor": "Silver pocket watch",
            }
        ],
    )

    app = StudioApp()
    async with app.run_test() as pilot:
        screen = ProfileSetupScreen(current_profile=initial_profile)
        app.push_screen(screen)
        await pilot.pause()

        cast_table = screen.query_one("#cast_table")
        assert len(cast_table.columns) == 7
        assert cast_table.row_count == 1

        # Check remove cast member action
        cast_table.cursor_coordinate = (0, 0)
        screen.action_remove_selected_cast_member()
        await pilot.pause()
        assert len(screen.cast) == 0
        assert cast_table.row_count == 0


@pytest.mark.anyio
async def test_idea_seed_screen_max_actors_input(tmp_path: Path):
    """Test IdeaSeedScreen max_actors field interaction and persistence."""
    set_active_workspace(tmp_path)
    seed = IdeaSeed(
        name="test_seed",
        inciting_incident="Incident",
        complications="Complications",
        ending_targets="Target",
        max_actors=3,
    )

    app = StudioApp()
    async with app.run_test() as pilot:
        screen = IdeaSeedScreen(constraint=seed)
        app.push_screen(screen)
        await pilot.pause()

        max_input = screen.query_one("#max_actors")
        assert max_input.value == "3"

        max_input.value = "2"
        screen.action_save()
        await pilot.pause()

        saved = load_idea_seed("test_seed")
        assert saved is not None
        assert saved.max_actors == 2
