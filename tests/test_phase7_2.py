"""Unit and integration tests for Sprint 7.2 (Data Model Refactor & Workspace Enhancements)."""

from unittest.mock import patch
import pytest

from studio.models.constraints import LogisticalConstraint
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.screens import ProfileSetupScreen
from studio.screens_constraints import LogisticalConstraintScreen
from studio.tui import StudioApp
from studio.utils.prompt_builder import PromptBuilder
from studio.workspace import RecipePane
from textual.widgets import Input, TextArea


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_team_profile_schema_refactor_and_legacy_migration():
    """Verify TeamProfile models crew, cast, gear, and handles legacy 'roles' migration."""
    # 1. New schema
    profile = TeamProfile(
        team_name="Indie Crew",
        admin_username="alex_dp",
        location="Austin, TX",
        crew={"Director": ["Alex"], "Producer": ["Jordan"]},
        cast=[
            {
                "name": "Sam",
                "age_range": "20s-30s",
                "gender": "Non-binary",
                "physicality": "Athletic, tall",
            }
        ],
        available_gear=["RED Komodo 6K", "Aputure 300d", "Rode Wireless GO II"],
    )

    assert profile.crew["Director"] == ["Alex"]
    assert profile.roles["Producer"] == ["Jordan"]  # Backward compatibility property
    assert len(profile.cast) == 1
    assert profile.cast[0]["name"] == "Sam"
    assert len(profile.available_gear) == 3

    # 2. Legacy YAML deserialization (roles -> crew)
    legacy_data = {
        "team_name": "Legacy Team",
        "admin_username": "old_admin",
        "location": "Dallas, TX",
        "roles": {"Cinematographer": ["Chris"]},
    }
    migrated_profile = TeamProfile(**legacy_data)
    assert migrated_profile.crew == {"Cinematographer": ["Chris"]}
    assert migrated_profile.roles == {"Cinematographer": ["Chris"]}


def test_logistical_constraint_schema_cleanup():
    """Verify LogisticalConstraint schema cleanup and legacy 'props_and_dialogue' migration."""
    # 1. New schema
    log = LogisticalConstraint(
        name="warehouse_shoot",
        description="Industrial warehouse location",
        locations=["Warehouse", "Night"],
        location_details="High ceilings, echoes",
        available_set_dressing=["Wooden crates", "Forklift", "Dusty lamp"],
    )

    assert log.name == "warehouse_shoot"
    assert log.location_details == "High ceilings, echoes"
    assert len(log.available_set_dressing) == 3
    assert log.props_and_dialogue == ["Wooden crates", "Forklift", "Dusty lamp"]

    # 2. Legacy migration
    legacy_data = {
        "name": "legacy_set",
        "main_character_details": {"name": "Old Char"},
        "props_and_dialogue": ["Old prop 1", "Old prop 2"],
    }
    migrated_log = LogisticalConstraint(**legacy_data)
    assert migrated_log.available_set_dressing == ["Old prop 1", "Old prop 2"]
    assert not hasattr(migrated_log, "main_character_details")


def test_prompt_builder_empty_instructions_handling():
    """Verify ADDITIONAL FILMMAKER DIRECTIVES is completely omitted if empty or whitespace."""
    draw = FridayDraw(
        genre_1="Comedy",
        genre_2="Sci-Fi",
        character_name="Dr. EV",
        character_trait="Inventor",
        character_gender="Male",
        required_prop="Laser Pointer",
        required_line="Check the batteries.",
    )
    profile = TeamProfile(
        team_name="SciFi Crew",
        admin_username="inventor_1",
        location="Seattle, WA",
    )

    # None
    prompt_none = PromptBuilder.compile_system_prompt(draw=draw, profile=profile, additional_instructions=None)
    assert "ADDITIONAL FILMMAKER DIRECTIVES" not in prompt_none

    # Empty string
    prompt_empty = PromptBuilder.compile_system_prompt(draw=draw, profile=profile, additional_instructions="")
    assert "ADDITIONAL FILMMAKER DIRECTIVES" not in prompt_empty

    # Whitespace only
    prompt_ws = PromptBuilder.compile_system_prompt(draw=draw, profile=profile, additional_instructions="    \n\t  ")
    assert "ADDITIONAL FILMMAKER DIRECTIVES" not in prompt_ws

    # Non-empty instructions
    prompt_with_instructions = PromptBuilder.compile_system_prompt(
        draw=draw,
        profile=profile,
        additional_instructions="Emphasize slapstick physical humor during scene 2.",
    )
    assert "ADDITIONAL FILMMAKER DIRECTIVES" in prompt_with_instructions
    assert "Emphasize slapstick physical humor during scene 2." in prompt_with_instructions


