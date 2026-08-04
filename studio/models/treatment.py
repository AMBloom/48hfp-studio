"""Treatment output schema models for 48HFP-Studio.

Represents the complete pre-production film treatment layout required for 48HFP.
"""

from typing import List
from pydantic import BaseModel, Field


class TitleAndLogline(BaseModel):
    """Film title, genre blend, and logline."""

    title: str = Field(description="Working title of the short film")
    genre_blend: str = Field(
        description="Primary and secondary genre combination, e.g., 'Film Noir / Single Room Movie'"
    )
    logline: str = Field(
        description="1-2 sentence dramatic logline summarizing protagonist, conflict, and stakes"
    )


class CharacterRosterItem(BaseModel):
    """Detailed character specification for cast allocation."""

    name: str = Field(description="Character name")
    actor_or_traits: str = Field(description="Actor assigned or key physical/personality traits")
    role: str = Field(
        description="Role in story (e.g., Protagonist, Antagonist, Supporting, Cameo)"
    )
    is_required_character: bool = Field(
        default=False,
        description="True if this character satisfies the 48HFP required character constraint",
    )


class NarrativeSynopsis(BaseModel):
    """Three-act narrative structure and thematic arc."""

    act_1_setup: str = Field(
        description="Act I: Setup, world building, protagonist goal, and inciting incident"
    )
    act_2_escalation: str = Field(
        description="Act II: Complications, rising tension, midpoint shift, and obstacle escalation"
    )
    act_3_climax_resolution: str = Field(
        description="Act III: Dramatic climax, resolution, and emotional payoff"
    )
    thematic_arc: str = Field(description="Core theme and character motivation integration")


class SceneBreakdownItem(BaseModel):
    """Individual scene specification within the 4-7 minute pacing limit."""

    scene_number: int = Field(description="Sequential scene number (1, 2, 3...)")
    heading: str = Field(description="Scene heading, e.g., 'INT. CLOCK SHOP - NIGHT'")
    location: str = Field(description="Physical filming location")
    time_of_day: str = Field(description="Time of day (DAY, NIGHT, DUSK, DAWN)")
    characters_present: List[str] = Field(
        description="List of character names appearing in this scene"
    )
    action_summary: str = Field(description="Detailed visual action and pacing summary")
    props_used: List[str] = Field(
        description="Key props utilized in this scene, including any required prop"
    )


class DialogueSnippetItem(BaseModel):
    """Key dialogue beat snippet."""

    character: str = Field(description="Character speaking")
    line: str = Field(description="Dialogue text")
    is_required_line: bool = Field(
        default=False,
        description="True if this snippet contains or represents the verbatim 48HFP required dialogue line",
    )
    context_notes: str = Field(description="Dramatic context or delivery instructions")


class FestivalComplianceChecklist(BaseModel):
    """48HFP rule compliance verification checklist."""

    verbatim_line_verified: bool = Field(
        description="Confirmation that required line appears verbatim"
    )
    prop_usage_verified: bool = Field(
        description="Confirmation that required prop is visually used in action"
    )
    character_linkage_verified: bool = Field(
        description="Confirmation that required character name/trait matches"
    )
    pacing_runtime_verified: bool = Field(
        description="Confirmation that treatment fits 4-7 minute runtime"
    )
    compliance_notes: str = Field(
        description="Specific notes on how festival constraints were fulfilled"
    )


class TreatmentOutput(BaseModel):
    """Complete structured pre-production film treatment."""

    title_and_logline: TitleAndLogline
    character_roster: List[CharacterRosterItem]
    synopsis: NarrativeSynopsis
    scene_breakdown: List[SceneBreakdownItem]
    dialogue_snippets: List[DialogueSnippetItem]
    compliance_checklist: FestivalComplianceChecklist
