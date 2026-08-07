# Implementation Plan - Sprint 6.2: In-TUI Friday Draw Wizard & Profile Setup Modals

**Sprint Goal:** Build interactive Textual `ModalScreen` dialogs for entry/editing of the Friday Night Draw (`DrawWizardScreen`) and Team Profile (`ProfileSetupScreen`), integrating them seamlessly into `studio/tui.py` for live reactive state updates and persistent storage.

---

## Proposed Required Changes

### 1. New Screens Module (`studio/screens.py`)
- Create `studio/screens.py` to house all Textual modal screens and keep `studio/tui.py` clean.
- Implement `DrawWizardScreen(ModalScreen[Optional[FridayDraw]])`:
  - Centered modal card layout with CSS styling.
  - Form widgets:
    - Primary Genre: Textual `Select` widget pre-populated with `GENRES_GROUP_1` options from `studio.models.draw`.
    - Secondary Genre: Textual `Select` widget pre-populated with `GENRES_GROUP_2` options from `studio.models.draw`.
    - Character Name: Textual `Input` widget.
    - Character Trait: Textual `Input` widget.
    - Character Gender: Textual `Input` widget (default placeholder "Any / Unspecified").
    - Required Prop: Textual `Input` widget.
    - Verbatim Line: Textual `Input` widget.
  - Controls: "Save" button (`#save_draw_btn`) and "Cancel" button (`#cancel_draw_btn`).
  - Pre-fill logic: Populate input/select values if an existing `FridayDraw` object is provided in `__init__`.
  - Save Logic:
    - Collect input values from form controls.
    - Validate and pass empty fields through `create_default_draw(...)` from `studio.models.draw` to ensure random fallback placeholders are applied for blank inputs.
    - Persist the validated `FridayDraw` instance using `save_draw(draw)` from `studio.utils.draw_store`.
    - Dismiss the screen returning the updated `FridayDraw`: `self.dismiss(draw)`.
  - Cancel Logic: Dismiss screen returning `None`: `self.dismiss(None)`.

- Implement `ProfileSetupScreen(ModalScreen[Optional[TeamProfile]])`:
  - Centered modal card layout with CSS styling.
  - Form widgets:
    - Team Name: Textual `Input` widget.
    - Admin Username: Textual `Input` widget.
    - Location: Textual `Input` widget.
  - Controls: "Save" button (`#save_profile_btn`) and "Cancel" button (`#cancel_profile_btn`).
  - Pre-fill logic: Populate input fields if an existing `TeamProfile` object is provided in `__init__`.
  - Save Logic:
    - Collect input values from form controls.
    - Construct or update `TeamProfile` object (preserving existing roles, custom details, and active constraint sets if updating).
    - Persist profile using `save_profile(profile)` from `studio.utils.profile_store`.
    - Dismiss the screen returning updated `TeamProfile`: `self.dismiss(profile)`.
  - Cancel Logic: Dismiss screen returning `None`: `self.dismiss(None)`.

### 2. TUI Integration (`studio/tui.py`)
- Import `DrawWizardScreen` and `ProfileSetupScreen` from `studio.screens`.
- Update `StudioApp` keybindings:
  - Add `("d", "open_draw_wizard", "Friday Draw")`
  - Add `("p", "open_profile_setup", "Profile Setup")`
- Add screen push actions to `StudioApp`:
  - `action_open_draw_wizard()`: Executes `self.push_screen(DrawWizardScreen(self.app_draw), callback=self.update_draw)`.
  - `action_open_profile_setup()`: Executes `self.push_screen(ProfileSetupScreen(self.app_profile), callback=self.update_profile)`.
- Implement callback handler methods in `StudioApp`:
  - `update_draw(self, new_draw: Optional[FridayDraw]) -> None`: Updates `self.app_draw = new_draw` if `new_draw` is not `None`, triggering reactive state cascade.
  - `update_profile(self, new_profile: Optional[TeamProfile]) -> None`: Updates `self.app_profile = new_profile` if `new_profile` is not `None`, triggering reactive state cascade.
- Add physical buttons to `NavigationSidebar` / `StudioWorkspace` so users can trigger modals via mouse click or hotkeys.

### 3. Test Suite (`tests/test_phase6_2.py`)
- Create unit tests for screen modals and TUI integration:
  - `test_draw_wizard_screen_save`: Verify form completion, fallback execution via `create_default_draw`, persistence via `save_draw`, and dismissal returning updated `FridayDraw`.
  - `test_draw_wizard_screen_cancel`: Verify cancel dismissal returning `None`.
  - `test_profile_setup_screen_save`: Verify profile input collection, persistence via `save_profile`, and dismissal returning updated `TeamProfile`.
  - `test_profile_setup_screen_cancel`: Verify cancel dismissal returning `None`.
  - `test_tui_modal_launch_and_callbacks`: Verify modal screen push from `StudioApp`, callback execution, and reactive UI updates.

---

## User Review Required

> [!IMPORTANT]
> - **Fallback Validation:** Any blank fields submitted in the Friday Draw Wizard will automatically be populated using `create_default_draw(...)` fallbacks, guaranteeing valid `FridayDraw` schemas.
> - **State Preservation:** Saving profile updates preserves existing team roles, custom details, and active constraint selections.
> - **Reactive Cascading:** Modals pass updated objects back via callbacks to `StudioApp`, which updates `self.app_draw` or `self.app_profile` to automatically update all child HUD, Sidebar, and Workspace widgets.

---

## Proposed Changes

### Component 1: TUI Screens Module

#### [NEW] [screens.py](file:///home/andrew/48HFP%20App/studio/screens.py)
- Implement `DrawWizardScreen` and `ProfileSetupScreen` classes inheriting from `textual.screen.ModalScreen`.

### Component 2: TUI Integration

#### [MODIFY] [tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)
- Import modal screens from `studio.screens`.
- Add bindings `d` (Friday Draw) and `p` (Profile Setup).
- Implement `action_open_draw_wizard`, `action_open_profile_setup`, `update_draw`, and `update_profile`.
- Add interactive buttons to `NavigationSidebar` / `StudioWorkspace` to open modals.

### Component 3: Test Suite

#### [NEW] [test_phase6_2.py](file:///home/andrew/48HFP%20App/tests/test_phase6_2.py)
- Add comprehensive pytest suite testing modal rendering, form submissions, fallback handling, file saving, and TUI callback reactivity.

---

## Verification Plan

### Automated Tests
- Run `pytest tests/test_phase6_2.py` using Textual pilot driver.
- Run full test suite `pytest` across all project tests to verify zero regressions.

### Manual Verification
- Launch TUI via `python main.py` or `48hfp tui`.
- Press `P` or click Profile Setup button, fill in fields, save, and verify sidebar HUD updates in real-time.
- Press `D` or click Friday Draw button, fill in fields (leaving some blank to test fallbacks), save, and verify workspace HUD updates in real-time.
