# Walkthrough: Phase 5 - Expanded Fungible Fallbacks (Sprint 5.0)

## Overview
In Sprint 5.0 of **48HFP-Studio**, we refactored the Friday Night Draw fallback logic to eliminate AI genre bias by replacing hardcoded static placeholders with expansive, randomized pools of highly fungible, generic constraints.

---

## What Was Built

### 1. Expanded Fungible Fallback Pools ([studio/models/draw.py](file:///home/andrew/48HFP%20App/studio/models/draw.py))

Defined four top-level constant lists near `GENRES_GROUP_1` and `GENRES_GROUP_2`:
- `FALLBACK_NAMES` (25 gender-paired names):
  *Examples*: `"Michael / Michelle"`, `"Colin / Coleen"`, `"Sam / Samantha"`, `"Julian / Julianne"`, `"Andrew / Andrea"`.
- `FALLBACK_TRAITS` (39 versatile professions/traits):
  *Examples*: `"Commuter"`, `"Office worker"`, `"Doctor"`, `"Driver"`, `"Startup Founder"`, `"Data Analyst"`, `"Librarian"`.
- `FALLBACK_PROPS` (30 everyday physical objects):
  *Examples*: `"Mirror"`, `"Tape"`, `"Banana"`, `"Coffee mug"`, `"Flashlight"`, `"Deck of cards"`, `"Headphones"`.
- `FALLBACK_LINES` (27 generic dialogue lines):
  *Examples*: `"Look what I did."`, `"Don't tell anyone."`, `"There's no 'I' in 'Team'."`, `"I've got a bad feeling about this."`, `"It insists upon itself."`.

### 2. Smart Default Draw Generator Refactoring ([studio/models/draw.py](file:///home/andrew/48HFP%20App/studio/models/draw.py))

Refactored `create_default_draw()` to automatically pick a random choice from the newly defined fallback pools whenever `character_name`, `character_trait`, `required_prop`, or `required_line` evaluate as empty or whitespace-only:
```python
c_name = character_name.strip() if character_name and character_name.strip() else random.choice(FALLBACK_NAMES)
c_trait = character_trait.strip() if character_trait and character_trait.strip() else random.choice(FALLBACK_TRAITS)
prop = required_prop.strip() if required_prop and required_prop.strip() else random.choice(FALLBACK_PROPS)
line = required_line.strip() if required_line and required_line.strip() else random.choice(FALLBACK_LINES)
```

---

## Verification & Testing Highlights

### Automated Unit Test Suite (`tests/test_phase3.py`)

Updated `test_friday_draw_fallback_generator()` in `tests/test_phase3.py` to assert that fallback values generated for blank inputs belong to their respective constant fallback lists (`FALLBACK_NAMES`, `FALLBACK_TRAITS`, `FALLBACK_PROPS`, `FALLBACK_LINES`).

Executed test suite:
```bash
PYTHONPATH=. pytest -v
```

Output:
```
============================= test session starts ==============================
platform linux -- Python 3.12.2, pytest-8.3.3, pluggy-1.5.0
collected 13 items

tests/test_phase3.py::test_genre_group_constants PASSED                  [  7%]
tests/test_phase3.py::test_friday_draw_fallback_generator PASSED         [ 15%]
tests/test_phase3.py::test_draw_store_lifecycle PASSED                   [ 23%]
tests/test_phase3.py::test_prompt_builder_hierarchy_and_recency_effect PASSED [ 30%]
tests/test_phase4.py::test_sanitize_filename_part PASSED                 [ 38%]
tests/test_phase4.py::test_empty_directory_fallback_and_version_increment PASSED [ 46%]
tests/test_phase4.py::test_save_treatment_output_zero_padding_and_safe_write PASSED [ 53%]
tests/test_phase4.py::test_convert_treatment_to_markdown PASSED          [ 61%]
tests/test_phase4.py::test_inference_engine_missing_api_key PASSED       [ 69%]
tests/test_phase4.py::test_inference_engine_successful_generation PASSED [ 76%]
tests/test_phase4.py::test_inference_engine_model_resolution PASSED      [ 84%]
tests/test_phase4.py::test_cli_generate_dry_run PASSED                   [ 92%]
tests/test_phase4.py::test_cli_generate_missing_api_key PASSED           [100%]

============================== 13 passed in 0.98s ==============================
```
