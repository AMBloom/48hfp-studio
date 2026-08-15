"""Asset Store and Pandas CSV Exporter/Importer for 48HFP-Studio Shot Lists.

Manages saving generated shot lists to local storage in CSV format using pandas,
enforcing cross-platform pathing, version zero-padding (e.g., v01, v02),
and safe-write non-overwrite guarantees.
"""

from datetime import datetime
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import pandas as pd

from studio.models.shotlist import ShotItem, ShotListBase
from studio.utils.global_state import get_workspace_root
from studio.utils.treatment_store import sanitize_filename_part


def get_next_shotlist_version_number(assets_dir: Path) -> int:
    """Scan assets directory for existing shotlists and compute next version number.

    Defaults safely to 1 if no shotlist CSV files exist or if directory is empty.
    """
    if not assets_dir.exists():
        return 1

    pattern = re.compile(r"^shotlist_v(\d+)_", re.IGNORECASE)
    versions: List[int] = []

    for file_path in assets_dir.glob("shotlist_v*.csv"):
        match = pattern.match(file_path.name)
        if match:
            try:
                versions.append(int(match.group(1)))
            except ValueError:
                continue

    if not versions:
        return 1

    return max(versions) + 1


def save_shotlist_csv(
    shotlist: ShotListBase,
    title: str = "Untitled",
    assets_dir: Optional[Path] = None,
) -> Path:
    """Safely export ShotListBase to CSV file using pandas with auto-incrementing zero-padded version.

    Target directory: `<workspace>/assets`
    Version format: shotlist_v01_<title>_<timestamp>.csv
    Safe-Write System: Ensures previous outputs are NEVER overwritten.
    """
    target_dir = assets_dir or (get_workspace_root() / "assets")
    target_dir.mkdir(parents=True, exist_ok=True)

    clean_title = sanitize_filename_part(title or shotlist.title or "Untitled")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    version = get_next_shotlist_version_number(target_dir)

    while True:
        version_str = f"v{version:02d}"
        filename = f"shotlist_{version_str}_{clean_title}_{timestamp}.csv"
        file_path = target_dir / filename

        if not file_path.exists():
            break
        version += 1

    # Convert Pydantic ShotItems into pandas DataFrame
    rows = []
    for s in shotlist.shots:
        cast_str = ", ".join(s.cast) if isinstance(s.cast, list) else str(s.cast or "")
        rows.append({
            "Shot": s.shot_number,
            "Scene": s.scene_number,
            "Location": s.location,
            "Setup": s.setup,
            "Shot Size": s.shot_size,
            "Camera Movement": s.camera_movement,
            "Cast": cast_str,
            "Description": s.description,
        })

    df = pd.DataFrame(
        rows,
        columns=[
            "Shot",
            "Scene",
            "Location",
            "Setup",
            "Shot Size",
            "Camera Movement",
            "Cast",
            "Description",
        ],
    )

    df.to_csv(file_path, index=False, encoding="utf-8")
    return file_path


def list_saved_shotlists(assets_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """Scan workspace assets/ directory and return list of shot list metadata dictionaries.

    Returns dicts with keys: 'filename', 'version', 'title', 'path', 'mtime', 'formatted_date'.
    Sorted by mtime descending (newest first).
    """
    target_dir = assets_dir or (get_workspace_root() / "assets")
    if not target_dir.exists():
        return []

    results: List[Dict[str, str]] = []
    pattern = re.compile(r"^shotlist_v(\d+)_(.+)_\d{8}_\d{6}\.csv$", re.IGNORECASE)

    for p in target_dir.glob("shotlist_v*.csv"):
        if not p.is_file():
            continue
        stat = p.stat()
        mtime = stat.st_mtime
        formatted_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

        match = pattern.match(p.name)
        if match:
            version_str = f"v{int(match.group(1)):02d}"
            raw_title = match.group(2).replace("_", " ")
        else:
            version_str = "v--"
            raw_title = p.stem

        results.append({
            "filename": p.name,
            "version": version_str,
            "title": raw_title,
            "path": str(p),
            "mtime": mtime,
            "formatted_date": formatted_date,
        })

    results.sort(key=lambda x: x["mtime"], reverse=True)
    return results


def load_shotlist_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Load and parse shot list CSV file using pandas into a list of row dictionaries for TUI DataTable consumption."""
    path_obj = Path(file_path)
    if not path_obj.exists():
        return []

    try:
        df = pd.read_csv(path_obj, dtype=str).fillna("")
    except Exception:
        return []

    expected_cols = [
        "Shot",
        "Scene",
        "Location",
        "Setup",
        "Shot Size",
        "Camera Movement",
        "Cast",
        "Description",
    ]

    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[expected_cols]
    return df.to_dict(orient="records")


def save_storyboard_image(
    image_bytes: bytes,
    shot_number: int,
    scene_number: str,
    storyboards_dir: Optional[Path] = None,
) -> Path:
    """Save storyboard image bytes to local storage in storyboards/ directory.

    Target directory: `<active_workspace>/storyboards`
    Filename format: `shot_{shot_number:03d}_scene_{scene_clean}.png`
    Auto-creates target directory if missing.
    """
    target_dir = storyboards_dir or (get_workspace_root() / "storyboards")
    target_dir.mkdir(parents=True, exist_ok=True)

    scene_clean = sanitize_filename_part(str(scene_number or "1"))
    filename = f"shot_{int(shot_number):03d}_scene_{scene_clean}.png"
    file_path = target_dir / filename

    file_path.write_bytes(image_bytes)
    return file_path

