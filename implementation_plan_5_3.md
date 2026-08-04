# Sprint 5.3 Implementation Plan (Tech Debt, UX Refinements & v0.1.1)

Sprint 5.3 addresses accumulated technical debt, refines prompt injection logic (location bias, system prompt appendix), strips unwanted quotes from user inputs, cleans up UI titles, and bumps the application version to `v0.1.1`.

## User Review Required

> [!IMPORTANT]
> **Key Behavioral Changes in v0.1.1:**
> - `save_treatment_output()` and `convert_treatment_to_markdown()` now accept an optional `prompt_text` parameter. When provided, the raw compiled prompt is saved as section `## 7. APPENDIX: SYSTEM PROMPT` inside generated treatment Markdown files.
> - User input for `required_line` in `FridayDraw` automatically strips leading/trailing single and double quotes (`"` and `'`).
> - The prompt builder global state section adds an explicit directive preventing Gemini from confusing the production filming location with the story's fictional setting.

## Open Questions

No open questions at this time. All requirements for Sprint 5.3 are well-defined.

## Proposed Changes

---

### Core Package Versioning

#### [MODIFY] [pyproject.toml](file:///home/andrew/48HFP%20App/pyproject.toml)
- Bump version from `0.1.0` to `0.1.1`.

#### [MODIFY] [__init__.py](file:///home/andrew/48HFP%20App/studio/__init__.py)
- Bump `__version__` from `"0.1.0"` to `"0.1.1"`.

---

### Models & Validation

#### [MODIFY] [draw.py](file:///home/andrew/48HFP%20App/studio/models/draw.py)
- Add `@field_validator("required_line")` to `FridayDraw` class (and update `create_default_draw()`) to strip leading/trailing whitespace and quotes (`.strip().strip('"\'').strip()`).

---

### UI & Terminal Formatting

#### [MODIFY] [ui.py](file:///home/andrew/48HFP%20App/studio/utils/ui.py)
- Update `display_prompt_panel()` title from `[bold gold1]⚡ Compiled System Prompt (Recency Effect Enforced)[/bold gold1]` to `[bold gold1]⚡ Compiled System Prompt[/bold gold1]`.
- Update `print_banner()` version string to `v0.1.1`.

---

### Treatment Storage & Prompt Appendix

#### [MODIFY] [treatment_store.py](file:///home/andrew/48HFP%20App/studio/utils/treatment_store.py)
- Update `convert_treatment_to_markdown(treatment: TreatmentOutput, prompt_text: Optional[str] = None)` to append `## 7. APPENDIX: SYSTEM PROMPT` in a code block if `prompt_text` is provided.
- Update `save_treatment_output(treatment: TreatmentOutput, outputs_dir: Optional[Path] = None, prompt_text: Optional[str] = None)` to forward `prompt_text` to `convert_treatment_to_markdown()`.

#### [MODIFY] [cli.py](file:///home/andrew/48HFP%20App/studio/cli.py)
- Update `generate_command` to pass `prompt_text` into `save_treatment_output(treatment, outputs_dir=output_dir, prompt_text=prompt_text)`.

---

### System Prompt Builder

#### [MODIFY] [prompt_builder.py](file:///home/andrew/48HFP%20App/studio/utils/prompt_builder.py)
- Update `_build_global_state_section()` to append:
  `NOTE: The Production Location dictates physical filming boundaries and logistics. It DOES NOT dictate the fictional setting of the story unless explicitly required by the Creative Constraints.`

---

## Verification Plan

### Automated Tests
- Run `PYTHONPATH=. pytest -v` to ensure all existing tests pass and no test signatures broken.
- Add unit tests in `tests/test_phase4.py` (or new test function) verifying:
  1. `FridayDraw` quote-stripping validator.
  2. `convert_treatment_to_markdown` and `save_treatment_output` with `prompt_text` appendix section 7.
  3. Location bias directive presence in `PromptBuilder.compile_system_prompt()`.

### Manual Verification
- Test `48hfp --version` to confirm `0.1.1`.
- Test `48hfp prompt` to verify UI panel title is `⚡ Compiled System Prompt`.
