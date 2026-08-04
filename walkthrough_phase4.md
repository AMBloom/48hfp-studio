# Phase 4 Walkthrough: Inference Engine & Output Versioning

Phase 4 concludes the development of **48HFP-Studio**, connecting the hierarchical prompt compiler from Phase 3 to Google's Gemini LLM backend via the `google-genai` SDK, enforcing structured JSON outputs through Pydantic schemas, and safe-writing versioned Markdown film treatments to local disk storage.

---

## 🚀 Key Features Implemented

### 1. AI Provider Integration (`studio/inference.py`)
- **Primary API Adapter**: Built using the official `google-genai` SDK (`from google import genai`).
- **Structured Output Enforcement**: Passes the `TreatmentOutput` Pydantic model directly into `config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=TreatmentOutput)`.
- **API Key & Error Handling**:
  - Checks for `GEMINI_API_KEY` in environment variables. Raises clean `InferenceError` with onboarding instructions if missing.
  - Defaults model to `gemini-2.5-flash` with support for `GEMINI_MODEL` env var or CLI `--model` overrides.
  - Wraps network timeouts, API failures, and payload validation errors gracefully.

### 2. Treatment Output Schema (`studio/models/treatment.py`)
Enforces the mandatory 6-section 48HFP script layout:
1. `TitleAndLogline`: Working title, genre blend, and 1-2 sentence dramatic logline.
2. `CharacterRosterItem`: Detailed character roster with 48HFP required character flag.
3. `NarrativeSynopsis`: Act I Setup, Act II Escalation, Act III Climax/Resolution, and Thematic Arc.
4. `SceneBreakdownItem`: Scene number, heading, location, time of day, characters present, visual action, and props used.
5. `DialogueSnippetItem`: Character dialogue beats with verbatim required line tracking.
6. `FestivalComplianceChecklist`: Explicit verification flags for verbatim line, prop usage, character linkage, and 4-7 minute runtime pacing.

### 3. Output Versioning & Safe-Write System (`studio/utils/treatment_store.py`)
- **Cross-Platform Pathing**: Uses `pathlib.Path.cwd() / "outputs"` for bulletproof path resolution across Windows, macOS, and Linux.
- **Version Zero-Padding**: Formats versions as 2-digit zero-padded integers (`v01`, `v02`, `v10`).
- **Empty Directory Fallback**: Scans `./outputs` for existing `treatment_v*.md` files and safely defaults to `1` (`v01`) if empty or uninitialized.
- **Strict Safe-Write**: Constructs filenames using `treatment_v[XX]_[Logistical]_[Creative]_[YYYYMMDD_HHMMSS].md` and guarantees existing treatments are **never overwritten**.
- **Markdown Export**: Converts Pydantic objects into formatted Markdown documents with headers and tables.

### 4. CLI Command (`48hfp generate`)
Added `48hfp generate` command in `studio/cli.py`:
- `48hfp generate`: Compiles prompt, displays a `rich` loading spinner, invokes Gemini, safe-writes treatment, and prints a summary panel with compliance status.
- `48hfp generate --dry-run`: Previews the compiled prompt without making API calls.
- `48hfp generate --model <name>`: Overrides model used for generation.
- `48hfp generate --output-dir <path>`: Saves treatment to a custom output directory.

---

## 🧪 Automated Verification Results

Ran `pytest -v` across Phase 3 and Phase 4 test suites:

```bash
tests/test_phase3.py::test_genre_group_constants PASSED
tests/test_phase3.py::test_friday_draw_fallback_generator PASSED
tests/test_phase3.py::test_draw_store_lifecycle PASSED
tests/test_phase3.py::test_prompt_builder_hierarchy_and_recency_effect PASSED
tests/test_phase4.py::test_sanitize_filename_part PASSED
tests/test_phase4.py::test_empty_directory_fallback_and_version_increment PASSED
tests/test_phase4.py::test_save_treatment_output_zero_padding_and_safe_write PASSED
tests/test_phase4.py::test_convert_treatment_to_markdown PASSED
tests/test_phase4.py::test_inference_engine_missing_api_key PASSED
tests/test_phase4.py::test_inference_engine_successful_generation PASSED
tests/test_phase4.py::test_cli_generate_dry_run PASSED
tests/test_phase4.py::test_cli_generate_missing_api_key PASSED

============================== 12 passed in 0.87s ==============================
```

---

## 📖 How to Run Phase 4

### 1. Preview Prompt (Dry Run)
```bash
48hfp generate --dry-run
```

### 2. Set API Key and Generate Treatment
```bash
export GEMINI_API_KEY="your-gemini-api-key"
48hfp generate
```

### 3. Check Generated Treatment Output
Check `./outputs/`:
```bash
ls -la outputs/
cat outputs/treatment_v01_*.md
```
