"""Pydantic schemas for Logistical and Creative Constraint Sets."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


def current_iso_timestamp() -> str:
    """Return current ISO 8601 formatted timestamp string."""
    return datetime.now().isoformat()


class ConstraintType(str, Enum):
    """Supported constraint set categories."""

    LOGISTICAL = "logistical"
    CREATIVE = "creative"


class CharacterDetail(BaseModel):
    """Details for a specific character in a logistical set."""

    name: str = Field(..., description="Character name or role title")
    actor_traits: Optional[str] = Field(default="", description="Actor traits, age, gender, appearance")
    wardrobe: Optional[str] = Field(default="", description="Wardrobe or costume notes")
    notes: Optional[str] = Field(default="", description="Personality, motives, or specific acting notes")


class LogisticalConstraint(BaseModel):
    """User-defined Logistical Constraint Set representing physical shoot reality."""

    name: str = Field(..., description="Unique slug identifier (e.g. interior_indie_crew)")
    description: str = Field(default="", description="Brief summary of this logistical setup")
    locations: List[str] = Field(
        default_factory=list,
        description="Filming locations (e.g. Interior, Restaurant, Night)",
    )
    sub_locations: List[str] = Field(
        default_factory=list,
        description="Sub-locations (e.g. Dining Room, Kitchen, Restroom, Parking Lot)",
    )
    location_details: str = Field(
        default="",
        description="Layout, lighting availability, spatial restrictions, noise levels",
    )
    main_character_details: Optional[CharacterDetail] = Field(
        default=None,
        description="Specific actor traits/wardrobe extending the required character",
    )
    other_characters: List[CharacterDetail] = Field(
        default_factory=list,
        description="Additional available cast and character traits",
    )
    props_and_dialogue: List[str] = Field(
        default_factory=list,
        description="Available set dressing, props, running jokes, or specific dialogue hooks",
    )
    created_at: str = Field(default_factory=current_iso_timestamp)
    updated_at: str = Field(default_factory=current_iso_timestamp)

    @field_validator("name")
    @classmethod
    def validate_name_slug(cls, v: str) -> str:
        """Ensure name is valid slug format."""
        slug = v.strip().lower().replace(" ", "_")
        if not slug:
            raise ValueError("Constraint name cannot be empty")
        return slug

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = current_iso_timestamp()


class CreativeConstraint(BaseModel):
    """User-defined Creative Constraint Set enforcing directorial and narrative vision."""

    name: str = Field(..., description="Unique slug identifier (e.g. a24_slow_burn)")
    description: str = Field(default="", description="Brief summary of this creative set")
    scenarios: List[str] = Field(
        default_factory=list,
        description="Partially baked short story scenario descriptions",
    )
    core_philosophy: str = Field(
        default="",
        description="Thematic spine and directorial motivation",
    )
    scene_economy: str = Field(
        default="",
        description="Pacing directives (e.g. long takes, frantic cuts, minimal dialogue)",
    )
    progression_and_climax: str = Field(
        default="",
        description="Narrative structure guidelines, emotional arc, and climax dynamics",
    )
    visuals_and_post: str = Field(
        default="",
        description="Color grading intent, scoring style, aspect ratio, VFX limits",
    )
    created_at: str = Field(default_factory=current_iso_timestamp)
    updated_at: str = Field(default_factory=current_iso_timestamp)

    @field_validator("name")
    @classmethod
    def validate_name_slug(cls, v: str) -> str:
        """Ensure name is valid slug format."""
        slug = v.strip().lower().replace(" ", "_")
        if not slug:
            raise ValueError("Constraint name cannot be empty")
        return slug

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = current_iso_timestamp()
