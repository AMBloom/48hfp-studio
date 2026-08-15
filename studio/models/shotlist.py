"""Shot List output schema models for 48HFP-Studio.

Represents a structured, scene-by-scene StudioBinder-style shot list breakdown required for pre-production.
"""

from typing import List
from pydantic import BaseModel, Field


class ShotItem(BaseModel):
    """Individual camera shot specification in StudioBinder shot list breakdown."""

    shot_number: int = Field(description="Sequential shot number (1, 2, 3...)")
    scene_number: str = Field(description="Scene heading or scene number (e.g. '1' or 'INT. CLOCK SHOP - NIGHT')")
    location: str = Field(description="Physical filming location")
    setup: str = Field(description="Camera setup identifier (e.g. 'Setup A - Counter')")
    shot_size: str = Field(description="Framing / shot size (e.g. ECU, CU, MCU, MS, WS, EWS)")
    camera_movement: str = Field(description="Camera movement or angle (e.g. Static, Pan Left, Dolly In, Handheld)")
    cast: List[str] = Field(default_factory=list, description="Cast members featured in this shot")
    description: str = Field(description="Visual action, framing, focal point, and story beat description")


class ShotListBase(BaseModel):
    """Complete structured shot list breakdown payload."""

    title: str = Field(default="Untitled", description="Working title of the short film")
    shots: List[ShotItem] = Field(default_factory=list, description="Ordered list of visual camera shots")