def test_prompt_builder_renders_crew_cast_gear_set_dressing():
    """Verify PromptBuilder renders crew, cast, gear, and set dressing in prompt sections."""
    profile = TeamProfile(
        team_name="Pro Crew",
        admin_username="pro_admin",
        location="Miami, FL",
        crew={"Director": ["Dave"], "DP": ["Sarah"]},
        cast=[{"name": "Elena", "age_range": "30s", "gender": "Female", "physicality": "Tall, dark hair"}],
        available_gear=["Sony FX6", "DZOFilm Zoom"],
    )
    log = LogisticalConstraint(
        name="miami_beach",
        locations=["Exterior", "Beach"],
        location_details="Bright sunlight",
        available_set_dressing=["Beach towel", "Lifeguard tower", "Surfboard"],
    )

    prompt = PromptBuilder.compile_system_prompt(profile=profile, logistical=log)

    assert "1. GLOBAL PRODUCTION TEAM STATE & RESOURCES" in prompt
    assert "• Director: Dave" in prompt
    assert "• Elena: Age 30s, Gender: Female, Physicality: Tall, dark hair" in prompt
    assert "• Sony FX6" in prompt

    assert "5. ACTIVE LOGISTICAL CONSTRAINT SET" in prompt
    assert "miami_beach" in prompt
    assert "• Beach towel" in prompt


@pytest.mark.anyio
async def test_profile_setup_screen_with_cast_and_gear(tmp_path):
    """Verify ProfileSetupScreen inputs crew, 4-input cast, and gear catalog."""
    profile_file = tmp_path / ".48hfp_profile.yaml"

    with patch("studio.utils.profile_store.get_profile_path", return_value=profile_file):
        app = StudioApp()
        async with app.run_test() as pilot:
            screen = ProfileSetupScreen()
            saved_results = []
            app.push_screen(screen, callback=lambda res: saved_results.append(res))
            await pilot.pause()

            screen.query_one("#team_name", Input).value = "Apex Films"
            screen.query_one("#admin_username", Input).value = "apex_admin"
            screen.query_one("#location", Input).value = "Denver, CO"

            # Add Cast member (4 inputs)
            screen.query_one("#cast_name", Input).value = "Taylor"
            screen.query_one("#cast_age", Input).value = "40s"
            screen.query_one("#cast_gender", Input).value = "Male"
            screen.query_one("#cast_physicality", Input).value = "Bearded, rugged"
            screen.query_one("#add_cast_btn").press()
            await pilot.pause()

            assert len(screen.cast) == 1
            assert screen.cast[0]["name"] == "Taylor"

            # Gear
            screen.query_one("#available_gear", TextArea).text = "Canon C300 Mark III\nSennheiser MKH416"

            screen.query_one("#save_profile_btn").press()
            await pilot.pause()

            assert len(saved_results) == 1
            p = saved_results[0]
            assert p.team_name == "Apex Films"
            assert len(p.cast) == 1
            assert p.cast[0]["name"] == "Taylor"
            assert len(p.available_gear) == 2


@pytest.mark.anyio
async def test_logistical_constraint_screen_location_details_bug_fix(tmp_path):
    """Verify LogisticalConstraintScreen extracts location_details and available_set_dressing."""
    constraints_dir = tmp_path / "constraints"

    with patch("studio.utils.constraint_store.get_constraints_base_dir", return_value=constraints_dir):
        app = StudioApp()
        async with app.run_test() as pilot:
            screen = LogisticalConstraintScreen()
            saved_results = []
            app.push_screen(screen, callback=lambda res: saved_results.append(res))
            await pilot.pause()

            screen.query_one("#name", Input).value = "diner_night"
            screen.query_one("#description", Input).value = "Late night diner shoot"
            screen.query_one("#location_details", TextArea).text = "Neon signs, booth seating, fluorescent lighting"
            screen.query_one("#available_set_dressing", TextArea).text = "Coffee pot\nJukebox\nMenu boards"

            await pilot.click("#save_logistical_btn")
            await pilot.pause()

            assert len(saved_results) == 1
            c = saved_results[0]
            assert c.name == "diner_night"
            assert c.location_details == "Neon signs, booth seating, fluorescent lighting"
            assert c.available_set_dressing == ["Coffee pot", "Jukebox", "Menu boards"]


def test_recipe_pane_transient_text_area_height_css():
    """Verify RecipePane CSS assigns explicit height/max-height to additional_instructions TextArea."""
    css = RecipePane.DEFAULT_CSS
    assert "#additional_instructions" in css
    assert "height: 5;" in css or "height: 6;" in css or "max-height:" in css
