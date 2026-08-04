# Phase 4 Implementation Plan: Inference Engine & Output Versioning

Phase 4 completes the **48HFP-Studio** MVP by connecting the hierarchical prompt compiler (Phase 3) to the Google Gemini backend via the `google-genai` SDK, enforcing structured JSON output through a comprehensive Pydantic `TreatmentOutput` schema, converting the response into a readable Markdown document, and safe-writing versioned files to local storage.

## User Review Required

> [!IMPORTANT]
> **API Key & Default Model**:
> The inference engine relies on the `GEMINI_API_KEY` environment variable. The default model is set to `gemini-2.5-flash` (or `gemini-2.0-flash` / `gemini-1.5-flash`), with CLI override support (`48hfp generate --model <name>`).
>
> **Output Versioning Naming Convention**:
> Outputs will be saved in `./outputs/` with the exact pattern:
> `treatment_v[XX]_[Logistical_Name]_[Creative_Name]_[YYYYMMDD_HHMMSS].md`
> Files will **never** overwrite existing treatments; version numbers will automatically increment based on existing files in `./outputs/`.

## Open Questions

> [!NOTE]
> None at this time. All requirements match the project specifications and build seamlessly on Phase 1, Phase 2, and Phase 3 implementations.

---

## Proposed Changes

### 1. Data Models (`studio/models/treatment.py`)

#### [NEW] [treatment.py](file:///home/andrew/48HFP%20App/studio/models/treatment.py)
Define the complete Pydantic schema for structured treatment generation:
- `TitleAndLogline`: `title`, `genre_blend`, `logline`
- `CharacterRosterItem`: `name`, `actor_or_traits`, `role`, `is_required_character`
- `NarrativeSynopsis`: `act_1_setup`, `act_2_escalation`, `act_3_climax_resolution`, `thematic_arc`
- `SceneBreakdownItem`: `scene_number`, `heading`, `location`, `time_of_day`, `characters_present`, `action_summary`, `props_used`
- `DialogueSnippetItem`: `character`, `line`, `is_required_line`, `context_notes`
- `FestivalComplianceChecklist`: `verbatim_line_verified`, `prop_usage_verified`, `character_linkage_verified`, `pacing_runtime_verified`, `compliance_notes`
- `TreatmentOutput`: Top-level model containing all above sections.

---

### 2. Inference Engine (`studio/inference.py`)

#### [NEW] [inference.py](file:///home/andrew/48HFP%20App/studio/inference.py)
Implement `InferenceEngine` using `google-genai` SDK:
- Check for `GEMINI_API_KEY` in environment. Raise user-friendly `InferenceError` if missing.
- Instantiate `genai.Client` and invoke `client.models.generate_content`.
- Configure `response_mime_type="application/json"` and `response_schema=TreatmentOutput`.
- Robust error handling for network timeouts, API rate limits, and invalid schema responses.

---

### 3. Output Storage & Markdown Export (`studio/utils/treatment_store.py`)

#### [NEW] [treatment_store.py](file:///home/andrew/48HFP%20App/studio/utils/treatment_store.py)
Implement output versioning and Markdown export:
- `convert_treatment_to_markdown(treatment: TreatmentOutput) -> str`: Converts Pydantic object into a beautifully formatted 6-section Markdown document.
- `get_next_version_number(outputs_dir: Path) -> int`: Scans `./outputs` for existing `treatment_v*.md` files and computes `max(versions) + 1`.
- `save_treatment_output(treatment: TreatmentOutput, outputs_dir: Optional[Path] = None) -> Path`:
  - Resolves active logistical and creative constraint set names.
  - Sanitizes set names for safe filesystem use.
  - Formats timestamp `YYYYMMDD_HHMMSS`.
  - Constructs filename: `treatment_v[XX]_[Logistical]_[Creative]_[Timestamp].md`.
  - Performs safe-write check (ensures file doesn't already exist).
  - Writes Markdown content and returns saved file `Path`.

---

### 4. CLI Integration (`studio/cli.py`)

#### [MODIFY] [cli.py](file:///home/andrew/48HFP%20App/studio/cli.py)
Add `48hfp generate` command:
- Accepts optional `--model` and `--output-dir` arguments.
- Compiles system prompt using `PromptBuilder.compile_system_prompt()`.
- Renders `rich` loading spinner during generation.
- Calls `InferenceEngine` and `save_treatment_output`.
- Prints `rich` summary panel with saved file path, version number, title/logline, and festival compliance status.

---

### 5. Automated Tests (`tests/test_phase4.py`)

#### [NEW] [test_phase4.py](file:///home/andrew/48HFP%20App/tests/test_phase4.py)
Implement comprehensive unit tests:
- `test_treatment_output_schema_validation`: Test schema validation and JSON parsing.
- `test_convert_treatment_to_markdown`: Verify Markdown output structure.
- `test_get_next_version_number_and_safe_write`: Verify auto-incrementing version numbers and safe-write prevention of overwrites.
- `test_inference_engine_missing_api_key`: Verify error handling when `GEMINI_API_KEY` is not present.
- `test_cli_generate_help`: Test CLI command registration and options.

---

## Verification Plan

### Automated Tests
- Run `pytest tests/test_phase4.py` to verify unit test suite.
- Run `pytest` to ensure all existing tests (Phase 1, Phase 2, Phase 3) continue to pass.

### Manual Verification
- Test `48hfp generate --help` to confirm CLI command integration.
- Test `GEMINI_API_KEY` validation message when API key is unconfigured.
- Test mock/live treatment generation and inspect generated `./outputs/treatment_v01_*.md` file formatting.
- Verify safe-write behavior by running generation multiple times and checking that version numbers increment (`v01`, `v02`, etc.) without overwriting existing files.
