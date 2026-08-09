# 48HFP-Studio: Master Application Bible (v3.0.0 - Studio-in-a-Box Edition)

## 1. Project Overview & Vision
48HFP-Studio is an open-source, terminal-native AI co-pilot designed for indie film teams. Transitioned in v3.0 to a comprehensive "Studio-in-a-Box," the application manages the entire pre-production workflow: from concept ideation and interactive onboarding to treatment generation, scriptwriting, and production asset creation (shot lists and storyboards). 

It operates via a Textual-powered stateful Terminal User Interface (TUI) with a split-pane dashboard, while maintaining headless CLI subcommands. The engine generates deterministic, 100% compliant outputs by ingesting modular, user-defined "Constraint Sets" alongside the official Friday Night Draw.

## 2. Environment & Tech Stack
*   **Target OS:** Cross-platform (Developed on Ubuntu 24.04 LTS)
*   **Runtime:** Python 3.11+
*   **Frameworks:** `textual` (TUI dashboard), `typer` (CLI routing), `rich` (terminal UI)
*   **Data Validation:** `pydantic` v2
*   **Storage:** `PyYAML` (human-readable config/constraint files)
*   **LLM Orchestration:** `google-genai` SDK (Primary text inference). 
*   **Data Output:** `pandas` (for spreadsheet/shot list generation), standard `.fountain` (plain-text screenplays).

## 3. Global State & Persistent Workspaces
The application relies on persistent workspaces to allow portability across devices.
*   **Team Profile:** (`~/.48hfp_profile.yaml`) Stores Team Name, Admin, Location, segmented Crew and Cast rosters (with physical descriptions), and an Available Gear catalog.
*   **Project Workspaces:** A sandboxed environment system to store specific constraints, draws, treatments, and scripts together.

## 4. The Unified Constraint Architecture
Generative inputs are treated as modular "Constraint Sets."
*   **A. Immutable Festival Rules:** Hard-coded engine constraints (4-7 min runtime, required prop usage, verbatim dialog rule, required character linkage).
*   **B. Logistical Constraints:** Physical shoot reality (locations, available set dressing/wardrobe).
*   **C. Directorial Vision:** Visual economy, lighting/color intent, and audio landscape.
*   **D. Thematic Framework:** Core philosophy, emotional arc, and world rules.
*   **E. Idea Seeds:** Inciting incident, complications, and ending targets.
*   **F. The Friday Night Draw:** Ephemeral kickoff data (Genres, Character, Prop, Line).

## 5. Prompt Engineering & Inference Architecture
The System Prompt Builder enforces **The Recency Effect**. LLMs prioritize instructions at the bottom of the prompt.
*   **Hierarchy:** Persona -> Global State (Crew/Cast/Gear) -> Directorial Vision -> Thematic Framework -> Idea Seed -> Logistical Constraints -> Transient User Directives -> Output Schema -> Friday Draw -> **Immutable Rules (The Anchor)**.

## 6. Output Versioning & File System
To protect against data loss during a 48-hour sprint, the app never overwrites previous outputs. 
*   Files are automatically named using the active constraint sets and a timestamp: `treatment_v[XX]_[Title]_[Logistical]_[Directorial]_[Thematic]_[Idea]_[Timestamp].md`.

---

## Development Roadmap (v3.x)

### ✅ Completed Phases (v1.0 - v2.0)
*   **Phase 1-4:** Core CLI Scaffolding, PyYAML Data Models, Friday Draw Wizard, Hierarchical Prompt Compiler, and Gemini Inference Engine.
*   **Phase 5-6:** Textual TUI Scaffolding, Live Widget Binding, Modal Forms, and Split-Pane Workspace.
*   **Phase 7:** Tri-Split Architecture (Directorial, Thematic, Idea Seed refactor), Cast/Crew Segmentation, Gear Inventory, and UI Stabilization.

### 🚀 Current Expansion: Studio-in-a-Box (v3.0+)

**Phase 8: Project Workspaces & Interactive Onboarding**
*   **Sprint 8.1:** Persistent Project Setup (Transitioning from a global default sandbox to named project directories for portability).
*   **Sprint 8.2:** The Filmmaker Personality Quiz (Curating ~12 visionary director archetypes and routing users to default constraint sets via a gamified onboarding wizard).

**Phase 9: Iterative Development**
*   **Sprint 9.1:** Treatment Revision Engine (Allowing users to modify a generated treatment via conversational change requests while enforcing the exact Pydantic output schema).

**Phase 10: The Screenplay Engine**
*   **Sprint 10.1:** Generative Screenplays (Feeding the locked treatment + constraints to generate a working draft).
*   **Sprint 10.2:** Fountain Format Integration (Standardizing on the open-source `.fountain` format for plain-text screenwriting, allowing export/import to industry-standard software without PDF parsing nightmares).

**Phase 11: Production Assets**
*   **Sprint 11.1:** StudioBinder Shot Lists (Parsing the screenplay and constraints to output an actionable `.xlsx`/`.csv` shot list using Pandas).
*   **Sprint 11.2:** Pre-Vis Storyboarding (Generating highly constrained, 16:9 monochrome "pre-vis" image prompts and compiling them into a local HTML viewer).