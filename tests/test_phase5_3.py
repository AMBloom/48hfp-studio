"""Unit tests for Sprint 5.3 (UX Refinements, Quote Fixes, Appendix & v0.1.1)."""

from pathlib import Path
from typer.testing import CliRunner

from studio import __version__
from studio.cli import app
from studio.models.draw import FridayDraw, create_default_draw
from studio.utils.prompt_builder import PromptBuilder
from studio.utils.treatment_store import convert_treatment_to_markdown, save_treatment_output
from tests.test_phase4 import create_sample_treatment

runner = CliRunner()


def test_version_bump():
    """Verify application version is updated to 3.0.0."""
    assert __version__ == "3.0.0"

    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "3.0.0" in result.output


def test_required_line_quote_stripping():
    """Verify single and double quotes are automatically stripped from required_line."""
    # 1. Double quotes
    draw_double = FridayDraw(
        genre_1="Comedy",
        genre_2="Heist",
        character_name="Sam",
        character_trait="Driver",
        required_prop="Key",
        required_line='"Wait for my signal!"',
    )
    assert draw_double.required_line == "Wait for my signal!"

    # 2. Single quotes
    draw_single = FridayDraw(
        genre_1="Comedy",
        genre_2="Heist",
        character_name="Sam",
        character_trait="Driver",
        required_prop="Key",
        required_line="'Don't look back.'",
    )
    assert draw_single.required_line == "Don't look back."

    # 3. create_default_draw helper
    draw_default = create_default_draw(required_line='  "Look what I did."  ')
    assert draw_default.required_line == "Look what I did."


def test_treatment_markdown_prompt_appendix(tmp_path: Path):
    """Verify system prompt appendix section 7 is correctly generated."""
    treatment = create_sample_treatment()
    raw_prompt = "SYSTEM PROMPT DIRECTIVE: DO NOT FAIL"

    # convert_treatment_to_markdown
    md = convert_treatment_to_markdown(treatment, prompt_text=raw_prompt)
    assert "## 7. APPENDIX: SYSTEM PROMPT" in md
    assert "SYSTEM PROMPT DIRECTIVE: DO NOT FAIL" in md

    # save_treatment_output
    file_path = save_treatment_output(treatment, outputs_dir=tmp_path, prompt_text=raw_prompt)
    content = file_path.read_text(encoding="utf-8")
    assert "## 7. APPENDIX: SYSTEM PROMPT" in content
    assert "SYSTEM PROMPT DIRECTIVE: DO NOT FAIL" in content


def test_prompt_builder_location_bias_directive():
    """Verify global state section includes the explicit location bias directive."""
    prompt = PromptBuilder.compile_system_prompt()
    assert (
        "NOTE: The Production Location dictates physical filming boundaries and logistics. "
        "It DOES NOT dictate the fictional setting of the story unless explicitly required by the Creative Constraints."
    ) in prompt
