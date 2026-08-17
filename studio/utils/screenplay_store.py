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
from studio.utils.profile_store import load_profile
from studio.utils.treatment_store import sanitize_filename_part


def get_next_screenplay_version_number(screenplays_dir: Path) -> int:
    """Scan screenplays directory for existing scripts and compute next version number.

    Supports encapsulated format (script_v01.fountain) and legacy format (script_v01_...fountain).
    Defaults safely to 1 if no screenplay files exist or if directory is empty.
    """
    if not screenplays_dir.exists():
        return 1

    encapsulated_pattern = re.compile(r"^script_v(\d+)\.fountain$", re.IGNORECASE)
    legacy_pattern = re.compile(r"^script_v(\d+)_", re.IGNORECASE)
    versions: List[int] = []

    for file_path in screenplays_dir.glob("script_v*.fountain"):
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
    project_dir: Optional[Path] = None,
) -> Path:
    """Safely export screenplay to Fountain file with auto-incrementing zero-padded version.

    Default target: `<workspace_root>/projects/<Clean_Project_Title>/script_v01.fountain`.
    Prepends standardized Fountain title metadata block (Title, Author, Draft date).
    If `screenplays_dir` is explicitly supplied, preserves flat output for backward compatibility.
    Safe-Write System: Ensures previous outputs are NEVER overwritten.
    """
    title_clean = sanitize_filename_part(title)

    # Programmatic Fountain metadata injection
    profile = load_profile()
    author = profile.team_name if (profile and profile.team_name) else "48HFP Production Team"
    draft_date = datetime.now().strftime("%Y-%m-%d")
    fountain_header = f"Title: {title}\nAuthor: {author}\nDraft date: {draft_date}\n\n"

    cleaned_text = clean_fountain_text(screenplay_text)
    if not cleaned_text.startswith("Title:"):
        final_content = fountain_header + cleaned_text
    else:
        final_content = cleaned_text

    if screenplays_dir is not None:
        target_dir = screenplays_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        version = get_next_screenplay_version_number(target_dir)

        while True:
            version_str = f"v{version:02d}"
            filename = f"script_{version_str}_{title_clean}_{timestamp}.fountain"
            file_path = target_dir / filename
            if not file_path.exists():
                break
            version += 1
    else:
        target_dir = project_dir or (get_workspace_root() / "projects" / title_clean)
        target_dir.mkdir(parents=True, exist_ok=True)

        version = get_next_screenplay_version_number(target_dir)

        while True:
            version_str = f"v{version:02d}"
            filename = f"script_{version_str}.fountain"
            file_path = target_dir / filename
            if not file_path.exists():
                break
            version += 1

    file_path.write_text(final_content, encoding="utf-8")
    return file_path


def list_saved_screenplays(screenplays_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """Scan workspace for saved screenplays and return list of metadata dictionaries.

    Discovers screenplays from both legacy flat directories and encapsulated project folders.
    Returns dicts with keys: 'filename', 'version', 'title', 'path', 'mtime', 'formatted_date'.
    Sorted by mtime descending (newest first).
    """
    candidate_paths: List[Path] = []

    if screenplays_dir is not None:
        if screenplays_dir.exists():
            candidate_paths.extend(screenplays_dir.glob("script_v*.fountain"))
    else:
        ws_root = get_workspace_root()
        legacy_dir = ws_root / "screenplays"
        if legacy_dir.exists():
            candidate_paths.extend(legacy_dir.glob("script_v*.fountain"))

        projects_dir = ws_root / "projects"
        if projects_dir.exists():
            candidate_paths.extend(projects_dir.glob("*/script_v*.fountain"))

    results: List[Dict[str, str]] = []
    seen_paths = set()
    legacy_pattern = re.compile(r"^script_v(\d+)_(.+)_\d{8}_\d{6}\.fountain$", re.IGNORECASE)
    encapsulated_pattern = re.compile(r"^script_v(\d+)\.fountain$", re.IGNORECASE)

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


def list_saved_treatments(outputs_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """Scan workspace for saved treatments and return list of treatment metadata dictionaries.

    Discovers treatments from both legacy flat directories and encapsulated project folders.
    Returns dicts with keys: 'filename', 'version', 'title', 'path', 'mtime', 'formatted_date'.
    Sorted by mtime descending (newest first).
    """
    candidate_paths: List[Path] = []

    if outputs_dir is not None:
        if outputs_dir.exists():
            candidate_paths.extend(outputs_dir.glob("treatment_v*.md"))
    else:
        ws_root = get_workspace_root()
        legacy_dir = ws_root / "outputs"
        if legacy_dir.exists():
            candidate_paths.extend(legacy_dir.glob("treatment_v*.md"))

        projects_dir = ws_root / "projects"
        if projects_dir.exists():
            candidate_paths.extend(projects_dir.glob("*/treatment_v*.md"))

    results: List[Dict[str, str]] = []
    seen_paths = set()
    legacy_pattern = re.compile(r"^treatment_v(\d+)_(.+)_\d{8}_\d{6}\.md$", re.IGNORECASE)
    encapsulated_pattern = re.compile(r"^treatment_v(\d+)\.md$", re.IGNORECASE)

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
            parts = leg_match.group(2).split("_")
            raw_title = parts[0] if parts else leg_match.group(2)
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

