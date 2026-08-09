"""Storage utility for Logistical, Directorial, Thematic, and Idea Constraint Sets using PyYAML."""

from pathlib import Path
from typing import List, Optional, Tuple
import yaml

from studio.models.constraints import (
    CharacterDetail,
    ConstraintType,
    DirectorialVision,
    IdeaSeed,
    LogisticalConstraint,
    ThematicFramework,
)


def get_constraints_base_dir() -> Path:
    """Return constraints base path dynamically relative to current working directory."""
    return Path.cwd() / "constraints"


def get_logistical_dir() -> Path:
    """Return logistical constraints directory path."""
    return get_constraints_base_dir() / "logistical"


def get_directorial_dir() -> Path:
    """Return directorial vision constraints directory path."""
    return get_constraints_base_dir() / "directorial"


def get_thematic_dir() -> Path:
    """Return thematic framework constraints directory path."""
    return get_constraints_base_dir() / "thematic"


def get_ideas_dir() -> Path:
    """Return idea seeds constraints directory path."""
    return get_constraints_base_dir() / "ideas"


def ensure_constraints_dirs() -> None:
    """Ensure constraint directories exist."""
    get_logistical_dir().mkdir(parents=True, exist_ok=True)
    get_directorial_dir().mkdir(parents=True, exist_ok=True)
    get_thematic_dir().mkdir(parents=True, exist_ok=True)
    get_ideas_dir().mkdir(parents=True, exist_ok=True)


# --- Logistical Constraints ---


def save_logistical_constraint(constraint: LogisticalConstraint) -> Path:
    """Save a LogisticalConstraint object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_logistical_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_logistical_constraint(name: str) -> Optional[LogisticalConstraint]:
    """Load a LogisticalConstraint object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_logistical_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return LogisticalConstraint.model_validate(data)
    except Exception:
        return None


def list_logistical_constraints() -> List[LogisticalConstraint]:
    """List all available LogisticalConstraint sets."""
    ensure_constraints_dirs()
    results: List[LogisticalConstraint] = []
    for file_path in sorted(get_logistical_dir().glob("*.yaml")):
        c = load_logistical_constraint(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_logistical_constraint(name: str) -> bool:
    """Delete a LogisticalConstraint set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_logistical_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Directorial Vision Constraints ---


def save_directorial_vision(constraint: DirectorialVision) -> Path:
    """Save a DirectorialVision object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_directorial_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_directorial_vision(name: str) -> Optional[DirectorialVision]:
    """Load a DirectorialVision object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_directorial_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return DirectorialVision.model_validate(data)
    except Exception:
        return None


def list_directorial_visions() -> List[DirectorialVision]:
    """List all available DirectorialVision sets."""
    ensure_constraints_dirs()
    results: List[DirectorialVision] = []
    for file_path in sorted(get_directorial_dir().glob("*.yaml")):
        c = load_directorial_vision(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_directorial_vision(name: str) -> bool:
    """Delete a DirectorialVision set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_directorial_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Thematic Framework Constraints ---


def save_thematic_framework(constraint: ThematicFramework) -> Path:
    """Save a ThematicFramework object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_thematic_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_thematic_framework(name: str) -> Optional[ThematicFramework]:
    """Load a ThematicFramework object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_thematic_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return ThematicFramework.model_validate(data)
    except Exception:
        return None


def list_thematic_frameworks() -> List[ThematicFramework]:
    """List all available ThematicFramework sets."""
    ensure_constraints_dirs()
    results: List[ThematicFramework] = []
    for file_path in sorted(get_thematic_dir().glob("*.yaml")):
        c = load_thematic_framework(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_thematic_framework(name: str) -> bool:
    """Delete a ThematicFramework set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_thematic_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Idea Seed Constraints ---


def save_idea_seed(constraint: IdeaSeed) -> Path:
    """Save an IdeaSeed object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_ideas_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_idea_seed(name: str) -> Optional[IdeaSeed]:
    """Load an IdeaSeed object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_ideas_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return IdeaSeed.model_validate(data)
    except Exception:
        return None


def list_idea_seeds() -> List[IdeaSeed]:
    """List all available IdeaSeed sets."""
    ensure_constraints_dirs()
    results: List[IdeaSeed] = []
    for file_path in sorted(get_ideas_dir().glob("*.yaml")):
        c = load_idea_seed(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_idea_seed(name: str) -> bool:
    """Delete an IdeaSeed set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_ideas_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Seeding Defaults ---


def seed_default_constraints() -> Tuple[Optional[Path], Optional[Path], Optional[Path], Optional[Path]]:
    """Seed default starter constraint sets for all categories if none exist."""
    ensure_constraints_dirs()
    logistical_path = None
    directorial_path = None
    thematic_path = None
    ideas_path = None

    if not list_logistical_constraints():
        default_logistical = LogisticalConstraint(
            name="interior_indie_crew",
            description="Default indoor indie shoot setup with a small crew and kitchen/living room locations.",
            locations=["Interior", "Apartment", "Day/Night"],
            sub_locations=["Living Room", "Kitchen", "Hallway", "Balcony"],
            location_details="Natural daylight through living room windows. Kitchen equipped with island counter and fluorescent overheads.",
            main_character_details=CharacterDetail(
                name="Protagonist",
                actor_traits="Late 20s - Early 30s, expressive eyes, casual clothing",
                wardrobe="Faded denim jacket, graphic tee, sneakers",
                notes="Resourceful but anxious under pressure",
            ),
            other_characters=[
                CharacterDetail(
                    name="Eclectic Neighbor",
                    actor_traits="40s, eccentric posture, loud voice",
                    wardrobe="Bright bathrobe or oversized vintage cardigan",
                    notes="Provides unexpected plot exposition",
                )
            ],
            props_and_dialogue=[
                "Vintage coffee mug",
                "Flickering table lamp",
                "Unopened letter on kitchen counter",
                "Running Joke: 'Did anyone actually remember the coffee?'",
            ],
        )
        logistical_path = save_logistical_constraint(default_logistical)

    if not list_directorial_visions():
        default_directorial = DirectorialVision(
            name="a24_slow_burn",
            description="A24-style indie psychological drama with deliberate pacing and lingering shots.",
            visual_economy="Long static takes, minimal cuts, letting dialogue breath with natural pauses.",
            lighting_color="Desaturated warm tones, soft directional lighting, moody shadows.",
            audio_landscape="Ambient acoustic score with subtle synth drones and naturalistic room tone.",
        )
        directorial_path = save_directorial_vision(default_directorial)

    if not list_thematic_frameworks():
        default_thematic = ThematicFramework(
            name="existential_dread",
            description="Explores human isolation, fragile connections, and unspoken secrets.",
            core_philosophy="Tension through silence, spatial intimacy, and understated subtext.",
            emotional_arc="Subtle character escalation building to a quiet, high-stakes emotional confrontation.",
            world_rules="Claustrophobic domestic realism where small daily choices carry overwhelming weight.",
        )
        thematic_path = save_thematic_framework(default_thematic)

    if not list_idea_seeds():
        default_idea = IdeaSeed(
            name="late_night_visitor",
            description="An unexpected arrival disrupts a fragile quiet night.",
            inciting_incident="Two long-lost acquaintances reunite under suspicious circumstances during a citywide power outage.",
            complications="A lost key, hidden motives, and a sudden knock at the back door.",
            ending_targets="A tense standoff resolving in an unexpected gesture of forgiveness.",
        )
        ideas_path = save_idea_seed(default_idea)

    return logistical_path, directorial_path, thematic_path, ideas_path

