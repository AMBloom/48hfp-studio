# Implementation Plan - Sprint 6.4: In-TUI Constraint Library Management (CRUD)

This plan outlines the implementation of interactive modal screens for creating, editing, viewing, and managing Logistical and Creative Constraint Sets within the Textual TUI of 48HFP-Studio.

## Proposed Changes

### 1. New Module (`studio/screens_constraints.py`)
Create interactive modal screens for individual constraint data entry and editing.

#### [NEW] [screens_constraints.py](file:///home/andrew/48HFP%20App/studio/screens_constraints.py)
* **`LogisticalConstraintScreen(ModalScreen[Optional[LogisticalConstraint]])`**:
  * Constructor accepts `constraint: Optional[LogisticalConstraint] = None` for editing existing sets.
  * Form inputs for:
    * `name` (`Input`): Slug identifier (e.g., `interior_indie_crew`).
    * `description` (`Input`): Brief summary of logistical setup.
    * `locations` (`Input`): Comma-separated location strings.
    * `sub_locations` (`Input`): Comma-separated sub-location strings.
    * `location_details` (`TextArea`): Details on layout, lighting, restrictions.
    * `main_character` details (`Input` / `TextArea` for name, actor traits, wardrobe, notes).
    * `props_and_dialogue` (`TextArea`): Newline-separated props or dialogue lines.
  * Buttons: "Save Logistical Constraint" (`#save_logistical_btn`) and "Cancel" (`#cancel_logistical_btn`).
  * On save: Validates inputs, constructs `LogisticalConstraint`, calls `save_logistical_constraint()`, and dismisses with the saved object.
  * On cancel/escape: Dismisses with `None`.

* **`CreativeConstraintScreen(ModalScreen[Optional[CreativeConstraint]])`**:
  * Constructor accepts `constraint: Optional[CreativeConstraint] = None`.
  * Form inputs for:
    * `name` (`Input`): Slug identifier (e.g., `a24_slow_burn`).
    * `description` (`Input`): Brief summary of creative vision.
    * `scenarios` (`TextArea`): Newline-separated short story scenario ideas.
    * `core_philosophy` (`TextArea`): Thematic spine and directorial motivation.
    * `scene_economy` (`TextArea`): Pacing directives (long takes, editing style).
    * `progression_and_climax` (`TextArea`): Narrative structure and emotional arc.
    * `visuals_and_post` (`TextArea`): Color grading, aspect ratio, scoring intent.
  * Buttons: "Save Creative Constraint" (`#save_creative_btn`) and "Cancel" (`#cancel_creative_btn`).
  * On save: Validates inputs, constructs `CreativeConstraint`, calls `save_creative_constraint()`, and dismisses with the saved object.
  * On cancel/escape: Dismisses with `None`.

---

### 2. New Module (`studio/screens_library.py`)
Create the central library viewer modal for managing and assigning active constraint sets.

#### [NEW] [screens_library.py](file:///home/andrew/48HFP%20App/studio/screens_library.py)
* **`ConstraintLibraryScreen(ModalScreen[Optional[TeamProfile]])`**:
  * Constructor accepts `current_profile: Optional[TeamProfile] = None`.
  * Display Layout: Split layout using two `DataTable` widgets:
    * `#logistical_table`: Columns for Name, Locations, Details, Active Status (`[ACTIVE]`).
    * `#creative_table`: Columns for Name, Core Philosophy, Scene Economy, Active Status (`[ACTIVE]`).
  * Action Toolbar Buttons:
    * "New Logistical" (`#btn_new_logistical`): Pushes `LogisticalConstraintScreen()`. Callback refreshes tables.
    * "New Creative" (`#btn_new_creative`): Pushes `CreativeConstraintScreen()`. Callback refreshes tables.
    * "Edit Selected" (`#btn_edit_selected`): Identifies active selection, loads model from `constraint_store`, pushes modal screen with pre-filled instance. Callback refreshes tables.
    * "Delete Selected" (`#btn_delete_selected`): Prompts/deletes via `delete_logistical_constraint()` or `delete_creative_constraint()`. If deleted item was active, clears active constraint in profile and calls `save_profile()`.
    * "Set Active" (`#btn_set_active`): Updates `current_profile` with active constraint name for selected type, calls `save_profile()`, updates active indicators in data tables, and notifies user.
    * "Close" (`#btn_close_library`): Dismisses screen returning `current_profile`.

---

### 3. TUI Integration (`studio/tui.py` & `studio/workspace.py`)
Wire the new library screen into the main Textual application layout and bindings.

#### [MODIFY] [tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)
* Import `ConstraintLibraryScreen` from `studio.screens_library`.
* Add keybinding `("l", "open_library", "Constraint Library")` to `StudioApp.BINDINGS`.
* Update `NavigationSidebar`:
  * Add trigger button `Button("📚 Constraints [L]", id="btn_library_modal", variant="default")`.
* Implement `action_open_library()` in `StudioApp`:
  ```python
  def action_open_library(self) -> None:
      self.push_screen(ConstraintLibraryScreen(self.app_profile), callback=self.update_profile)
  ```
* Update `on_button_pressed` handler in `StudioApp` and `NavigationSidebar` to catch `btn_library_modal`.

---

### 4. Test Suite (`tests/test_phase6_4.py`)
Create unit test suite covering modal form submission, data persistence, and active assignment routing.

#### [NEW] [test_phase6_4.py](file:///home/andrew/48HFP%20App/tests/test_phase6_4.py)
* `test_logistical_constraint_screen_save_and_cancel()`: Form input, validation, YAML store saving, and screen dismissal.
* `test_creative_constraint_screen_save_and_cancel()`: Form input, validation, YAML store saving, and screen dismissal.
* `test_constraint_library_screen_rendering()`: Verify `DataTable` populates with saved logistical and creative sets.
* `test_constraint_library_set_active()`: Test selecting a constraint set, clicking "Set Active", verifying `app_profile` update and persistence.
* `test_constraint_library_delete()`: Verify deletion removes constraint file and clears active profile references if active.
* `test_tui_integration_library_keybinding()`: Verify opening library via `L` keypress and `action_open_library()`.

---

## Verification Plan

### Automated Tests
- Run `python -m pytest` to execute the full test suite including `tests/test_phase6_4.py`.
