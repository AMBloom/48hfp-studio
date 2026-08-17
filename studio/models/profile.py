"""Pydantic model for global team configuration profile."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


def current_iso_timestamp() -> str:
    """Return current ISO 8601 formatted timestamp string."""
    return datetime.now().isoformat()


class TeamProfile(BaseModel):
    """Global state representing the production team configuration."""

    team_name: str = Field(..., description="Name of the 48HFP production team")
    admin_username: str = Field(..., description="Primary user/admin username")
    location: str = Field(..., description="Production team location (e.g. City, Country)")
    crew: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Crew members grouped by role (e.g. Director, Producer, DP, etc.)",
    )
    cast: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Actor details with keys: name, age_range, gender, ethnicity, hair, build, visual_anchor, physicality",
    )
    available_gear: List[str] = Field(
        default_factory=list,
        description="Catalog of available filmmaking assets and gear",
    )
    custom_details: Optional[str] = Field(
        default="",
        description="Open text field for dietary restrictions, vehicle availability, equipment, etc.",
    )
    active_logistical_constraint: Optional[str] = Field(
        default=None,
        description="Name of currently active Logistical Constraint Set",
    )
    active_directorial_vision: Optional[str] = Field(
        default=None,
        description="Name of currently active Directorial Vision Constraint Set",
    )
    active_thematic_framework: Optional[str] = Field(
        default=None,
        description="Name of currently active Thematic Framework Constraint Set",
    )
    active_idea_seed: Optional[str] = Field(
        default=None,
        description="Name of currently active Idea Seed Constraint Set",
    )
    created_at: str = Field(default_factory=current_iso_timestamp)
    updated_at: str = Field(default_factory=current_iso_timestamp)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_fields(cls, data: Any) -> Any:
        """Migrate legacy roles and cast format."""
        if isinstance(data, dict):
            if "roles" in data and "crew" not in data:
                data["crew"] = data.pop("roles")
            if "cast" in data and isinstance(data["cast"], list):
                migrated_cast = []
                for item in data["cast"]:
                    if isinstance(item, dict):
                        c = dict(item)
                        c.setdefault("ethnicity", "Unspecified")
                        c.setdefault("hair", "Unspecified")
                        c.setdefault("build", "Unspecified")
                        c.setdefault("visual_anchor", "None")
                        if "physicality" not in c:
                            parts = [c["ethnicity"], c["hair"], c["build"]]
                            c["physicality"] = ", ".join([p for p in parts if p != "Unspecified"]) or "Unspecified"
                        migrated_cast.append(c)
                data["cast"] = migrated_cast
        return data


    @property
    def roles(self) -> Dict[str, List[str]]:
        """Backward compatibility property returning crew."""
        return self.crew

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to now."""
        self.updated_at = current_iso_timestamp()
