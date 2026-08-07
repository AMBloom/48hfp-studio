# Implementation Plan - Sprint 6.3: In-TUI Treatment Generator & Split-Pane Workspace

Connect the AI `InferenceEngine` to the Textual TUI via non-blocking background workers and build out a split-pane Markdown previewer workspace.

## User Review Required

> [!IMPORTANT]
> - **Module Refactoring:** The existing `StudioWorkspace` widget in `studio/tui.py` will be moved to a dedicated module `studio/workspace.py` to maintain modular separation of concerns. `studio/tui.py` will remain focused on application routing and state distribution.
> - **Async Background Worker:** AI inference and filesystem I/O operations will run in a Textual background thread via `@work(thread=True)` decorator to ensure the TUI UI loop never freezes or stutters during API generation calls.

## Open Questions

- None. Requirements and interfaces align with previous sprint architectures.

## Proposed Changes

### 1. New Workspace Module (`studio/workspace.py`)

#### [NEW] [workspace.py](file:///home/andrew/48HFP%20App/studio/workspace.py)
Create `studio/workspace.py` containing three primary Textual widgets:

- **`RecipePane(Static)` (Left Split):**
  - Displays summary of active `TeamProfile` constraints (Logistical, Creative, Location) and `FridayDraw` parameters (Genres, Character, Prop, Line).
  - Includes a `Button("⚡ Generate Treatment [G]", id="btn_generate_treatment", variant="success")`.
  - Disables button and displays generating status when `is_generating` reactive is True.

- **`OutputPane(Static)` (Right Split):**
  - Contains Textual `LoadingIndicator(id="treatment-loading")` and `Markdown(id="treatment-markdown")`.
  - Displays `LoadingIndicator` during active API generation calls (`is_generating == True`).
  - Displays formatted Markdown treatment content when generation completes.
  - Watches `markdown_text` reactive property to dynamically update the `Markdown` widget.

- **`StudioWorkspace(Static)` (Parent Split-Pane Container):**
  - Wraps `RecipePane` and `OutputPane` inside a horizontal container (`#split-workspace`).
  - Distributes reactive properties (`profile`, `draw`, `markdown_text`, `is_generating`) to child panes.

---

### 2. TUI Application Integration (`studio/tui.py`)

#### [MODIFY] [tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)
- Import `StudioWorkspace` from `studio.workspace`.
- Add keybinding `("g", "generate_treatment", "Generate Treatment")` to `StudioApp.BINDINGS`.
- Add reactives `current_markdown: reactive[str]` and `is_generating: reactive[bool]` to `StudioApp`.
- Add `@work(thread=True)` decorated method `action_generate_treatment()`:
  - Sets `is_generating = True`.
  - Compiles system prompt via `PromptBuilder.compile_system_prompt()`.
  - Invokes `InferenceEngine.generate_treatment(prompt=prompt)`.
  - Exports treatment file via `save_treatment_output()`.
  - Converts treatment to markdown using `convert_treatment_to_markdown()`.
  - Uses `self.call_from_thread()` to safely update UI state on the main thread upon completion or error.
  - Catches `InferenceError` and updates `current_markdown` with formatted error message and triggers a notification.
- Wire button handler `on_button_pressed()` to trigger `action_generate_treatment()` when `btn_generate_treatment` is pressed.

---

### 3. Test Suite (`tests/test_phase6_3.py`)

#### [NEW] [test_phase6_3.py](file:///home/andrew/48HFP%20App/tests/test_phase6_3.py)
- `test_workspace_rendering`: Verifies rendering of `StudioWorkspace`, `RecipePane`, and `OutputPane` with active profile & draw state.
- `test_action_generate_treatment_success`: Mocks `InferenceEngine.generate_treatment` and `save_treatment_output`, executes worker thread, and verifies markdown reactive updates and UI state changes.
- `test_action_generate_treatment_inference_error`: Mocks `InferenceEngine.generate_treatment` to raise `InferenceError`, ensuring error markdown is rendered and app remains stable.
- `test_generate_button_event_trigger`: Verifies clicking `btn_generate_treatment` fires `action_generate_treatment`.

## Verification Plan

### Automated Tests
- Run `pytest tests/test_phase6_3.py` to verify async worker execution, split-pane reactivity, and error handling.
- Run `pytest` across full test suite (`test_phase*.py`) to ensure no regressions in existing TUI screens, CLI, or inference modules.

### Manual Verification
- Test keybinding `G` and button click in Textual TUI.
- Confirm split-pane layout correctly renders recipe summary on left and treatment markdown / loading indicator on right.
