"""Hierarchical System Prompt Compiler engine for 48HFP-Studio.

Enforces prompt injection hierarchy and The Recency Effect by appending
Immutable Festival Rules at the absolute bottom of the system prompt.
"""

from typing import Optional

from studio.models.constraints import (
    DirectorialVision,
    IdeaSeed,
    LogisticalConstraint,
    ThematicFramework,
)
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.models.treatment import TreatmentOutput
from studio.utils.constraint_store import (
    load_directorial_vision,
    load_idea_seed,
    load_logistical_constraint,
    load_thematic_framework,
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
        directorial: Optional[DirectorialVision] = None,
        thematic: Optional[ThematicFramework] = None,
        idea: Optional[IdeaSeed] = None,
        additional_instructions: Optional[str] = None,
    ) -> str:
        """Compile and return the complete hierarchical system prompt string.

        Hierarchy:
        1. System Persona Directive
        2. Global Team State
        3. Active Directorial Vision
        4. Active Thematic Framework
        5. Active Idea Seed
        6. Active Logistical Constraints
        7. Additional Filmmaker Directives (Optional - Omitted if empty)
        8. Output Schema Directives
        9. Friday Night Draw Kickoff Input
        10. Immutable Festival Rules (Recency Effect - Absolute Bottom)
        """
        # Resolve inputs from store if not provided
        final_profile = profile or load_profile()
        final_draw = draw or load_draw()

        if logistical is None and final_profile and final_profile.active_logistical_constraint:
            logistical = load_logistical_constraint(final_profile.active_logistical_constraint)

        if directorial is None and final_profile and final_profile.active_directorial_vision:
            directorial = load_directorial_vision(final_profile.active_directorial_vision)

        if thematic is None and final_profile and final_profile.active_thematic_framework:
            thematic = load_thematic_framework(final_profile.active_thematic_framework)

        if idea is None and final_profile and final_profile.active_idea_seed:
            idea = load_idea_seed(final_profile.active_idea_seed)

        sections = []

        # 1. System Persona Directive
        sections.append(cls._build_persona_section())

        # 2. Global Team State
        sections.append(cls._build_global_state_section(final_profile))

        # 3. Active Directorial Vision
        sections.append(cls._build_directorial_section(directorial))

        # 4. Active Thematic Framework
        sections.append(cls._build_thematic_section(thematic))

        # 5. Active Idea Seed
        sections.append(cls._build_idea_section(idea))

        # 6. Active Logistical Constraints
        sections.append(cls._build_logistical_section(logistical))

        # 7. Additional Directives (Omitted if empty)
        add_directives_section = cls._build_additional_directives_section(additional_instructions)
        if add_directives_section:
            sections.append(add_directives_section)

        # 8. Output Schema Directives
        sections.append(cls._build_schema_section())

        # 9. Friday Night Draw Input
        sections.append(cls._build_draw_section(final_draw))

        # 10. Immutable Festival Rules (The Recency Effect - Placed at absolute bottom)
        sections.append(cls._build_immutable_rules_section(final_draw))

        return "\n\n".join(sections)

    @classmethod
    def compile_revision_prompt(
        cls,
        current_treatment: TreatmentOutput,
        notes: str,
        original_prompt: Optional[str] = None,
        draw: Optional[FridayDraw] = None,
        profile: Optional[TeamProfile] = None,
    ) -> str:
        """Compile a revision prompt ensuring Recency Effect (Immutable Rules at absolute bottom)

        and stateless token conservation (single latest draft + newest note).
        """
        # Resolve base system prompt
        source_prompt = original_prompt or cls.compile_system_prompt(draw=draw, profile=profile)

        rules_marker = "================================================================================\n8. IMMUTABLE FESTIVAL RULES"
        if rules_marker in source_prompt:
            parts = source_prompt.split(rules_marker, 1)
            main_part = parts[0].rstrip()
            rules_section = rules_marker + parts[1]
        else:
            main_part = source_prompt.strip()
            final_draw = draw or load_draw()
            rules_section = cls._build_immutable_rules_section(final_draw)

        # Strip out any prior revision directives to enforce stateless single-draft payload
        rev_marker = "================================================================================\nREVISION DIRECTIVES & PREVIOUS DRAFT"
        if rev_marker in main_part:
            base_part = main_part.split(rev_marker, 1)[0].rstrip()
        else:
            base_part = main_part.rstrip()

        treatment_json = current_treatment.model_dump_json(indent=2)
        revision_section = (
            "================================================================================\n"
            "REVISION DIRECTIVES & PREVIOUS DRAFT\n"
            "================================================================================\n"
            "Below is the SINGLE MOST RECENT DRAFT of the film treatment in JSON format:\n\n"
            "```json\n"
            f"{treatment_json}\n"
            "```\n\n"
            "FILMMAKER REVISION NOTES / CHANGE REQUESTS:\n"
            f"\"{notes.strip()}\"\n\n"
            "REVISION INSTRUCTIONS:\n"
            "1. Update the film treatment according to the filmmaker's revision notes.\n"
            "2. Preserve all existing elements that do not conflict with the notes.\n"
            "3. You MUST continue to strictly satisfy all festival rules, character requirements, prop usages, and verbatim line mandates.\n"
            "4. Your output MUST strictly match the required TreatmentOutput JSON schema."
        )

        return f"{base_part}\n\n{revision_section}\n\n{rules_section}"

    @classmethod
    def compile_screenplay_prompt(
        cls,
        treatment: TreatmentOutput,
        draw: Optional[FridayDraw] = None,
        profile: Optional[TeamProfile] = None,
        additional_instructions: Optional[str] = None,
    ) -> str:
        """Compile a screenplay prompt that instructs the LLM to interpret the active treatment

        into a complete, Hollywood-ready screenplay strictly formatted in Fountain markup syntax (.fountain).
        """
        final_draw = draw or load_draw()
        final_profile = profile or load_profile()

        sections = []

        # Persona & Objective
        sections.append(
            "================================================================================\n"
            "SCREENPLAY GENERATION DIRECTIVE (.FOUNTAIN FORMAT)\n"
            "================================================================================\n"
            "You are a master Hollywood screenwriter. Your task is to adapt the provided film treatment\n"
            "into a complete, professional, 100% production-ready short film screenplay in standard FOUNTAIN markup.\n"
            "Target screenplay length: approximately 4 to 6 pages (aiming for a 4 to 7 minute short film)."
        )

        # Global Team State
        sections.append(cls._build_global_state_section(final_profile))

        # Treatment Context
        treatment_markdown = treatment.model_dump_json(indent=2)
        sections.append(
            "================================================================================\n"
            "SOURCE FILM TREATMENT (JSON PAYLOAD)\n"
            "================================================================================\n"
            "Base your screenplay directly on the characters, plot, beats, and scene breakdown below:\n\n"
            "```json\n"
            f"{treatment_markdown}\n"
            "```"
        )

        # Additional Directives if present
        if additional_instructions and additional_instructions.strip():
            sections.append(
                "================================================================================\n"
                "ADDITIONAL FILMMAKER DIRECTIVES\n"
                "================================================================================\n"
                f"{additional_instructions.strip()}"
            )

        # Fountain Syntax Rules & Strict Output Directives
        sections.append(
            "================================================================================\n"
            "FOUNTAIN FORMATTING DIRECTIVES & STRICT OUTPUT RULES\n"
            "================================================================================\n"
            "Strictly follow standard Fountain screenplay syntax:\n"
            "1. SCENE HEADINGS: Must begin with INT., EXT., EST., INT./EXT., or EXT./INT. in ALL CAPS.\n"
            "2. CHARACTER NAMES: Must be in ALL CAPS on a single line preceding dialogue.\n"
            "3. PARENTHETICALS: Must be enclosed in parentheses (parenthetical) on a line below character name.\n"
            "4. DIALOGUE: Appears directly below character name / parenthetical.\n"
            "5. ACTION / BLOCKING: Standard sentence case describing character actions, camera, and props.\n"
            "6. TRANSITIONS: ALL CAPS ending with TO: (e.g. CUT TO:).\n\n"
            "CRITICAL OUTPUT MANDATE:\n"
            "• Output ONLY the pure raw .fountain screenplay text.\n"
            "• DO NOT wrap your response in markdown code fences (no ```fountain or ```).\n"
            "• DO NOT include introductory greetings, system prompt appendices, or trailing commentary."
        )

        # Friday Draw & Immutable Festival Rules (Recency Effect - Absolute Bottom)
        sections.append(cls._build_draw_section(final_draw))
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
            "Available Crew Roster & Roles:",
        ]
        crew_dict = profile.crew or profile.roles or {}
        if crew_dict:
            for role, members in crew_dict.items():
                m_str = ", ".join(members) if members else "None assigned"
                lines.append(f"  • {role}: {m_str}")
        else:
            lines.append("  • No specific crew role assignments provided.")

        if profile.cast:
            lines.append("Available Cast Roster:")
            for actor in profile.cast:
                lines.append(
                    f"  • {actor.get('name', 'Actor')}: Age {actor.get('age_range', 'N/A')}, "
                    f"Gender: {actor.get('gender', 'N/A')}, Physicality: {actor.get('physicality', 'N/A')}"
                )

        if profile.available_gear:
            lines.append("Available Equipment & Gear Catalog:")
            for g in profile.available_gear:
                lines.append(f"  • {g}")

        if profile.custom_details and profile.custom_details.strip():
            lines.append(f"Custom Equipment & Logistics Notes:\n  {profile.custom_details.strip()}")

        lines.append(f"\n{location_directive}")

        return header + "\n".join(lines)

    @staticmethod
    def _build_directorial_section(directorial: Optional[DirectorialVision]) -> str:
        header = (
            "================================================================================\n"
            "2. ACTIVE DIRECTORIAL VISION (VISUAL & AUDIO STYLE)\n"
            "================================================================================\n"
        )
        if not directorial:
            return header + "Active Vision: [None Primed - Apply versatile cinematic visual directives]"

        lines = [
            f"Vision Name: {directorial.name}",
            f"Description: {directorial.description or 'N/A'}",
            f"Visual Economy & Camera Movement:\n  {directorial.visual_economy or 'N/A'}",
            f"Lighting & Color Grading Intent:\n  {directorial.lighting_color or 'N/A'}",
            f"Audio Landscape & Music Intent:\n  {directorial.audio_landscape or 'N/A'}",
        ]
        return header + "\n".join(lines)

    @staticmethod
    def _build_thematic_section(thematic: Optional[ThematicFramework]) -> str:
        header = (
            "================================================================================\n"
            "3. ACTIVE THEMATIC FRAMEWORK (CORE PHILOSOPHY & EMOTIONAL ARC)\n"
            "================================================================================\n"
        )
        if not thematic:
            return header + "Active Framework: [None Primed - Apply flexible dramatic thematic spine]"

        lines = [
            f"Framework Name: {thematic.name}",
            f"Description: {thematic.description or 'N/A'}",
            f"Core Philosophy & Subtext:\n  {thematic.core_philosophy or 'N/A'}",
            f"Emotional Arc & Climax Dynamics:\n  {thematic.emotional_arc or 'N/A'}",
            f"World Rules & Atmospheric Logic:\n  {thematic.world_rules or 'N/A'}",
        ]
        return header + "\n".join(lines)

    @staticmethod
    def _build_idea_section(idea: Optional[IdeaSeed]) -> str:
        header = (
            "================================================================================\n"
            "4. ACTIVE IDEA SEED (NARRATIVE SPARK & SCENARIO)\n"
            "================================================================================\n"
        )
        if not idea:
            return header + "Active Seed: [None Primed - Generate original scenario tailored to draw]"

        lines = [
            f"Seed Name: {idea.name}",
            f"Description: {idea.description or 'N/A'}",
            f"Inciting Incident / Initial Spark:\n  {idea.inciting_incident or 'N/A'}",
            f"Complications & Midpoint Twists:\n  {idea.complications or 'N/A'}",
            f"Ending Targets & Resolution Notes:\n  {idea.ending_targets or 'N/A'}",
        ]
        return header + "\n".join(lines)

    @staticmethod
    def _build_logistical_section(logistical: Optional[LogisticalConstraint]) -> str:
        header = (
            "================================================================================\n"
            "5. ACTIVE LOGISTICAL CONSTRAINT SET (SHOOT REALITY & PHYSICAL ASSETS)\n"
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

        if logistical.other_characters:
            lines.append("Additional Available Cast Roster:")
            for char in logistical.other_characters:
                lines.append(f"  • {char.name}: {char.actor_traits or 'No traits'} (Wardrobe: {char.wardrobe or 'N/A'})")

        dressing = logistical.available_set_dressing
        if dressing:
            lines.append("Available Set Dressing, Wardrobe & Dialogue Hooks:")
            for item in dressing:
                lines.append(f"  • {item}")

        return header + "\n".join(lines)

    @staticmethod
    def _build_additional_directives_section(additional_instructions: Optional[str]) -> Optional[str]:
        if not additional_instructions or not additional_instructions.strip():
            return None
        return (
            "================================================================================\n"
            "ADDITIONAL FILMMAKER DIRECTIVES\n"
            "================================================================================\n"
            f"{additional_instructions.strip()}"
        )

    @staticmethod
    def _build_schema_section() -> str:
        return (
            "================================================================================\n"
            "6. OUTPUT FORMATTING & TREATMENT SCHEMA DIRECTIVES\n"
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
            "7. THE FRIDAY NIGHT DRAW (KICKOFF INPUT DATA)\n"
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
            "8. IMMUTABLE FESTIVAL RULES (STRICT COMPLIANCE MANDATE - RECENCY EFFECT)\n"
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

