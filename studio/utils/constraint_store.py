"""Storage utility for Logistical and Creative Constraint Sets using PyYAML."""

from pathlib import Path
from typing import List, Optional, Tuple
import yaml

from studio.models.constraints import (
    CharacterDetail,
    ConstraintType,
    CreativeConstraint,
    LogisticalConstraint,
)


def get_constraints_base_dir() -> Path:
    """Return constraints base path dynamically relative to current working directory."""
    return Path.cwd() / "constraints"


def get_logistical_dir() -> Path:
    """Return logistical constraints directory path."""
    return get_constraints_base_dir() / "logistical"


def get_creative_dir() -> Path:
    """Return creative constraints directory path."""
    return get_constraints_base_dir() / "creative"


def ensure_constraints_dirs() -> None:
    """Ensure constraint directories exist."""
    get_logistical_dir().mkdir(parents=True, exist_ok=True)
    get_creative_dir().mkdir(parents=True, exist_ok=True)


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


# --- Creative Constraints ---


def save_creative_constraint(constraint: CreativeConstraint) -> Path:
    """Save a CreativeConstraint object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_creative_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_creative_constraint(name: str) -> Optional[CreativeConstraint]:
    """Load a CreativeConstraint object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_creative_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return CreativeConstraint.model_validate(data)
    except Exception:
        return None


def list_creative_constraints() -> List[CreativeConstraint]:
    """List all available CreativeConstraint sets."""
    ensure_constraints_dirs()
    results: List[CreativeConstraint] = []
    for file_path in sorted(get_creative_dir().glob("*.yaml")):
        c = load_creative_constraint(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_creative_constraint(name: str) -> bool:
    """Delete a CreativeConstraint set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_creative_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Seeding Defaults ---


def seed_default_constraints() -> Tuple[Optional[Path], Optional[Path]]:
    """Seed default starter logistical and creative constraint sets if none exist."""
    ensure_constraints_dirs()
    logistical_path = None
    creative_path = None

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

    if not list_creative_constraints():
        default_creative = CreativeConstraint(
            name="a24_slow_burn",
            description="A24-style indie psychological drama with deliberate pacing and lingering shots.",
            scenarios=[
                "Two long-lost friends reunite under suspicious circumstances during a power outage.",
                "A tense dinner party where unspoken secrets gradually unravel.",
            ],
            core_philosophy="Tension through silence, spatial intimacy, and understated subtext.",
            scene_economy="Long static takes, minimal cuts, letting dialogue breath with natural pauses.",
            progression_and_climax="Subtle character escalation building to a quiet, high-stakes emotional confrontation.",
            visuals_and_post="Desaturated warm tones, soft directional lighting, ambient acoustic score with subtle synth drones.",
        )
        creative_path = save_creative_constraint(default_creative)

    return logistical_path, creative_path
