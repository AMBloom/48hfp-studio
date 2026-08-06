# Walkthrough - Sprint 5.4: v2.0 Roadmap & Textual Scaffolding

Sprint 5.4 transitions **48HFP-Studio** from a linear CLI to a stateful Terminal User Interface (TUI) powered by the `textual` framework.

## Key Changes Executed

### 1. Master Application Bible Updates
* Updated [PROJECT_INSTRUCTIONS.md](file:///home/andrew/48HFP%20App/PROJECT_INSTRUCTIONS.md) header to **v2.0 - TUI Edition**.
* Documented transition to a split-pane dashboard workspace while keeping headless CLI subcommands intact.
* Added `textual` to tech stack and appended **Phase 5 (Textual Scaffolding)** and **Phase 6 (Stateful Library)** to the development roadmap.

### 2. Dependency Management
* Updated [requirements.txt](file:///home/andrew/48HFP%20App/requirements.txt) with `textual>=0.40.0`.
* Updated [pyproject.toml](file:///home/andrew/48HFP%20App/pyproject.toml) `dependencies` array with `"textual>=0.40.0"`.
* Installed `textual` (v8.2.8) in local Python environment via `pip install -r requirements.txt`.

### 3. TUI Scaffolding & Layout Architecture
* Created [studio/tui.py](file:///home/andrew/48HFP%20App/studio/tui.py) containing:
  * `StudioApp` inheriting from `textual.app.App`.
  * CSS layout defining a 3-zone structure (Header HUD, Left Navigation Sidebar, Main Content Studio Workspace).
  * `HeaderHUD`: Persistent header displaying `"🎬 48HFP-Studio v2.0"`.
  * `NavigationSidebar`: Persistent 30-col sidebar displaying navigation stubs.
  * `StudioWorkspace`: Main content workspace displaying welcome details and status stubs.

### 4. CLI Root Integration
* Updated [studio/cli.py](file:///home/andrew/48HFP%20App/studio/cli.py) root callback `main()`:
  * Root invocation (`python main.py` or `48hfp`) instantiates and launches `StudioApp().run()`.
  * Preserved `if ctx.invoked_subcommand is not None: return` bypass so headless subcommands (`python main.py info`, `generate`, etc.) execute without starting the TUI.

### 5. Automated Test Suite
* Updated [tests/test_phase5_2.py](file:///home/andrew/48HFP%20App/tests/test_phase5_2.py) to assert `StudioApp.run()` launch on root invocation and subcommand bypass.
* Created [tests/test_phase5_4.py](file:///home/andrew/48HFP%20App/tests/test_phase5_4.py) testing `StudioApp` title, widget composition via Textual's test driver (`run_test`), and CLI integration.

---

## Verification Results

### Automated Tests
Ran `python -m pytest`:
```text
============================== 23 passed in 1.28s ==============================
```
All 23 unit tests across all test suites passed cleanly.
