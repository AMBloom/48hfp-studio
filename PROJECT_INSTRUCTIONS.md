48HFP-Studio: Master Application Bible (v2.0 - CLI Edition)
1. Project Overview & Vision
48HFP-Studio is an open-source, terminal-native AI co-pilot designed for indie film teams competing in the 48 Hour Film Project or similar short film festivals. The application operates exclusively via a Command Line Interface (CLI), ensuring a lightweight footprint, high-speed operation, and easy distribution via GitHub.

The software acts as a highly disciplined pre-production engine. By ingesting modular, user-defined "Constraint Sets" alongside the official Friday Night Draw, the app generates deterministic, 100% compliant script treatments. The application enforces immutable festival rules and creative alignment before cameras roll, saving critical hours during a 48-hour sprint.
2. Environment & Tech Stack
Target OS: Cross-platform (Developed on Ubuntu 24.04 LTS)
Runtime: Python 3.11+
CLI Framework: typer (command routing) & rich (terminal formatting/UI)
Data Validation: pydantic v2
Configuration Storage: PyYAML (for human-readable, multi-line string constraint files)
LLM Orchestration: google-genai SDK (Primary inference engine). Note: Architecture must abstract the provider interface to allow open-source users to easily plug in Ollama, Gemma, or OpenAI endpoints in future builds.


3. Global State: Team Configuration
Upon first run (or via a config command), the CLI stores persistent user variables in a local configuration file (e.g., ~/.48hfp_profile.yaml). These variables inform metadata and context for all generated treatments.

Production Team Name
Team Admin Username (Primary app user)
Production Team Location (City, Country)
Team Members by Role (Producer, Director, Actor, Hair Stylist, Makeup Artist, Production Designer, Grip, Gaffer, DP, AD, etc.)
Custom Details (Open text field for dietary restrictions, vehicle availability, etc.)


4. The Unified Constraint Architecture
All generative inputs are treated as "Constraint Sets." This object-oriented approach allows producers to build, save, and hot-swap variables depending on real-world conditions (e.g., swapping to an "Interior Skeleton Crew" logistical set if it rains on shoot day).
A. Immutable Festival Rules (Hard-Coded Engine Constraints)
These rules are immutable, undeletable, and hard-coded into the core prompt compiler.

Time Constraints: Project must respect the 48-hour development window (reflected in scene economy).
Required Prop: Must be physically seen on screen AND actively used in the film.
Required Line: Must be spoken, sung, or written VERBATIM. It may be split between two actors sequentially without added words. Subtitles required if translated.
Required Character: The character name and trait/profession MUST belong to the same on-screen entity. The character must be seen, though the name does not have to be spoken aloud.
Runtime Constraints: Script pacing must target a 4 to 7-minute final runtime.
B. Logistical Constraint Sets (Mutable YAML)
User-defined files representing the physical reality of the shoot.

Filming Location(s): (e.g., Interior, Restaurant, Night)
Sub-Locations: (e.g., Dining Room, Kitchen, Restroom, Parking Lot)
Location Details: (Long text field detailing layout, lighting, restrictions)
Main Character Details: (Extends the required character with specific actor traits/wardrobe)
Other Characters & Details: (e.g., John Smith, Male, Welder, Cowardly)
Other Props / Dialog: (Available set dressing or running jokes to include)
C. Creative Constraint Sets (Mutable YAML)
User-defined files enforcing the directorial and narrative vision.

Scenarios: Partially baked short descriptions of a story scenario to be combined with the Friday draw.
Core Philosophy & Motivation: The thematic spine of the film.
Scene Economy: Pacing directives (e.g., "Long takes," "frantic cuts").
Progression & Climax: Narrative structure guidelines.
Visuals & Post-Production: Color grading intent, scoring style, or visual effects limits.
D. The Friday Night Draw (Ephemeral Input)
Entered via CLI wizard at kickoff. If any field is left blank ("default"), the LLM is instructed to auto-generate a compliant option.

Genre 1 & Genre 2
Main Character Name (Male or Female)
Character Profession / Trait
Required Prop
Required Line of Dialog


5. Prompt Engineering & Inference Architecture
To ensure extreme reliability, idempotency, and strict rule adherence, the System Prompt Builder must enforce The Recency Effect. LLMs prioritize instructions at the bottom of the prompt.

Prompt Injection Hierarchy (Top to Bottom):

