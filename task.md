# Task Checklist - Sprint 6.2: In-TUI Friday Draw Wizard & Profile Setup Modals

- [x] Component 1: Create `studio/screens.py` modal screens
  - [x] Implement `DrawWizardScreen` modal form with genre `Select` and `Input` fields
  - [x] Implement `ProfileSetupScreen` modal form with profile `Input` fields
  - [x] Add save validation, fallback handling (`create_default_draw`), file storage calls (`save_draw`, `save_profile`), and screen dismissal callbacks
- [x] Component 2: Integrate modal screens into `studio/tui.py`
  - [x] Import screens into `studio/tui.py`
  - [x] Add key bindings (`d` for Draw Wizard, `p` for Profile Setup)
  - [x] Add physical trigger buttons or action links in `NavigationSidebar` / `StudioWorkspace`
  - [x] Implement screen push actions (`action_open_draw_wizard`, `action_open_profile_setup`)
  - [x] Implement callback handlers (`update_draw`, `update_profile`) to update reactive app state
- [x] Component 3: Build automated tests in `tests/test_phase6_2.py`
  - [x] Test `DrawWizardScreen` form submission, fallbacks, saving, and cancellation
  - [x] Test `ProfileSetupScreen` form submission, saving, and cancellation
  - [x] Test TUI integration, screen pushing, callbacks, and reactive state updates
- [x] Component 4: Verification & Walkthrough
  - [x] Run `pytest tests/test_phase6_2.py` and full `pytest` suite (33 passed)
  - [x] Update `walkthrough.md` with results
