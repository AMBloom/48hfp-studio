"""Persistence utilities for saving and loading Friday Draw kickoff data."""

from pathlib import Path
from typing import Optional
import yaml

from studio.models.draw import FridayDraw
from studio.utils.global_state import get_active_workspace, get_workspace_root

LEGACY_DRAW_PATH = Path.home() / ".48hfp_draw.yaml"


def get_draw_path() -> Path:
    """Return path to Friday Draw storage YAML file relative to active workspace or fallback."""
    active = get_active_workspace()
    if active:
        return active / "draw.yaml"

    ws_root = get_workspace_root()
    ws_draw = ws_root / "draw.yaml"
    if ws_draw.exists():
        return ws_draw

    if LEGACY_DRAW_PATH.exists():
        return LEGACY_DRAW_PATH

    return ws_draw


def draw_exists() -> bool:
    """Check whether a saved Friday Draw configuration file exists."""
    return get_draw_path().is_file()


def load_draw() -> Optional[FridayDraw]:
    """Load and validate FridayDraw from persistent YAML storage."""
    path = get_draw_path()
    if not path.is_file():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return FridayDraw(**data)
    except Exception:
        return None


def save_draw(draw: FridayDraw) -> Path:
    """Save FridayDraw instance to persistent YAML file (~/.48hfp_draw.yaml)."""
    path = get_draw_path()
    data = draw.model_dump()

    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)

    return path


def delete_draw() -> bool:
    """Delete the saved Friday Draw file if it exists."""
    path = get_draw_path()
    if path.is_file():
        path.unlink()
        return True
    return False
