# Sprint 7.2 Walkthrough - Data Model Refactor & Workspace Enhancements

## Overview
Sprint 7.2 delivers UI rendering stabilization, Pydantic data model refactoring for production teams and logistical constraints, interactive modal enhancements, transient prompt directive injection, and comprehensive unit/integration test coverage.

## Key Changes Executed

### 1. UI Stabilization (The "Ghosting" Fix)
- **[workspace.py](file:///home/andrew/48HFP%20App/studio/workspace.py)**: Wrapped `#recipe-content` inside a dedicated `#recipe-scroll` `VerticalScroll` container with explicit width constraints (`width: 100% - 2;`). This enforces a strict rendering boundary that prevents recipe text from ghosting or bleeding past the right border.

### 2. Roster Segmentation & Gear Inventory (`TeamProfile` Refactor)
- **[profile.py](file:///home/andrew/48HFP%20App/studio/models/profile.py)**:
  - Renamed `roles` to `crew: Dict[str, List[str]]`.
  - Added `@model_validator(mode="before")` to automatically migrate legacy `roles` fields in YAML profiles to `crew`.
  - Added `.roles` backward-compatibility property.
  - Added `cast: List[Dict[str, str]]` (storing `name`, `age_range`, `gender`, `physicality`).
  - Added `available_gear: List[str]` catalog.
- **[screens.py](file:///home/andrew/48HFP%20App/studio/screens.py)**: Refactored `ProfileSetupScreen`:
  - Separate **Crew Roster Builder** section with role selection, member name input, and crew `DataTable`.
  - Separate **Cast Roster Builder** section with 4 distinct data inputs (`Name`, `Age Range`, `Gender`, `Physicality`) and dedicated cast `DataTable`.
  - Dedicated `TextArea` widget for cataloging **Available Gear & Equipment**.
- **[ui.py](file:///home/andrew/48HFP%20App/studio/utils/ui.py)**: Updated `display_profile_table` to render Crew, Cast, and Gear tables/panels.

### 3. Logistical Schema Cleanup
- **[constraints.py](file:///home/andrew/48HFP%20App/studio/models/constraints.py)**:
  - Removed obsolete `main_character_details` field.
  - Renamed `props_and_dialogue` to `available_set_dressing: List[str]`.
  - Added `@model_validator(mode="before")` for smooth deserialization of legacy constraint files.
  - Added `.props_and_dialogue` backward-compatibility property.
- **[screens_constraints.py](file:///home/andrew/48HFP%20App/studio/screens_constraints.py)**:
  - Removed main character inputs from `LogisticalConstraintScreen`.
  - Renamed props input to "Available Set Dressing & Wardrobe".
  - **Bug Fix**: Extracted `location_details` from `TextArea("#location_details")` during `action_save()`.
- **[ui.py](file:///home/andrew/48HFP%20App/studio/utils/ui.py)**: Updated `display_logistical_detail` to display set dressing and remove main character section.

### 4. Transient "Additional Instructions" & Prompt Compiler
- **[workspace.py](file:///home/andrew/48HFP%20App/studio/workspace.py)**: Added `TextArea(id="additional_instructions")` widget with fixed height (`height: 5; max-height: 6;`) to prevent overflowing the "Generate Treatment" button.
- **[tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)**: Updated `action_generate_treatment()` to query the `#additional_instructions` text from `RecipePane` and pass it to the compiler.
- **[prompt_builder.py](file:///home/andrew/48HFP%20App/studio/utils/prompt_builder.py)**:
  - Updated `compile_system_prompt()` to accept `additional_instructions: Optional[str] = None`.
  - If provided and non-empty, injects a new `ADDITIONAL FILMMAKER DIRECTIVES` section into the prompt hierarchy directly above Output Schema Directives.
  - If `additional_instructions` is empty or only whitespace, the section is completely omitted from the prompt to conserve tokens.
  - Updated global state and logistical sections to format Crew, Cast, Gear, and Set Dressing.

### 5. Test Suite Updates
- **[test_phase7_2.py](file:///home/andrew/48HFP%20App/tests/test_phase7_2.py)**: Added 7 unit and async pilot integration tests.
  - Verification: All 41 unit and integration tests across the entire test suite passed cleanly (`41 passed in 4.70s`).

---

## Verification Results

```bash
$ pytest tests/
============================== 41 passed in 4.70s ==============================
```
