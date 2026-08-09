"""Unit and integration tests for Phase 3 (Friday Draw & Prompt Builder)."""

import pytest
from studio.models.draw import (
    FALLBACK_LINES,
    FALLBACK_NAMES,
    FALLBACK_PROPS,
    FALLBACK_TRAITS,
    GENRES_GROUP_1,
    GENRES_GROUP_2,
    FridayDraw,
    create_default_draw,
)
from studio.utils.draw_store import delete_draw, draw_exists, load_draw, save_draw
from studio.utils.prompt_builder import PromptBuilder


def test_genre_group_constants():
    """Verify Group 1 and Group 2 genre pools contain required genres."""
    assert "Action / Adventure" in GENRES_GROUP_1
    assert "Comedy" in GENRES_GROUP_1
    assert "Film Noir" in GENRES_GROUP_1
    assert "Thriller / Suspense" in GENRES_GROUP_1
    assert len(GENRES_GROUP_1) == 15

    assert "Buddy Film" in GENRES_GROUP_2
    assert "Heist" in GENRES_GROUP_2
    assert "Silent Film" in GENRES_GROUP_2
    assert "Workplace Film" in GENRES_GROUP_2
    assert len(GENRES_GROUP_2) == 15


def test_friday_draw_fallback_generator():
    """Verify create_default_draw applies valid defaults for blank inputs."""
    draw = create_default_draw()
    assert draw.genre_1 in GENRES_GROUP_1
    assert draw.genre_2 in GENRES_GROUP_2
    assert draw.character_name in FALLBACK_NAMES
    assert draw.character_trait in FALLBACK_TRAITS
    assert draw.required_prop in FALLBACK_PROPS
    assert draw.required_line in FALLBACK_LINES

    draw_empty = create_default_draw(
        genre_1="",
        genre_2="  ",
        character_name="",
        character_trait="  ",
        required_prop="",
        required_line="  ",
    )
    assert draw_empty.genre_1 in GENRES_GROUP_1
    assert draw_empty.genre_2 in GENRES_GROUP_2
    assert draw_empty.character_name in FALLBACK_NAMES
    assert draw_empty.character_trait in FALLBACK_TRAITS
    assert draw_empty.required_prop in FALLBACK_PROPS
    assert draw_empty.required_line in FALLBACK_LINES


def test_draw_store_lifecycle():
    """Test saving, loading, and deleting FridayDraw state."""
    draw = create_default_draw(
        genre_1="Sci Fi",
        genre_2="Heist",
        character_name="Test Agent",
        character_trait="Hacker",
        required_prop="Quantum Deck",
        required_line="Access granted.",
    )

    save_path = save_draw(draw)
    assert save_path.is_file()
    assert draw_exists()

    loaded = load_draw()
    assert loaded is not None
    assert loaded.genre_1 == "Sci Fi"
    assert loaded.genre_2 == "Heist"
    assert loaded.character_name == "Test Agent"
    assert loaded.required_prop == "Quantum Deck"

    delete_draw()
    assert not draw_exists()


def test_prompt_builder_hierarchy_and_recency_effect():
    """Verify prompt compiler ordering and anchoring of Immutable Rules at bottom."""
    draw = create_default_draw(
        genre_1="Film Noir",
        genre_2="Single Room Movie",
        character_name="Sam Spade",
        character_trait="Private Investigator",
        required_prop="Tarnished Silver Lighter",
        required_line="The rain never stops in this city.",
    )

    compiled = PromptBuilder.compile_system_prompt(draw=draw)

    # Check key sections are present
    assert "SYSTEM PERSONA DIRECTIVE" in compiled
    assert "1. GLOBAL PRODUCTION TEAM STATE & RESOURCES" in compiled
    assert "2. ACTIVE DIRECTORIAL VISION" in compiled
    assert "3. ACTIVE THEMATIC FRAMEWORK" in compiled
    assert "4. ACTIVE IDEA SEED" in compiled
    assert "5. ACTIVE LOGISTICAL CONSTRAINT SET" in compiled
    assert "6. OUTPUT FORMATTING & TREATMENT SCHEMA DIRECTIVES" in compiled
    assert "7. THE FRIDAY NIGHT DRAW (KICKOFF INPUT DATA)" in compiled
    assert "8. IMMUTABLE FESTIVAL RULES (STRICT COMPLIANCE MANDATE - RECENCY EFFECT)" in compiled

    # Verify Recency Effect: Immutable rules are at the very bottom
    sections = compiled.split("================================================================================\n")
    last_section = sections[-1]
    assert "IMMUTABLE FESTIVAL RULES" in sections[-2] or "IMMUTABLE FESTIVAL RULES" in last_section
    assert "4 to 7 minute total runtime" in last_section
    assert "The rain never stops in this city." in last_section
    assert "Tarnished Silver Lighter" in last_section
    assert "Sam Spade" in last_section
