"""Pydantic model for global team configuration profile."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


def current_iso_timestamp() -> str:
    """Return current ISO 8601 formatted timestamp string."""
    return datetime.now().isoformat()


class TeamProfile(BaseModel):
    """Global state representing the production team configuration."""

    team_name: str = Field(..., description="Name of the 48HFP production team")
    admin_username: str = Field(..., description="Primary user/admin username")
    location: str = Field(..., description="Production team location (e.g. City, Country)")
    roles: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Team members grouped by role (e.g. Director, Producer, DP, Actors, etc.)",
    )
    custom_details: Optional[str] = Field(
        default="",
        description="Open text field for dietary restrictions, vehicle availability, equipment, etc.",
    )
    active_logistical_constraint: Optional[str] = Field(
        default=None,
        description="Name of currently active Logistical Constraint Set",
    )
    active_creative_constraint: Optional[str] = Field(
        default=None,
        description="Name of currently active Creative Constraint Set",
    )
    created_at: str = Field(default_factory=current_iso_timestamp)
    updated_at: str = Field(default_factory=current_iso_timestamp)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to now."""
        self.updated_at = current_iso_timestamp()
