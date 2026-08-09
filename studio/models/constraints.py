"""Pydantic schemas for Logistical and Creative Constraint Sets."""

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


def current_iso_timestamp() -> str:
    """Return current ISO 8601 formatted timestamp string."""
    return datetime.now().isoformat()


class ConstraintType(str, Enum):
    """Supported constraint set categories."""

    LOGISTICAL = "logistical"
    DIRECTORIAL = "directorial"
    THEMATIC = "thematic"
    IDEA = "idea"


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
    other_characters: List[CharacterDetail] = Field(
        default_factory=list,
        description="Additional available cast and character traits",
    )
    available_set_dressing: List[str] = Field(
        default_factory=list,
        description="Available set dressing, wardrobe, props, running jokes, or specific dialogue hooks",
    )
    created_at: str = Field(default_factory=current_iso_timestamp)
    updated_at: str = Field(default_factory=current_iso_timestamp)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_logistical_fields(cls, data: Any) -> Any:
        """Migrate legacy 'props_and_dialogue' to 'available_set_dressing' and strip obsolete fields."""
        if isinstance(data, dict):
            if "props_and_dialogue" in data and "available_set_dressing" not in data:
                data["available_set_dressing"] = data.pop("props_and_dialogue")
            if "main_character_details" in data:
                data.pop("main_character_details", None)
        return data

    @property
    def props_and_dialogue(self) -> List[str]:
        """Backward compatibility property returning available_set_dressing."""
        return self.available_set_dressing

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


class DirectorialVision(BaseModel):
    """User-defined Directorial Vision constraint set (visuals, lighting, audio)."""

    name: str = Field(..., description="Unique slug identifier (e.g. a24_slow_burn)")
    description: str = Field(default="", description="Brief summary of this directorial vision")
    visual_economy: str = Field(
        default="",
        description="Visual pacing, shot design, camera movement, scene economy",
    )
    lighting_color: str = Field(
        default="",
        description="Lighting mood, color palette, post-production color grading intent",
    )
    audio_landscape: str = Field(
        default="",
        description="Scoring intent, sound design, music genres, audio motifs",
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


class ThematicFramework(BaseModel):
    """User-defined Thematic Framework constraint set (philosophy, emotional arc, world rules)."""

    name: str = Field(..., description="Unique slug identifier (e.g. existential_dread)")
    description: str = Field(default="", description="Brief summary of this thematic framework")
    core_philosophy: str = Field(
        default="",
        description="Thematic spine, core message, directorial motivation",
    )
    emotional_arc: str = Field(
        default="",
        description="Character emotional trajectory, tone shifts, climax dynamics",
    )
    world_rules: str = Field(
        default="",
        description="Internal narrative logic, world rules, atmospheric constraints",
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


class IdeaSeed(BaseModel):
    """User-defined Idea Seed constraint set (inciting incident, complications, ending targets)."""

    name: str = Field(..., description="Unique slug identifier (e.g. late_night_visitor)")
    description: str = Field(default="", description="Brief summary of this idea seed")
    inciting_incident: str = Field(
        default="",
        description="Initial spark, disruption, or story setup",
    )
    complications: str = Field(
        default="",
        description="Obstacles, twists, escalating stakes, mid-point friction",
    )
    ending_targets: str = Field(
        default="",
        description="Resolution direction, twist ending, or final emotional lingering note",
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

