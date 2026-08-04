# Walkthrough: Phase 3 - The Friday Night Engine & Prompt Builder

## Overview
In Phase 3 of **48HFP-Studio**, we constructed the kickoff data capture system (**Friday Draw Wizard**) and the **Hierarchical Prompt Compiler** (`PromptBuilder`). The prompt compiler enforces **The Recency Effect** by placing Immutable Festival Rules alongside kickoff parameters at the absolute bottom of the generated system prompt to guarantee LLM compliance during script treatment generation.

---

## What Was Built

### 1. Sprint 3.1: Friday Draw Kickoff Engine & Persistence

- **Pydantic Data Model & Strict Genre Pools ([studio/models/draw.py](file:///home/andrew/48HFP%20App/studio/models/draw.py))**:
  - `FridayDraw`: Pydantic schema validating `genre_1`, `genre_2`, `character_name`, `character_trait`, `character_gender`, `required_prop`, and `required_line`.
  - `GENRES_GROUP_1` (15 exact genres): *Action / Adventure, Comedy, Dark Comedy, Drama, Fantasy, Film de Femme, Film Noir, Fish Out of Water, Horror, Mockumentary, Musical, Road Movie, Romance, Sci Fi, Thriller / Suspense*.
  - `GENRES_GROUP_2` (15 exact genres): *Buddy Film, Family Film, Food Film, Heist, Inspirational Film, Misunderstanding, Moral Dilemma, Revenge, Romantic Comedy, Silent Film, Single Room Movie, Sports Film / Game Film, Utopian or Dystopian, Vacation / Holiday Film, Workplace Film*.
  - `create_default_draw()`: Smart default fallback generator that fills blank or omitted fields with compliant placeholders or random valid selections from the genre pools.

- **Persistent Kickoff Storage ([studio/utils/draw_store.py](file:///home/andrew/48HFP%20App/studio/utils/draw_store.py))**:
  - `load_draw()`, `save_draw()`, `draw_exists()`, `delete_draw()` for YAML serialization to/from `~/.48hfp_draw.yaml`.

- **Interactive Kickoff Wizard & CLI Subcommands ([studio/draw.py](file:///home/andrew/48HFP%20App/studio/draw.py))**:
  - `48hfp draw wizard`: Interactive terminal wizard featuring styled `rich.prompt.Prompt` selection for Group 1 & Group 2 genres, character details, prop, and dialogue line. Supports `--non-interactive` execution for automated workflows.
  - `48hfp draw show`: Displays active Friday Draw parameters in formatted Rich tables.
  - `48hfp draw reset`: Prompted removal of saved kickoff data.
  - `48hfp draw prompt`: Compiles and previews the full system prompt.

---

### 2. Sprint 3.2: Hierarchical Prompt Compiler & Recency Effect

- **System Prompt Builder Engine ([studio/utils/prompt_builder.py](file:///home/andrew/48HFP%20App/studio/utils/prompt_builder.py))**:
  - Implemented `PromptBuilder.compile_system_prompt()` concatenating global team state, active logistical set, active creative set, output schema, and kickoff data in a strict prompt injection hierarchy.
  - **The Recency Effect Implementation**: Anchors the **Immutable Festival Rules** (4–7 min runtime target, verbatim dialogue rule, active prop usage, and character linkage) at the **absolute bottom** of the compiled prompt to ensure LLM prioritization above creative guidelines.

---

### 3. Rich UI & CLI System Integration

- **Rich Formatting Helpers ([studio/utils/ui.py](file:///home/andrew/48HFP%20App/studio/utils/ui.py))**:
  - `display_draw_table`: Renders formatted summary table of kickoff draw inputs.
  - `display_prompt_panel`: Formatted preview container for inspecting compiled system prompts.

- **Main CLI Application ([studio/cli.py](file:///home/andrew/48HFP%20App/studio/cli.py))**:
  - Registered `draw` subcommand group.
  - Registered root `48hfp prompt` command to compile and inspect the system prompt.
  - Updated `48hfp info` command to render Friday Draw Kickoff status alongside team profile and active constraints readiness.

---

## Verification & Testing Highlights

### 1. Automated Unit Test Suite (`tests/test_phase3.py`)
Executed test suite covering genre pool validation, fallback generation, YAML persistence, and prompt compiler hierarchy:
```bash
python3 -m pytest tests/test_phase3.py
```
Output:
```
============================== 4 passed in 0.03s ===============================
```

### 2. Friday Draw Non-Interactive Kickoff
Command executed:
```bash
python main.py draw wizard --genre1 "Sci Fi" --genre2 "Heist" --character-name "John Miller" --character-trait "Cyberneticist" --character-gender "Male" --prop "Glowing USB drive" --line "The vault opens at midnight." --non-interactive
```
Result: Successfully recorded kickoff parameters to `~/.48hfp_draw.yaml` and displayed formatted kickoff summary table.

### 3. Kickoff Draw Display (`48hfp draw show`)
Command executed:
```bash
python main.py draw show
```
Result:
```
              🎲 Friday Night Draw Kickoff Data
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Constraint Category      ┃ Draw Value                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Primary Genre (Group 1)  │ Sci Fi                         │
│ Secondary Genre (Group 2)│ Heist                          │
│ Required Character Name  │ John Miller                    │
│ Character Trait/Prof.    │ Cyberneticist                  │
│ Character Gender/Sex     │ Male                           │
│ Required Prop            │ Glowing USB drive              │
│ Required Verbatim Line   │ "The vault opens at midnight." │
└──────────────────────────┴────────────────────────────────┘
```

### 4. Prompt Compilation & Recency Effect Inspection (`48hfp prompt`)
Command executed:
```bash
python main.py prompt
```
Result: Successfully compiled system prompt displaying Team Profile, Active Logistical (`interior_indie_crew`), Active Creative (`a24_slow_burn`), Schema Directives, Friday Draw Kickoff, and **Immutable Festival Rules anchored at the absolute bottom**.

### 5. System Status Inspection (`48hfp info`)
Command executed:
```bash
python main.py info
```
Result: System overview panel verified complete readiness across Profile (Configured), Active Constraints (Primed), and Friday Draw Kickoff (Recorded).