System Persona: "You are an expert film producer and screenwriter..."
Global State: Team size and available crew/roles.
Active Creative Constraints: Tone, pacing, visuals, and scenarios.
Active Logistical Constraints: Locations, actors, and physical limitations.
Output Schema Enforcement: Pydantic JSON structure rules.
The Friday Night Draw: Genre, Prop, Character, Line.
Immutable Festival Rules (The Anchor): The strict constraints regarding verbatim dialogue, prop usage, and character linkage are injected at the absolute end of the prompt sequence to prevent hallucination or override by the Creative Guidelines.


6. Output Versioning & File System
To protect against accidental data loss during high-stress ideation, the CLI must never overwrite previous outputs.

All generated treatments are saved to a local /outputs directory.
Files are automatically named using the active constraint sets and a precise timestamp.
Naming Convention Format: treatment_v[XX]_[Logistical_Name]_[Creative_Name]_[YYYYMMDD_HHMMSS].md (Example: treatment_v01_SherwoodStudios_A24SlowBurn_20260803_190530.md)


7. Next Steps for Antigravity 2 (Agent Directives)
When passing this project to the agentic IDE, instruct the agent to execute the following sequence:

Scaffold the CLI architecture: Set up typer entry points (main.py) for handling the wizard inputs and configuration management.
Build the Data Models: Implement the Pydantic schemas for the structured LLM output and the PyYAML parser for reading/writing the Constraint Set files.
Develop the Prompt Builder: Construct the hierarchical prompt engine ensuring Immutable Rules and Friday Draw data are appended at the bottom.
Implement Versioned Output: Build the file-writing utility that generates the timestamped markdown treatments in the /outputs folder.



Development Roadmap
Phase 1: Core CLI Scaffolding & Global State
Objective: Establish the terminal-native application shell and persistent user configuration.

Sprint 1.1: Project Initialization & CLI Skeleton

1.1.1: Set up the typer application structure and root entry points.

1.1.2: Implement rich for styled, colorized terminal outputs.

Sprint 1.2: Team Configuration & Persistence

1.2.1: Build the CLI config command to onboard user and team details (Team Name, Admin, Location, Roles).

1.2.2: Implement PyYAML read/write logic to save and load this global state from a persistent ~/.48hfp_profile.yaml file.
Phase 2: The Unified Constraint System
Objective: Build the modular logic to handle Logistical and Creative Constraint Sets.

Sprint 2.1: Constraint Data Models & Storage

2.1.1: Write Pydantic schemas defining the specific fields for Logistical Constraints and Creative Constraints.

2.1.2: Build the file management utility to store, read, and validate these YAML constraint sets within a local /constraints directory.

Sprint 2.2: CLI Constraint Management (CRUD)

2.2.1: Add Typer commands to create, list, edit, and delete Constraint Sets.

2.2.2: Implement the set-active command to toggle which Logistical and Creative sets are currently primed for the next generation.
Phase 3: The Friday Night Engine & Prompt Builder
Objective: Capture the ephemeral kickoff data and construct the strict LLM system prompt.

Sprint 3.1: Friday Draw Wizard

3.1.1: Build an interactive terminal wizard using rich.prompt to capture Genre, Character, Prop, and Line.

3.1.2: Implement the "default" fallback logic to auto-generate compliant placeholders if a user leaves a field blank.

Sprint 3.2: Hierarchical Prompt Compiler

3.2.1: Build the PromptBuilder engine that concatenates the Global State, Active Creative Constraints, and Active Logistical Constraints.

3.2.2: Hard-code the Immutable Festival Rules (runtime, verbatim rule, prop usage, character linkage) and append them alongside the Friday Draw at the absolute bottom of the prompt to enforce the Recency Effect.
Phase 4: Inference Engine & Output Versioning
Objective: Connect to the LLM backend and safely store the generated treatments.

Sprint 4.1: AI Provider Integration

4.1.1: Implement the primary API adapter using the google-genai SDK.

4.1.2: Enforce Structured Outputs by passing the TreatmentOutput Pydantic schema to the model.

4.1.3: Build error handling for API timeouts and invalid schema returns.

Sprint 4.2: Output Versioning System

4.2.1: Build the Markdown export utility to convert the structured LLM response into a highly readable formatting standard.

4.2.2: Implement the safe-write system that exports the markdown document to the /outputs directory using a strict, timestamped naming convention (e.g., treatment_v[XX]_[Logistical]_[Creative]_[Timestamp].md).


Developer Diary



