# Implementation Plan - Sprint 6.1: Live Widget Binding & Real-Time Profile/Draw Sync

**Sprint Goal:** Upgrade the Textual TUI (`studio/tui.py`) from static scaffolding to reactive, live-bound data widgets displaying real-time `TeamProfile` and `FridayDraw` states.

---

## Required Changes

### 1. Reactive State in `StudioApp` (`studio/tui.py`)
- Import `reactive` from `textual.reactive`.
- Import `TeamProfile` from `studio.models.profile` and `FridayDraw` from `studio.models.draw`.
- Import `load_profile` from `studio.utils.profile_store` and `load_draw` from `studio.utils.draw_store`.
- Add reactive properties to `StudioApp`:
  - `app_profile: reactive[TeamProfile | None] = reactive(None)`
  - `app_draw: reactive[FridayDraw | None] = reactive(None)`

### 2. State Initialization (`StudioApp.on_mount`)
- Add an `on_mount()` method to `StudioApp`:
  ```python
  def on_mount(self) -> None:
      """Initialize reactive application state from persistent stores on mount."""
      self.app_profile = load_profile()
      self.app_draw = load_draw()
  ```

### 3. Widget Property Binding & Watchers
- Add reactive properties to child widgets:
  - `HeaderHUD`: `profile: reactive[TeamProfile | None] = reactive(None)`
  - `NavigationSidebar`: `profile: reactive[TeamProfile | None] = reactive(None)`
  - `StudioWorkspace`: `draw: reactive[FridayDraw | None] = reactive(None)`, `profile: reactive[TeamProfile | None] = reactive(None)`
- Add watch handlers to `StudioApp` to push reactive state down to child widgets:
  ```python
  def watch_app_profile(self, profile: TeamProfile | None) -> None:
      """Push app_profile changes down to child widgets."""
      try:
          self.query_one(NavigationSidebar).profile = profile
          self.query_one(HeaderHUD).profile = profile
          self.query_one(StudioWorkspace).profile = profile
      except Exception:
          pass

  def watch_app_draw(self, draw: FridayDraw | None) -> None:
      """Push app_draw changes down to child widgets."""
      try:
          self.query_one(StudioWorkspace).draw = draw
      except Exception:
          pass
  ```

### 4. Dynamic Sidebar Rendering (`NavigationSidebar`)
- Update `NavigationSidebar` to dynamically update its display based on `self.profile`.
- Define a `watch_profile` method or update helper to render:
  - **Team Name**: `profile.team_name` (or `"Unconfigured"` if `None`)
  - **Admin**: `profile.admin_username` (or `"N/A"` if `None`)
  - **Logistical Constraints**: `profile.active_logistical_constraint or "None"`
  - **Creative Constraints**: `profile.active_creative_constraint or "None"`
  - Active navigation options.

### 5. Dynamic Workspace Rendering (`StudioWorkspace`)
- Update `StudioWorkspace` to dynamically update its display based on `self.draw`.
- Define a `watch_draw` method or update helper to render:
  - If `draw` is present: Formatted summary of `FridayDraw` parameters:
    - Primary Genre (`genre_1`)
    - Secondary Genre (`genre_2`)
    - Character (`character_name` - `character_trait` [{`character_gender`}])
    - Required Prop (`required_prop`)
    - Required Line (`required_line`)
  - If `draw` is `None`: Clear "No Draw Recorded" notice with CLI guidance.

---

## User Review Required

> [!IMPORTANT]
> - **Top-Down Reactive Cascade:** State changes flow top-down (`StudioApp` reactive properties -> child widget reactive properties -> watch methods / UI redraws).
> - **Graceful Null Fallbacks:** All widgets handle `None` values gracefully without crashes or missing field errors.

---

## Proposed Changes

### Component 1: TUI Module

#### [MODIFY] [tui.py](file:///home/andrew/48HFP%20App/studio/tui.py)
- Implement `reactive` attributes on `StudioApp`, `HeaderHUD`, `NavigationSidebar`, and `StudioWorkspace`.
- Implement `on_mount()`, `watch_app_profile()`, `watch_app_draw()`.
- Add dynamic rendering logic to `NavigationSidebar` and `StudioWorkspace`.

### Component 2: Test Suite

#### [NEW] [test_phase6_1.py](file:///home/andrew/48HFP%20App/tests/test_phase6_1.py)
- Add unit tests for `StudioApp` initialization, `on_mount` state loading, watcher property propagation, and dynamic rendering for both populated and `None` states.

---

## Verification Plan

### Automated Tests
- Execute `pytest tests/test_phase6_1.py` using Textual's `run_test()` pilot driver.
- Execute full test suite `pytest` across all modules.

### Manual Verification
- Test TUI mounting via CLI with and without existing `~/.48hfp_profile.yaml` / `~/.48hfp_draw.yaml`.
