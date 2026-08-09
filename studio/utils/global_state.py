"""Global state manager tracking persistent application configuration and active workspace."""

from pathlib import Path
from typing import Optional
import yaml


GLOBAL_STATE_DIR = Path.home() / ".48hfp"
GLOBAL_STATE_FILE = GLOBAL_STATE_DIR / "global_state.yaml"


def get_global_state_path() -> Path:
    """Return the absolute path to the global state tracker YAML file."""
    return GLOBAL_STATE_FILE


def get_active_workspace() -> Optional[Path]:
    """Retrieve the currently active workspace path from global state.

    Returns resolved Path if configured and directory exists; otherwise None.
    """
    p = get_global_state_path()
    if not p.is_file():
        return None

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None

        ws_str = data.get("active_workspace_path")
        if not ws_str:
            return None

        ws_path = Path(ws_str).resolve()
        if ws_path.exists() and ws_path.is_dir():
            return ws_path
        return None
    except Exception:
        return None


def set_active_workspace(workspace_path: Path) -> Path:
    """Set the active workspace path in global state tracker (~/.48hfp/global_state.yaml)."""
    resolved_path = workspace_path.resolve()
    resolved_path.mkdir(parents=True, exist_ok=True)

    state_file = get_global_state_path()
    state_file.parent.mkdir(parents=True, exist_ok=True)

    data = {"active_workspace_path": str(resolved_path)}
    with open(state_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    return resolved_path


def clear_active_workspace() -> None:
    """Clear active workspace tracking in global state tracker."""
    state_file = get_global_state_path()
    if state_file.is_file():
        data = {"active_workspace_path": None}
        with open(state_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def get_workspace_root() -> Path:
    """High-level path resolver returning active workspace path if set, else falling back to CWD."""
    active = get_active_workspace()
    if active is not None:
        return active
    return Path.cwd()
