# Implementation Plan - Sprint 7.2: Data Model Refactor & Workspace Enhancements

Executing **Sprint 7.2: Data Model Refactor, Roster Segmentation & Workspace Enhancements**. This sprint stabilizes TUI rendering, refactors `TeamProfile` and `LogisticalConstraint` Pydantic models with backward compatibility, cleans up logistical UI forms, and adds a transient "Additional Instructions" input to the prompt compiler.

## User Review Required

> [!IMPORTANT]
> **Schema Breaking Changes & Migration Strategy**
> 1. `TeamProfile.roles` is renamed to `TeamProfile.crew`. Deserialization logic (via Pydantic `@model_validator(mode="before")`) will automatically map legacy `roles` fields in existing YAML files to `crew`.
> 2. `LogisticalConstraint.main_character_details` is removed and `props_and_dialogue` is renamed to `available_set_dressing`. Deserialization logic will map legacy `props_and_dialogue` to `available_set_dressing`.

## Proposed Changes

---

### Component 1: UI Stabilization (The "Ghosting" Fix)

#### [MODIFY] [workspace.py](file:///home/andrew/48HFP%20App/studio/workspace.py)
- Refactor `RecipePane`:
  - Replace the current `#recipe-content` setup (which relies on `padding-right: 2`) with a container wrapper `#recipe-container` surrounding the `#recipe-content` `Static` widget.
  - Apply CSS width constraints (`width: 100% - 2;` or strict boundary calculations) to prevent text bleeding past the right border.

---

### Component 2: Roster Segmentation & Gear Inventory (`TeamProfile` Refactor)

#### [MODIFY] [profile.py](file:///home/andrew/48HFP%20App/studio/models/profile.py)
- Update `TeamProfile` model:
  - Rename `roles` to `crew: Dict[str, List[str]] = Field(default_factory=dict)`.
  - Add validator to migrate legacy `roles` key in YAML dictionaries to `crew`.
  - Add `cast: List[Dict[str, str]] = Field(default_factory=list)` to hold actor details (`name`, `age_range`, `gender`, `physicality`).
  - Add `available_gear: List[str] = Field(default_factory=list)` to catalog equipment.

#### [MODIFY] [screens.py](file:///home/andrew/48HFP%20App/studio/screens.py)
- Refactor `ProfileSetupScreen`:
  - Split roster UI into distinct tabs or sections:
    - **Crew**: Standard crew roles select, member name input, add/remove controls, and data table.
    - **Cast**: Form inputs for actor Name, Age Range, Gender, Physicality + Data table for cast entries.
    - **Available Gear & Equipment**: `TextArea` widget (`#available_gear`) for entering equipment items.
  - Update `action_save` to map all form inputs into `TeamProfile(crew=..., cast=..., available_gear=...)`.

#### [MODIFY] [ui.py](file:///home/andrew/48HFP%20App/studio/utils/ui.py)
- Update `display_profile_table`:
  - Display Crew roles, Cast roster details, and Available Gear in Rich tables and panels.

#### [MODIFY] [cli.py](file:///home/andrew/48HFP%20App/studio/cli.py) & [tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)
- Update code accessing `profile.roles` to use `profile.crew`.

---

### Component 3: Logistical Schema Cleanup

#### [MODIFY] [constraints.py](file:///home/andrew/48HFP%20App/studio/models/constraints.py)
- Update `LogisticalConstraint` model:
  - Remove `main_character_details` field.
  - Rename `props_and_dialogue` to `available_set_dressing: List[str] = Field(default_factory=list)`.
  - Add deserialization validator to map legacy `props_and_dialogue` fields to `available_set_dressing`.

#### [MODIFY] [screens_constraints.py](file:///home/andrew/48HFP%20App/studio/screens_constraints.py)
- Update `LogisticalConstraintScreen`:
  - Remove Main Character inputs (`#main_char_name`, `#main_char_traits`, `#main_char_wardrobe`, `#main_char_notes`).
  - Rename Props/Dialogue input to "Available Set Dressing & Wardrobe" (`#available_set_dressing`).
  - **Bug Fix**: Ensure `location_details` is extracted from `TextArea("#location_details")` and passed to `LogisticalConstraint(location_details=...)` during `action_save()`.

#### [MODIFY] [ui.py](file:///home/andrew/48HFP%20App/studio/utils/ui.py)
- Update `display_logistical_detail` to display `available_set_dressing` and remove main character section.

---

### Component 4: Transient "Additional Instructions" & Prompt Compiler

#### [MODIFY] [workspace.py](file:///home/andrew/48HFP%20App/studio/workspace.py)
- In `RecipePane`:
  - Add `TextArea(id="additional_instructions")` widget placed below the Recipe Summary and above the "Generate Treatment [G]" button.

#### [MODIFY] [tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)
- In `action_generate_treatment()`:
  - Extract text from `#additional_instructions` `TextArea` in `RecipePane`.
  - Pass as `additional_instructions` argument to `PromptBuilder.compile_system_prompt()`.

#### [MODIFY] [prompt_builder.py](file:///home/andrew/48HFP%20App/studio/utils/prompt_builder.py)
- Update `compile_system_prompt`:
  - Add `additional_instructions: Optional[str] = None` parameter.
  - Update `_build_global_state_section`: include Crew, Cast, and Gear from `TeamProfile`.
  - Update `_build_logistical_section`: remove main character details and format `available_set_dressing`.
  - Inject new section "ADDITIONAL FILMMAKER DIRECTIVES" into the system prompt hierarchy directly above Output Schema Directives (Section 7).

---

### Component 5: Test Suite Updates

#### [NEW] [test_phase7_2.py](file:///home/andrew/48HFP%20App/tests/test_phase7_2.py)
- Create unit & integration test suite covering:
  - `TeamProfile` refactor (`crew`, `cast`, `available_gear`, legacy `roles` validator).
  - `LogisticalConstraint` cleanup (`available_set_dressing`, legacy validator).
  - Modal screen forms (`ProfileSetupScreen`, `LogisticalConstraintScreen`).
  - `location_details` extraction bug fix.
  - `PromptBuilder.compile_system_prompt` with `additional_instructions` section injection.

---

## Verification Plan

### Automated Tests
- Run `pytest tests/test_phase7_2.py` to verify all new unit and integration tests.
- Run full pytest test suite: `pytest tests/` to ensure zero regressions across existing phases.

### Manual Verification
- Launch TUI via `python -m studio.cli` or `48hfp`.
- Open Profile Setup (`[P]`), enter Crew, Cast, and Gear details, save, and verify rendering.
- Open Logistical Constraint modal (`[L]`), enter location details and set dressing, save, and verify.
- Enter additional filmmaker directives into `RecipePane` text area, trigger treatment generation, and verify prompt injection.
