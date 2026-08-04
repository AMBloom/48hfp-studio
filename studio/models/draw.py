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

FALLBACK_NAMES: List[str] = [
    "Michael / Michelle",
    "Colin / Coleen",
    "Dan / Danielle",
    "Sam / Samantha",
    "Alex / Alexa",
    "Aaron / Erin",
    "Gabriel / Gabrielle",
    "Julian / Julianne",
    "Oliver / Olivia",
    "Adrian / Adriana",
    "Paul / Paula",
    "Chris / Christine",
    "Victor / Victoria",
    "Jesse / Jessica",
    "Martin / Martina",
    "Simon / Simone",
    "Eric / Erica",
    "Brian / Brianna",
    "Carl / Carla",
    "Justin / Justine",
    "Stephen / Stephanie",
    "Andrew / Andrea",
    "Christian / Christina",
    "Leo / Leona",
    "Gene / Jean",
]

FALLBACK_TRAITS: List[str] = [
    "Commuter",
    "Customer",
    "Tourist",
    "Office worker",
    "Passerby",
    "Realtor",
    "Mediator",
    "Doctor",
    "First Responder",
    "Musician",
    "Driver",
    "Teacher",
    "Priest / Clergy",
    "Engineer",
    "Decorator",
    "Curator",
    "Writer",
    "Investor / Banker",
    "Politician",
    "Zookeeper",
    "Mechanic",
    "Locksmith",
    "Beautician / Stylist",
    "Athlete",
    "Hero",
    "Psychologist",
    "Chef / Waitstaff / Bartender",
    "Criminal / Outlaw",
    "Celebrity",
    "Salesperson",
    "Startup Founder",
    "Delivery Courier",
    "HOA Treasurer",
    "Watchmaker",
    "Dog Walker",
    "Data Analyst",
    "Night Watchman",
    "Podcast Host",
    "Librarian",
]

FALLBACK_PROPS: List[str] = [
    "Mirror",
    "Tape",
    "Pliers",
    "Hat",
    "Banana",
    "Pencil",
    "Trophy",
    "Umbrella",
    "Key",
    "Alarm clock",
    "Rubber band",
    "Paper clip",
    "The number 25",
    "Soda can",
    "USB thumb drive",
    "Coffee mug",
    "Flashlight",
    "Deck of cards",
    "Chess pawn",
    "Cast iron skillet",
    "Wristwatch",
    "Leather jacket",
    "Dog leash",
    "Sunglasses",
    "Receipt",
    "Coin",
    "Apple",
    "Towel",
    "Backpack",
    "Headphones",
]

FALLBACK_LINES: List[str] = [
    "Look what I did.",
    "Why do you ask?",
    "Don't tell anyone.",
    "Let me know when it's ready.",
    "Let me know when it is ready.",
    "There's no 'I' in 'Team'.",
    "I did not see that coming.",
    "Can you tell me what just happened?",
    "I'll take it from here.",
    "That's how you do it.",
    "I've got a bad feeling about this.",
    "I can't believe it.",
    "I'm ready for anything.",
    "I'm switching it up.",
    "This is going way too fast for me.",
    "Do you understand and accept these risks?",
    "Your mileage may vary.",
    "It's not you, it's me.",
    "It's not me, it's you.",
    "This explains everything.",
    "It's a long story.",
    "Does the Pope shit in the woods?",
    "Well that didn't pan out.",
    "That was worth the wait.",
    "It insists upon itself.",
    "Have a seat.",
    "It doesn't look like anything to me.",
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

    @field_validator("required_line")
    @classmethod
    def validate_required_line(cls, v: str) -> str:
        """Strip whitespace and surrounding single or double quotes from required_line."""
        clean_val = v.strip().strip('"\'').strip()
        if not clean_val:
            raise ValueError("Required line cannot be empty")
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

    c_name = character_name.strip() if character_name and character_name.strip() else random.choice(FALLBACK_NAMES)
    c_trait = character_trait.strip() if character_trait and character_trait.strip() else random.choice(FALLBACK_TRAITS)
    c_gender = character_gender.strip() if character_gender and character_gender.strip() else "Male or Female"
    prop = required_prop.strip() if required_prop and required_prop.strip() else random.choice(FALLBACK_PROPS)
    line = required_line.strip().strip('"\'').strip() if required_line and required_line.strip() else random.choice(FALLBACK_LINES)

    return FridayDraw(
        genre_1=g1,
        genre_2=g2,
        character_name=c_name,
        character_trait=c_trait,
        character_gender=c_gender,
        required_prop=prop,
        required_line=line,
    )
