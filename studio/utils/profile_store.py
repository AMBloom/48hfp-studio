"""Persistence logic for global team configuration profile using PyYAML."""

from pathlib import Path
from typing import Optional
import yaml

from studio.models.profile import TeamProfile

DEFAULT_PROFILE_PATH = Path.home() / ".48hfp_profile.yaml"


def get_profile_path() -> Path:
    """Return the persistent profile file path."""
    return DEFAULT_PROFILE_PATH


def profile_exists(path: Optional[Path] = None) -> bool:
    """Check if the profile file exists and is a file."""
    p = path or get_profile_path()
    return p.exists() and p.is_file()


def load_profile(path: Optional[Path] = None) -> Optional[TeamProfile]:
    """Load and validate the TeamProfile from YAML.

    Returns None if file does not exist or fails validation.
    """
    p = path or get_profile_path()
    if not p.exists():
        return None

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return TeamProfile.model_validate(data)
    except Exception as err:
        # Logging or handling corrupted profile
        return None


def save_profile(profile: TeamProfile, path: Optional[Path] = None) -> Path:
    """Save the TeamProfile to YAML at the specified path."""
    p = path or get_profile_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    profile.update_timestamp()
    data = profile.model_dump()

    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return p
