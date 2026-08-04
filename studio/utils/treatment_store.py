"""Output Versioning and Safe-Write Markdown exporter for 48HFP-Studio.

Manages saving generated treatments to local storage in Markdown format,
enforcing cross-platform pathing, version zero-padding (e.g., v01, v02),
and safe-write non-overwrite guarantees.
"""

from datetime import datetime
from pathlib import Path
import re
from typing import List, Optional

from studio.models.treatment import TreatmentOutput
from studio.utils.profile_store import load_profile


def sanitize_filename_part(text: str) -> str:
    """Sanitize constraint names or strings for clean filename usage."""
    if not text:
        return "Unconstrained"
    # Replace non-alphanumeric characters with underscores
    clean = re.sub(r"[^\w\-]", "_", text.strip())
    # Collapse multiple consecutive underscores
    clean = re.sub(r"_+", "_", clean)
    return clean.strip("_") or "Unconstrained"


def get_next_version_number(outputs_dir: Path) -> int:
    """Scan outputs directory for existing treatments and compute next version number.

    Guardrail 3 (Empty Directory Fallback): Defaults safely to 1 if no treatment
    files exist or if directory is empty.
    """
    if not outputs_dir.exists():
        return 1

    pattern = re.compile(r"^treatment_v(\d+)_", re.IGNORECASE)
    versions: List[int] = []

    for file_path in outputs_dir.glob("treatment_v*.md"):
        match = pattern.match(file_path.name)
        if match:
            try:
                versions.append(int(match.group(1)))
            except ValueError:
                continue

    if not versions:
        return 1

    return max(versions) + 1


def convert_treatment_to_markdown(treatment: TreatmentOutput) -> str:
    """Convert a TreatmentOutput Pydantic object into a readable Markdown document."""
    tl = treatment.title_and_logline
    syn = treatment.synopsis
    chk = treatment.compliance_checklist

    lines = [
        f"# {tl.title.upper()}",
        "",
        "## 1. FILM TITLE & LOGLINE",
        f"- **Working Title:** {tl.title}",
        f"- **Genre Blend:** {tl.genre_blend}",
        f"- **Logline:** {tl.logline}",
        "",
        "## 2. CHARACTER ROSTER & CASTING",
        "| Character | Actor / Traits | Role | 48HFP Required? |",
        "|---|---|---|---|",
    ]

    for char in treatment.character_roster:
        req_str = "✔ Yes" if char.is_required_character else "No"
        lines.append(f"| {char.name} | {char.actor_or_traits} | {char.role} | {req_str} |")

    lines.extend(
        [
            "",
            "## 3. NARRATIVE SYNOPSIS & THEMATIC ARC",
            "### Act I: Setup",
            syn.act_1_setup,
            "",
            "### Act II: Escalation",
            syn.act_2_escalation,
            "",
            "### Act III: Climax & Resolution",
            syn.act_3_climax_resolution,
            "",
            "### Thematic Arc & Core Motivation",
            syn.thematic_arc,
            "",
            "## 4. SCENE-BY-SCENE BREAKDOWN",
        ]
    )

    for sc in treatment.scene_breakdown:
        chars_str = ", ".join(sc.characters_present) if sc.characters_present else "None"
        props_str = ", ".join(sc.props_used) if sc.props_used else "None"
        lines.extend(
            [
                f"### Scene {sc.scene_number}: {sc.heading}",
                f"- **Location:** {sc.location} ({sc.time_of_day})",
                f"- **Characters Present:** {chars_str}",
                f"- **Props Used:** {props_str}",
                f"- **Action & Pacing:**",
                f"  {sc.action_summary}",
                "",
            ]
        )

    lines.extend(
        [
            "## 5. SAMPLE DIALOGUE SNIPPETS",
        ]
    )

    for d in treatment.dialogue_snippets:
        req_tag = " [VERBATIM REQUIRED LINE]" if d.is_required_line else ""
        lines.extend(
            [
                f"- **{d.character}**{req_tag}: *\"{d.line}\"*",
                f"  - *Context:* {d.context_notes}",
            ]
        )

    v_line = "[x]" if chk.verbatim_line_verified else "[ ]"
    v_prop = "[x]" if chk.prop_usage_verified else "[ ]"
    v_char = "[x]" if chk.character_linkage_verified else "[ ]"
    v_time = "[x]" if chk.pacing_runtime_verified else "[ ]"

    lines.extend(
        [
            "",
            "## 6. FESTIVAL COMPLIANCE CHECKLIST",
            f"- {v_line} **Verbatim Line Verified:** {chk.verbatim_line_verified}",
            f"- {v_prop} **Required Prop Usage Verified:** {chk.prop_usage_verified}",
            f"- {v_char} **Character Linkage Verified:** {chk.character_linkage_verified}",
            f"- {v_time} **Pacing & Runtime (4-7 mins) Verified:** {chk.pacing_runtime_verified}",
            "",
            "### Compliance Notes",
            chk.compliance_notes,
            "",
        ]
    )

    return "\n".join(lines)


def save_treatment_output(
    treatment: TreatmentOutput,
    outputs_dir: Optional[Path] = None,
) -> Path:
    """Safely export treatment to Markdown file with auto-incrementing zero-padded version.

    Guardrail 1 (Cross-Platform Pathing): Defaults to `pathlib.Path.cwd() / "outputs"`.
    Guardrail 2 (Version Zero-Padding): Formats version as v01, v02, v10, etc.
    Safe-Write System: Ensures previous outputs are NEVER overwritten.
    """
    # Guardrail 1: Cross-Platform Pathing using Path.cwd()
    target_dir = outputs_dir or (Path.cwd() / "outputs")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Resolve active constraints for naming
    profile = load_profile()
    log_name = "Unconstrained"
    cre_name = "Unconstrained"

    if profile:
        if profile.active_logistical_constraint:
            log_name = profile.active_logistical_constraint
        if profile.active_creative_constraint:
            cre_name = profile.active_creative_constraint

    log_clean = sanitize_filename_part(log_name)
    cre_clean = sanitize_filename_part(cre_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Guardrail 3 & 2: Calculate version and format with zero-padding
    version = get_next_version_number(target_dir)

    # Loop to guarantee safe-write non-overwrite protection
    while True:
        # Guardrail 2: Zero-padded 2-digit integer e.g., v01, v02
        version_str = f"v{version:02d}"
        filename = f"treatment_{version_str}_{log_clean}_{cre_clean}_{timestamp}.md"
        file_path = target_dir / filename

        if not file_path.exists():
            break
        version += 1

    markdown_content = convert_treatment_to_markdown(treatment)
    file_path.write_text(markdown_content, encoding="utf-8")

    return file_path
