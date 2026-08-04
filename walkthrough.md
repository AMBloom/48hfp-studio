# Walkthrough: Phase 2 - The Unified Constraint System

## Overview
In Phase 2 of **48HFP-Studio**, we implemented the complete modular architecture for managing user-defined **Logistical** and **Creative Constraint Sets**. This provides filmmakers with a hot-swappable, object-oriented framework to define their physical filming reality and directorial vision before AI script treatment generation.

---

## What Was Built

### 1. Sprint 2.1: Constraint Data Models & Cross-Platform Storage

- **Pydantic Schemas ([studio/models/constraints.py](file:///home/andrew/48HFP%20App/studio/models/constraints.py))**:
  - `CharacterDetail`: Character names, actor traits, wardrobe notes, and acting directives.
  - `LogisticalConstraint`: Filming locations, sub-locations, location details (layout/lighting), main character extension, additional cast roster, available props, and dialogue hooks.
  - `CreativeConstraint`: Pre-baked story scenarios, core philosophy & thematic spine, scene economy & pacing directives, progression & climax guidelines, visuals & post-production rules.
  - Name slug validation enforcing valid file-safe identifiers.

- **Global Profile Active Tracking ([studio/models/profile.py](file:///home/andrew/48HFP%20App/studio/models/profile.py))**:
  - Extended `TeamProfile` with `active_logistical_constraint` and `active_creative_constraint` fields to track primed sets across CLI sessions.

- **Dynamic Cross-Platform File Manager ([studio/utils/constraint_store.py](file:///home/andrew/48HFP%20App/studio/utils/constraint_store.py))**:
  - Implemented strictly cross-platform path resolution using `Path.cwd() / "constraints"`.
  - Automatic creation of `./constraints/logistical/` and `./constraints/creative/` directories relative to current working directory.
  - Full CRUD YAML serialization routines (`save`, `load`, `list`, `delete`).
  - **Auto-Seeding**: Automatic generation of starter sets (`interior_indie_crew` and `a24_slow_burn`) if the library is empty.

---

### 2. Sprint 2.2: CLI Constraint Management (CRUD) & Rich UI

- **Rich Terminal UI Components ([studio/utils/ui.py](file:///home/andrew/48HFP%20App/studio/utils/ui.py))**:
  - `display_constraints_table`: Formatted Rich overview table with highlighted `[ACTIVE]` status badges.
  - `display_logistical_detail` & `display_creative_detail`: Comprehensive Rich panels detailing set parameters.

- **Typer Subcommand Group ([studio/constraints.py](file:///home/andrew/48HFP%20App/studio/constraints.py))**:
  - `48hfp constraints list`: Table overview of all sets with active status markers.
  - `48hfp constraints create`: Interactive wizard and flag-driven non-interactive set creator.
  - `48hfp constraints show <name>`: Render detailed breakdown panels.
  - `48hfp constraints edit <name>`: Interactive updater for existing sets.
  - `48hfp constraints delete <name>`: Prompted removal with active state cleanup.
  - `48hfp constraints set-active`: Hot-swap active logistical and creative sets.
  - `48hfp constraints show-active`: View currently primed active sets.

- **Main CLI Integration ([studio/cli.py](file:///home/andrew/48HFP%20App/studio/cli.py))**:
  - Registered `constraints` and `constraint` subcommands.
  - Updated `48hfp info` to display active constraint sets alongside team profile status.

---

## Verification & Testing Highlights

### 1. Auto-Seeding & Set Listing
Executing `python main.py constraints list` automatically seeded starter sets and rendered the library table:
```
                       📦 Unified Constraint Sets Library
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Type         ┃ Name (Slug)              ┃    Status    ┃ Description         ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ Logistical   │ interior_indie_crew      │    ACTIVE    │ Default indoor      │
│              │                          │              │ indie shoot setup   │
│ Creative     │ a24_slow_burn            │    ACTIVE    │ A24-style indie     │
│              │                          │              │ psychological drama │
└──────────────┴──────────────────────────┴──────────────┴─────────────────────┘
```

### 2. Hot-Swapping Active Sets (`set-active`)
Command executed:
```bash
python main.py constraints set-active --logistical interior_indie_crew --creative a24_slow_burn
```
Result: Global profile saved active constraint names and primed generation context.

### 3. Verification of System Information (`info`)
Command executed:
```bash
python main.py info
```
Output verified that global state reflects configured team profile and active primed constraint sets.

### 4. Non-Interactive Set Creation & Deletion
Commands executed:
```bash
python main.py constraints create --type logistical --name desert_motel --description "Gritty roadside motel shoot" --non-interactive
python main.py constraints create --type creative --name thriller_noir --description "Fast paced crime thriller" --non-interactive
python main.py constraints delete desert_motel --type logistical --force
python main.py constraints delete thriller_noir --type creative --force
```
Result: All files were created in `./constraints/logistical/` and `./constraints/creative/`, validated against Pydantic schemas, listed in the library table, and safely deleted.
