"""Pydantic schema and constants for the Friday Night Draw kickoff data."""

from datetime import datetime
import random
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

GENRES_GROUP_1: List[str] = [
    "Action / Adventure",
    "Comedy",
    "Dark Comedy",
    "Drama",
    "Fantasy",
    "Film de Femme",
    "Film Noir",
    "Fish Out of Water",
    "Horror",
    "Mockumentary",
    "Musical",
    "Road Movie",
    "Romance",
    "Sci Fi",
    "Thriller / Suspense",
]

GENRES_GROUP_2: List[str] = [
    "Buddy Film",
    "Family Film",
    "Food Film",
    "Heist",
    "Inspirational Film",
    "Misunderstanding",
    "Moral Dilemma",
    "Revenge",
    "Romantic Comedy",
    "Silent Film",
    "Single Room Movie",
    "Sports Film / Game Film",
    "Utopian or Dystopian",
    "Vacation / Holiday Film",
    "Workplace Film",
]


def current_iso_timestamp() -> str:
    """Return current ISO 8601 formatted timestamp string."""
    return datetime.now().isoformat()


class FridayDraw(BaseModel):
    """Ephemeral Friday Night Draw kickoff parameters."""

    genre_1: str = Field(..., description="Selected primary genre from Group 1 pool")
    genre_2: str = Field(..., description="Selected secondary genre from Group 2 pool")
    character_name: str = Field(..., description="Required character name")
    character_trait: str = Field(..., description="Required character trait / profession")
    character_gender: str = Field(default="Any / Unspecified", description="Required character gender or sex")
    required_prop: str = Field(..., description="Required physical prop description")
    required_line: str = Field(..., description="Required verbatim line of dialogue")
    created_at: str = Field(default_factory=current_iso_timestamp)

    @field_validator("genre_1")
    @classmethod
    def validate_genre_1(cls, v: str) -> str:
        """Ensure genre_1 is in Group 1 pool or matches case-insensitively."""
        clean_val = v.strip()
        matched = next((g for g in GENRES_GROUP_1 if g.lower() == clean_val.lower()), None)
        if matched:
            return matched
        # If custom string or non-exact match, ensure it's non-empty
        if not clean_val:
            raise ValueError("Genre 1 cannot be empty")
        return clean_val

    @field_validator("genre_2")
    @classmethod
    def validate_genre_2(cls, v: str) -> str:
        """Ensure genre_2 is in Group 2 pool or matches case-insensitively."""
        clean_val = v.strip()
        matched = next((g for g in GENRES_GROUP_2 if g.lower() == clean_val.lower()), None)
        if matched:
            return matched
        if not clean_val:
            raise ValueError("Genre 2 cannot be empty")
        return clean_val


def create_default_draw(
    genre_1: Optional[str] = None,
    genre_2: Optional[str] = None,
    character_name: Optional[str] = None,
    character_trait: Optional[str] = None,
    character_gender: Optional[str] = None,
    required_prop: Optional[str] = None,
    required_line: Optional[str] = None,
) -> FridayDraw:
    """Generate a valid FridayDraw instance, applying fallback placeholders for blank fields."""
    g1 = genre_1.strip() if genre_1 and genre_1.strip() else random.choice(GENRES_GROUP_1)
    g2 = genre_2.strip() if genre_2 and genre_2.strip() else random.choice(GENRES_GROUP_2)

    c_name = character_name.strip() if character_name and character_name.strip() else "Alex Vance"
    c_trait = character_trait.strip() if character_trait and character_trait.strip() else "Clockmaker / Obsessive"
    c_gender = character_gender.strip() if character_gender and character_gender.strip() else "Male or Female"
    prop = required_prop.strip() if required_prop and required_prop.strip() else "An antique brass pocket watch"
    line = required_line.strip() if required_line and required_line.strip() else "We only have five minutes before the tide comes in."

    return FridayDraw(
        genre_1=g1,
        genre_2=g2,
        character_name=c_name,
        character_trait=c_trait,
        character_gender=c_gender,
        required_prop=prop,
        required_line=line,
    )
