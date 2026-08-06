# Implementation Plan - Sprint 5.4: v2.0 Roadmap & Textual Scaffolding

This implementation plan details the sequence for transitioning 48HFP-Studio from a linear CLI to a stateful Terminal User Interface (TUI) powered by the `textual` framework.

## Proposed Changes

---

### Step 1: Project Instructions Update

#### [MODIFY] [PROJECT_INSTRUCTIONS.md](file:///home/andrew/48HFP%20App/PROJECT_INSTRUCTIONS.md)
* Rewrite header to **48HFP-Studio: Master Application Bible (v2.0 - TUI Edition)**.
* Update vision and workflow description: Replace linear CLI workflow with a Textual-based split-pane dashboard (Header HUD, Left Navigation Sidebar, and Split-Pane Studio workspace).
* Add `textual>=0.40.0` to Environment & Tech Stack.
* Append **Phase 5: Textual Scaffolding** and **Phase 6: Stateful Library** to the Development Roadmap:
  * **Phase 5: Textual TUI Scaffolding & Layout Architecture**
    * *Sprint 5.4: Textual TUI Scaffolding & CLI Integration* (Current)
  * **Phase 6: Stateful Library & Interactive Dashboard**
    * *Sprint 6.1: Live Widget Binding & Real-Time Profile/Draw Sync*
    * *Sprint 6.2: In-TUI Friday Draw Wizard & Treatment Previewer*

---

### Step 2: Dependency Update

#### [MODIFY] [requirements.txt](file:///home/andrew/48HFP%20App/requirements.txt)
* Add `textual>=0.40.0`.

#### [MODIFY] [pyproject.toml](file:///home/andrew/48HFP%20App/pyproject.toml)
* Add `"textual>=0.40.0"` to `project.dependencies`.

---

### Step 3 & 4: New Module Creation & TUI Application Class

#### [NEW] [studio/tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)
* Import `App`, `ComposeResult`, `Widget` from `textual.app` and `textual.widgets`.
* Define `StudioApp` inheriting from `textual.app.App`.
* Set application title, CSS styles, and compose method.

---

### Step 5 & 6: CSS Layout & Widget Stubs

#### [NEW] [studio/tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)
* Define CSS layout for a three-zone grid/dock workspace:
  * Persistent top Header HUD (`#header-hud`): Height 3 rows, centered title "🎬 48HFP-Studio v2.0", dark cyan/yellow accents.
  * Persistent left Navigation Sidebar (`#nav-sidebar`): Width 30 columns, border heavy blue/cyan, displaying status & navigation stubs.
  * Main Content Studio Workspace (`#main-workspace`): Expands to remaining space (`1fr`), displaying active workspace/panel stubs.
* Implement stub widgets:
  * `HeaderHUD(Widget)`: Renders the header banner with title and version.
  * `NavigationSidebar(Widget)`: Renders sidebar navigation and system status summary.
  * `StudioWorkspace(Widget)`: Renders main content area stub (Welcome banner, Active Constraints, Quick Actions).

---

### Step 7: CLI Integration

#### [MODIFY] [studio/cli.py](file:///home/andrew/48HFP%20App/studio/cli.py)
* Import `StudioApp` from `studio.tui`.
* Update the root `main` callback:
  * Retain `if ctx.invoked_subcommand is not None: return` bypass so headless CLI commands (`info`, `generate`, `config`, `draw`, etc.) continue working without starting the TUI.
  * When no subcommand is specified, instantiate `app_instance = StudioApp()` and call `app_instance.run()`.

#### [NEW] [tests/test_phase5_4.py](file:///home/andrew/48HFP%20App/tests/test_phase5_4.py)
* Add unit tests verifying `StudioApp` initialization, layout composition, and CLI invocation behavior.

---

## Verification Plan

### Automated Tests
1. Run `pytest` to execute all tests (including new `test_phase5_4.py` and existing test suite).
   ```bash
   pytest
   ```
2. Verify dependency installation and imports.

### Manual Verification
1. Run `python main.py` in non-interactive/headful mode to verify Textual app starts cleanly.
2. Run `python main.py info` and `python main.py --help` to confirm subcommand bypass functions as expected.
