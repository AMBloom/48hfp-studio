"""Hierarchical System Prompt Compiler engine for 48HFP-Studio.

Enforces prompt injection hierarchy and The Recency Effect by appending
Immutable Festival Rules at the absolute bottom of the system prompt.
"""

from typing import Optional

from studio.models.constraints import CreativeConstraint, LogisticalConstraint
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.utils.constraint_store import (
    load_creative_constraint,
    load_logistical_constraint,
)
from studio.utils.draw_store import load_draw
from studio.utils.profile_store import load_profile


class PromptBuilder:
    """Compiles global state, active constraint sets, and Friday Draw into a strict system prompt."""

    @classmethod
    def compile_system_prompt(
        cls,
        draw: Optional[FridayDraw] = None,
        profile: Optional[TeamProfile] = None,
        logistical: Optional[LogisticalConstraint] = None,
        creative: Optional[CreativeConstraint] = None,
    ) -> str:
        """Compile and return the complete hierarchical system prompt string.

        Hierarchy:
        1. System Persona Directive
        2. Global Team State
        3. Active Creative Constraints
        4. Active Logistical Constraints
        5. Output Schema Directives
        6. Friday Night Draw Kickoff Input
        7. Immutable Festival Rules (Recency Effect - Absolute Bottom)
        """
        # Resolve inputs from store if not provided
        final_profile = profile or load_profile()
        final_draw = draw or load_draw()

        if logistical is None and final_profile and final_profile.active_logistical_constraint:
            logistical = load_logistical_constraint(final_profile.active_logistical_constraint)

        if creative is None and final_profile and final_profile.active_creative_constraint:
            creative = load_creative_constraint(final_profile.active_creative_constraint)

        sections = []

        # 1. System Persona Directive
        sections.append(cls._build_persona_section())

        # 2. Global Team State
        sections.append(cls._build_global_state_section(final_profile))

        # 3. Active Creative Constraints
        sections.append(cls._build_creative_section(creative))

        # 4. Active Logistical Constraints
        sections.append(cls._build_logistical_section(logistical))

        # 5. Output Schema Directives
        sections.append(cls._build_schema_section())

        # 6. Friday Night Draw Input
        sections.append(cls._build_draw_section(final_draw))

        # 7. Immutable Festival Rules (The Recency Effect - Placed at absolute bottom)
        sections.append(cls._build_immutable_rules_section(final_draw))

        return "\n\n".join(sections)

    @staticmethod
    def _build_persona_section() -> str:
        return (
            "================================================================================\n"
            "SYSTEM PERSONA DIRECTIVE\n"
            "================================================================================\n"
            "You are an expert, award-winning film producer and master screenwriter specializing\n"
            "in high-concept short films for the 48 Hour Film Project (48HFP) and international film festivals.\n"
            "Your objective is to generate a comprehensive, highly creative, and 100% rule-compliant\n"
            "pre-production film script treatment based strictly on the provided constraint parameters.\n"
            "You balance narrative tension, visual storytelling, tight scene economy, and practical production reality."
        )

    @staticmethod
    def _build_global_state_section(profile: Optional[TeamProfile]) -> str:
        header = (
            "================================================================================\n"
            "1. GLOBAL PRODUCTION TEAM STATE & RESOURCES\n"
            "================================================================================\n"
        )
        location_directive = (
            "NOTE: The Production Location dictates physical filming boundaries and logistics. "
            "It DOES NOT dictate the fictional setting of the story unless explicitly required by the Creative Constraints."
        )

        if not profile:
            return (
                header
                + f"Team Status: [Unconfigured - Use standard indie film crew defaults]\n\n{location_directive}"
            )

        lines = [
            f"Production Team Name: {profile.team_name}",
            f"Team Administrator: {profile.admin_username}",
            f"Production Location: {profile.location}",
            "Available Team Roster & Roles:",
        ]
        if profile.roles:
            for role, members in profile.roles.items():
                m_str = ", ".join(members) if members else "None assigned"
                lines.append(f"  • {role}: {m_str}")
        else:
            lines.append("  • No specific role assignments provided.")

        if profile.custom_details and profile.custom_details.strip():
            lines.append(f"Custom Equipment & Logistics Notes:\n  {profile.custom_details.strip()}")

        lines.append(f"\n{location_directive}")

        return header + "\n".join(lines)

    @staticmethod
    def _build_creative_section(creative: Optional[CreativeConstraint]) -> str:
        header = (
            "================================================================================\n"
            "2. ACTIVE CREATIVE CONSTRAINT SET (DIRECTORIAL VISION)\n"
            "================================================================================\n"
        )
        if not creative:
            return header + "Active Set: [None Primed - Apply flexible narrative guidelines]"

        lines = [
            f"Set Name: {creative.name}",
            f"Description: {creative.description or 'N/A'}",
        ]
        if creative.scenarios:
            lines.append("Pre-Baked Story Scenarios / Concepts:")
            for idx, sc in enumerate(creative.scenarios, 1):
                lines.append(f"  {idx}. {sc}")

        lines.append(f"Core Philosophy & Motivation:\n  {creative.core_philosophy or 'N/A'}")
        lines.append(f"Scene Economy & Pacing:\n  {creative.scene_economy or 'N/A'}")
        lines.append(f"Progression & Climax Structure:\n  {creative.progression_and_climax or 'N/A'}")
        lines.append(f"Visuals & Post-Production Guidelines:\n  {creative.visuals_and_post or 'N/A'}")

        return header + "\n".join(lines)

    @staticmethod
    def _build_logistical_section(logistical: Optional[LogisticalConstraint]) -> str:
        header = (
            "================================================================================\n"
            "3. ACTIVE LOGISTICAL CONSTRAINT SET (SHOOT REALITY & PHYSICAL ASSETS)\n"
            "================================================================================\n"
        )
        if not logistical:
            return header + "Active Set: [None Primed - Apply standard location and cast availability]"

        lines = [
            f"Set Name: {logistical.name}",
            f"Description: {logistical.description or 'N/A'}",
            f"Filming Locations: {', '.join(logistical.locations) if logistical.locations else 'N/A'}",
            f"Sub-Locations: {', '.join(logistical.sub_locations) if logistical.sub_locations else 'N/A'}",
            f"Location Layout & Lighting Details:\n  {logistical.location_details or 'N/A'}",
        ]

        if logistical.main_character_details:
            mc = logistical.main_character_details
            lines.append(f"Main Character Actor Extension:\n  Name: {mc.name} | Traits: {mc.actor_traits or 'N/A'} | Wardrobe: {mc.wardrobe or 'N/A'} | Notes: {mc.notes or 'N/A'}")

        if logistical.other_characters:
            lines.append("Additional Available Cast Roster:")
            for char in logistical.other_characters:
                lines.append(f"  • {char.name}: {char.actor_traits or 'No traits'} (Wardrobe: {char.wardrobe or 'N/A'})")

        if logistical.props_and_dialogue:
            lines.append("Available Physical Props & Dialogue Hooks:")
            for item in logistical.props_and_dialogue:
                lines.append(f"  • {item}")

        return header + "\n".join(lines)

    @staticmethod
    def _build_schema_section() -> str:
        return (
            "================================================================================\n"
            "4. OUTPUT FORMATTING & TREATMENT SCHEMA DIRECTIVES\n"
            "================================================================================\n"
            "Your output script treatment MUST be structured in clean Markdown with the following headers:\n\n"
            "1. # FILM TITLE & LOGLINE\n"
            "   - Working Title\n"
            "   - Genre Blend (Primary + Secondary)\n"
            "   - 1-2 sentence dramatic Logline\n\n"
            "2. ## CHARACTER ROSTER & CASTING\n"
            "   - Detailed breakdown of all characters, matching available team cast.\n"
            "   - Explicitly highlight the Required Character entity.\n\n"
            "3. ## NARRATIVE SYNOPSIS & THEMATIC ARC\n"
            "   - 3-paragraph story summary (Act I Setup, Act II Escalation, Act III Climax/Resolution).\n"
            "   - Core theme and motivation integration.\n\n"
            "4. ## SCENE-BY-SCENE BREAKDOWN\n"
            "   - Detailed scene numbered list specifying Location, Time, Characters, Action, and Props.\n\n"
            "5. ## SAMPLE DIALOGUE SNIPPETS\n"
            "   - Key dialogue beats including the verbatim required line.\n\n"
            "6. ## FESTIVAL COMPLIANCE CHECKLIST\n"
            "   - Explicit verification list confirming verbatim line, prop usage, character linkage, and runtime pacing."
        )

    @staticmethod
    def _build_draw_section(draw: Optional[FridayDraw]) -> str:
        header = (
            "================================================================================\n"
            "5. THE FRIDAY NIGHT DRAW (KICKOFF INPUT DATA)\n"
            "================================================================================\n"
        )
        if not draw:
            return header + "Kickoff Data: [No Friday Draw Recorded - Run '48hfp draw' wizard first]"

        return header + (
            f"Primary Genre (Group 1): {draw.genre_1}\n"
            f"Secondary Genre (Group 2): {draw.genre_2}\n"
            f"Required Character Name: {draw.character_name}\n"
            f"Required Character Trait / Profession: {draw.character_trait}\n"
            f"Required Character Gender / Sex: {draw.character_gender}\n"
            f"Required Physical Prop: {draw.required_prop}\n"
            f'Required Verbatim Dialogue Line: "{draw.required_line}"'
        )

    @staticmethod
    def _build_immutable_rules_section(draw: Optional[FridayDraw]) -> str:
        prop_str = f'"{draw.required_prop}"' if draw else 'the designated required prop'
        line_str = f'"{draw.required_line}"' if draw else 'the designated verbatim dialogue line'
        char_str = f'"{draw.character_name}" ({draw.character_trait})' if draw else 'the designated required character'

        return (
            "================================================================================\n"
            "6. IMMUTABLE FESTIVAL RULES (STRICT COMPLIANCE MANDATE - RECENCY EFFECT)\n"
            "================================================================================\n"
            "CRITICAL: The following rules are IMMUTABLE and ANCHORED at the bottom of this prompt.\n"
            "Due to The Recency Effect, you MUST prioritize these mandates above all other creative directives:\n\n"
            "1. RUNTIME PACING CONSTRAINT:\n"
            "   • The final script structure and pacing MUST strictly target a 4 to 7 minute total runtime.\n"
            "   • Do NOT write scenes that exceed a 7-minute visual pacing limit.\n\n"
            "2. VERBATIM DIALOGUE RULE:\n"
            f"   • The required line {line_str} MUST appear VERBATIM in the script.\n"
            "   • The line may be spoken, sung, or written.\n"
            "   • The line MAY be split between two actors sequentially without any extra words injected in between.\n"
            "   • If translated into a non-English language, exact subtitles showing the verbatim line are mandatory.\n\n"
            "3. REQUIRED PROP USAGE:\n"
            f"   • The required prop {prop_str} MUST be physically seen on screen AND actively used in the film/plot.\n"
            "   • It cannot merely sit in the background as inert set dressing.\n\n"
            "4. REQUIRED CHARACTER LINKAGE:\n"
            f"   • The character name and trait/profession {char_str} MUST belong to the SAME on-screen entity.\n"
            "   • The character MUST physically appear on screen (their name does not need to be spoken aloud).\n"
            "================================================================================"
        )
