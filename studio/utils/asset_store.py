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
    """Scan directory for existing shotlists and compute next version number.

    Supports encapsulated format (shotlist_v01.csv) and legacy format (shotlist_v01_...csv).
    Defaults safely to 1 if no shotlist CSV files exist or if directory is empty.
    """
    if not assets_dir.exists():
        return 1

    encapsulated_pattern = re.compile(r"^shotlist_v(\d+)\.csv$", re.IGNORECASE)
    legacy_pattern = re.compile(r"^shotlist_v(\d+)_", re.IGNORECASE)
    versions: List[int] = []

    for file_path in assets_dir.glob("shotlist_v*.csv"):
        enc_match = encapsulated_pattern.match(file_path.name)
        if enc_match:
            try:
                versions.append(int(enc_match.group(1)))
                continue
            except ValueError:
                pass
        leg_match = legacy_pattern.match(file_path.name)
        if leg_match:
            try:
                versions.append(int(leg_match.group(1)))
            except ValueError:
                continue

    if not versions:
        return 1

    return max(versions) + 1


def save_shotlist_csv(
    shotlist: ShotListBase,
    title: str = "Untitled",
    assets_dir: Optional[Path] = None,
    project_dir: Optional[Path] = None,
) -> Path:
    """Safely export ShotListBase to CSV file using pandas with auto-incrementing zero-padded version.

    Default target: `<workspace_root>/projects/<Clean_Project_Title>/shotlist_v01.csv`.
    If `assets_dir` is explicitly supplied, preserves flat output for backward compatibility.
    Safe-Write System: Ensures previous outputs are NEVER overwritten.
    """
    clean_title = sanitize_filename_part(title or shotlist.title or "Untitled")

    if assets_dir is not None:
        target_dir = assets_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        version = get_next_shotlist_version_number(target_dir)

        while True:
            version_str = f"v{version:02d}"
            filename = f"shotlist_{version_str}_{clean_title}_{timestamp}.csv"
            file_path = target_dir / filename

            if not file_path.exists():
                break
            version += 1
    else:
        target_dir = project_dir or (get_workspace_root() / "projects" / clean_title)
        target_dir.mkdir(parents=True, exist_ok=True)

        version = get_next_shotlist_version_number(target_dir)

        while True:
            version_str = f"v{version:02d}"
            filename = f"shotlist_{version_str}.csv"
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
    """Scan workspace for saved shot lists and return list of shot list metadata dictionaries.

    Discovers shot lists from both legacy flat directories and encapsulated project folders.
    Returns dicts with keys: 'filename', 'version', 'title', 'path', 'mtime', 'formatted_date'.
    Sorted by mtime descending (newest first).
    """
    candidate_paths: List[Path] = []

    if assets_dir is not None:
        if assets_dir.exists():
            candidate_paths.extend(assets_dir.glob("shotlist_v*.csv"))
    else:
        ws_root = get_workspace_root()
        legacy_dir = ws_root / "assets"
        if legacy_dir.exists():
            candidate_paths.extend(legacy_dir.glob("shotlist_v*.csv"))

        projects_dir = ws_root / "projects"
        if projects_dir.exists():
            candidate_paths.extend(projects_dir.glob("*/shotlist_v*.csv"))

    results: List[Dict[str, str]] = []
    seen_paths = set()
    legacy_pattern = re.compile(r"^shotlist_v(\d+)_(.+)_\d{8}_\d{6}\.csv$", re.IGNORECASE)
    encapsulated_pattern = re.compile(r"^shotlist_v(\d+)\.csv$", re.IGNORECASE)

    for p in candidate_paths:
        if not p.is_file() or str(p.resolve()) in seen_paths:
            continue
        seen_paths.add(str(p.resolve()))

        stat = p.stat()
        mtime = stat.st_mtime
        formatted_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

        leg_match = legacy_pattern.match(p.name)
        enc_match = encapsulated_pattern.match(p.name)

        if leg_match:
            version_str = f"v{int(leg_match.group(1)):02d}"
            raw_title = leg_match.group(2).replace("_", " ")
        elif enc_match:
            version_str = f"v{int(enc_match.group(1)):02d}"
            raw_title = p.parent.name.replace("_", " ")
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
    project_dir: Optional[Path] = None,
    title: str = "Untitled",
) -> Path:
    """Save storyboard image bytes to local storage in project images/ directory.

    Default target: `<active_workspace>/projects/<Clean_Title>/images/`
    Filename format: `shot_{shot_number:03d}_scene_{scene_clean}.png`
    Auto-creates target directory if missing.
    """
    clean_title = sanitize_filename_part(title or "Untitled")
    if storyboards_dir is not None:
        target_dir = storyboards_dir
    else:
        base_proj = project_dir or (get_workspace_root() / "projects" / clean_title)
        target_dir = base_proj / "images"

    target_dir.mkdir(parents=True, exist_ok=True)

    scene_clean = sanitize_filename_part(str(scene_number or "1"))
    filename = f"shot_{int(shot_number):03d}_scene_{scene_clean}.png"
    file_path = target_dir / filename

    file_path.write_bytes(image_bytes)
    return file_path

