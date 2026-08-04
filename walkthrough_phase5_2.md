# Walkthrough - Sprint 5.2: State-Aware Root Helper

Sprint 5.2 implements a state-aware root helper that intercepts root CLI execution (`python main.py` with no arguments), inspects the local team configuration and kickoff draw state, and dynamically guides the user on what action to take next.

## Summary of Changes

### Core CLI Application (`studio/cli.py`)

1. **Typer App Configuration**:
   - Modified `no_args_is_help` from `True` to `False` on the main `typer.Typer` app instantiation.

2. **Root Callback Logic (`main`)**:
   - Updated the callback decorator to `@app.callback(invoke_without_command=True)`.
   - Added `ctx: typer.Context` parameter to check `ctx.invoked_subcommand`. If a subcommand is called, `main()` returns early and allows Typer to execute the subcommand normally.
   - When no subcommand is invoked (`ctx.invoked_subcommand is None`), evaluated local state (`profile_exists()`, `draw_exists()`) and rendered the appropriate guidance panel using `print_panel(...)`.

3. **State Guidance Panels**:
   - **Stage 1 (No Profile)**:
     - **Title**: `🧭 What's Next? (Stage 1: Setup)`
     - **Color**: `yellow`
     - **Copy**:
       > You haven't configured your team yet.
       > 👉 Proceed: Run `python main.py config setup` to onboard your team.
   - **Stage 2 (Profile exists, No Draw)**:
     - **Title**: `🧭 What's Next? (Stage 2: Kickoff Draw)`
     - **Color**: `yellow`
     - **Copy**:
       > Your team is configured, but you haven't recorded your Friday Draw parameters.
       > 👉 Proceed: Run `python main.py draw wizard` to record your constraints.
       > 👉 Go Back: Run `python main.py config setup` to edit your team profile.
   - **Stage 3 (Profile and Draw exist)**:
     - **Title**: `🧭 What's Next? (Stage 3: Ready for Generation)`
     - **Color**: `green`
     - **Copy**:
       > All systems go. Your team profile and kickoff draw are locked in.
       > 👉 Proceed: Run `python main.py generate` to draft your film treatment.
       > 👉 Go Back: Run `python main.py constraints` to manage active sets.
       > 👉 Start Over: Run `python main.py draw reset` to wipe your draw and start fresh.

---

## Verification Results

### Terminal Output Verification (`python main.py`)

Running `python main.py` in the workspace terminal successfully renders the header banner followed by the state-aware Stage 3 guidance panel:

```text
╭───────────────────────────────────────────────────────╮
│  🎬 48HFP-Studio  v0.1.0                              │
│  Terminal-Native AI Co-Pilot for Short Film Festivals │
╰───────────────────────────────────────────────────────╯
╭────────────── 🧭 What's Next? (Stage 3: Ready for Generation) ───────────────╮
│ All systems go. Your team profile and kickoff draw are locked in.            │
│ 👉 Proceed: Run python main.py generate to draft your film treatment.        │
│ 👉 Go Back: Run python main.py constraints to manage active sets.            │
│ 👉 Start Over: Run python main.py draw reset to wipe your draw and start     │
│ fresh.                                                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Automated Unit Testing

Added unit tests in `tests/test_phase5_2.py` covering:
- Stage 1 rendering (`test_root_helper_stage_1_no_profile`)
- Stage 2 rendering (`test_root_helper_stage_2_profile_no_draw`)
- Stage 3 rendering (`test_root_helper_stage_3_profile_and_draw`)
- Subcommand pass-through (`test_subcommand_bypasses_root_helper`)

**Test Execution Output**:
```text
collected 17 items

tests/test_phase3.py ....                                                [ 23%]
tests/test_phase4.py .........                                           [ 76%]
tests/test_phase5_2.py ....                                              [100%]

============================== 17 passed in 1.03s ==============================
```
