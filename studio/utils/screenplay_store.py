"""Output Versioning and Safe-Write Screenplay (.fountain) exporter for 48HFP-Studio.

Manages saving generated screenplays to local storage in Fountain format,
enforcing cross-platform pathing, version zero-padding (e.g., v01, v02),
and safe-write non-overwrite guarantees.
"""

from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Optional

from studio.utils.global_state import get_workspace_root
from studio.utils.treatment_store import sanitize_filename_part


def get_next_screenplay_version_number(screenplays_dir: Path) -> int:
    """Scan screenplays directory for existing scripts and compute next version number.

    Defaults safely to 1 if no screenplay files exist or if directory is empty.
    """
    if not screenplays_dir.exists():
        return 1

    pattern = re.compile(r"^script_v(\d+)_", re.IGNORECASE)
    versions: List[int] = []

    for file_path in screenplays_dir.glob("script_v*.fountain"):
        match = pattern.match(file_path.name)
        if match:
            try:
                versions.append(int(match.group(1)))
            except ValueError:
                continue

    if not versions:
        return 1

    return max(versions) + 1


def clean_fountain_text(text: str) -> str:
    """Strip any accidental markdown code fence wrappers (```fountain or ```) from text."""
    if not text:
        return ""
    cleaned = text.strip()
    # Strip leading ```fountain or ```
    if cleaned.startswith("```"):
        first_line_end = cleaned.find("\n")
        if first_line_end != -1:
            cleaned = cleaned[first_line_end + 1:]
        else:
            cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned)
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].rstrip()
    return cleaned.strip()


def save_screenplay_output(
    screenplay_text: str,
    title: str = "Untitled",
    screenplays_dir: Optional[Path] = None,
) -> Path:
    """Safely export screenplay to Fountain file with auto-incrementing zero-padded version.

    Target directory: `<workspace>/screenplays`
    Version format: script_v01_<title>_<timestamp>.fountain
    Safe-Write System: Ensures previous outputs are NEVER overwritten.
    """
    target_dir = screenplays_dir or (get_workspace_root() / "screenplays")
    target_dir.mkdir(parents=True, exist_ok=True)

    title_clean = sanitize_filename_part(title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    version = get_next_screenplay_version_number(target_dir)

    while True:
        version_str = f"v{version:02d}"
        filename = f"script_{version_str}_{title_clean}_{timestamp}.fountain"
        file_path = target_dir / filename

        if not file_path.exists():
            break
        version += 1

    cleaned_text = clean_fountain_text(screenplay_text)
    file_path.write_text(cleaned_text, encoding="utf-8")

    return file_path


def list_saved_screenplays(screenplays_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """Scan workspace screenplays/ directory and return list of metadata dictionaries.

    Returns dicts with keys: 'filename', 'version', 'title', 'path', 'mtime', 'formatted_date'.
    Sorted by mtime descending (newest first).
    """
    target_dir = screenplays_dir or (get_workspace_root() / "screenplays")
    if not target_dir.exists():
        return []

    results: List[Dict[str, str]] = []
    pattern = re.compile(r"^script_v(\d+)_(.+)_\d{8}_\d{6}\.fountain$", re.IGNORECASE)

    for p in target_dir.glob("script_v*.fountain"):
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


def list_saved_treatments(outputs_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """Scan workspace outputs/ directory and return list of treatment metadata dictionaries.

    Returns dicts with keys: 'filename', 'version', 'title', 'path', 'mtime', 'formatted_date'.
    Sorted by mtime descending (newest first).
    """
    target_dir = outputs_dir or (get_workspace_root() / "outputs")
    if not target_dir.exists():
        return []

    results: List[Dict[str, str]] = []
    pattern = re.compile(r"^treatment_v(\d+)_(.+)_\d{8}_\d{6}\.md$", re.IGNORECASE)

    for p in target_dir.glob("treatment_v*.md"):
        if not p.is_file():
            continue
        stat = p.stat()
        mtime = stat.st_mtime
        formatted_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

        match = pattern.match(p.name)
        if match:
            version_str = f"v{int(match.group(1)):02d}"
            # Extract first section before underscore as title
            parts = match.group(2).split("_")
            raw_title = parts[0] if parts else match.group(2)
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
