"""Unit tests for Sprint 7.1 (UI Stabilization & Filename Upgrades)."""

from pathlib import Path
from studio.models.treatment import TitleAndLogline
from studio.screens_library import ConstraintLibraryScreen
from studio.utils.treatment_store import get_next_version_number, save_treatment_output
from studio.workspace import RecipePane
from tests.test_phase4 import create_sample_treatment


def test_constraint_library_screen_css():
    """Verify DEFAULT_CSS for ConstraintLibraryScreen has height 90vh, vertical layout, docked action bar, and TabbedContent margin clearance."""
    css = ConstraintLibraryScreen.DEFAULT_CSS
    assert "height: 90vh;" in css
    assert "layout: vertical;" in css
    assert "dock: bottom;" in css
    assert "margin-bottom: 1;" in css
    assert "margin-bottom: 3;" in css


def test_recipe_pane_css():
    """Verify RecipePane DEFAULT_CSS includes padding-right: 2 for right-border clearance."""
    css = RecipePane.DEFAULT_CSS
    assert "padding-right: 2;" in css


def test_treatment_filename_title_injection(tmp_path: Path):
    """Verify film title is injected immediately after version string and version increment regex works."""
    treatment = create_sample_treatment()
    treatment.title_and_logline = TitleAndLogline(
        title="Staycation Souffle",
        genre_blend="Comedy / Cooking",
        logline="A novice chef attempts a complex soufflé during a sudden lockdown.",
    )

    # 1. First save -> v01 with title injected
    file_path_1 = save_treatment_output(treatment, outputs_dir=tmp_path)
    assert file_path_1.exists()
    assert file_path_1.name.startswith("treatment_v01_Staycation_Souffle_")

    # 2. Version increment check with title-injected schema
    next_v = get_next_version_number(tmp_path)
    assert next_v == 2

    # 3. Second save -> v02 with title injected
    file_path_2 = save_treatment_output(treatment, outputs_dir=tmp_path)
    assert file_path_2.exists()
    assert file_path_2.name.startswith("treatment_v02_Staycation_Souffle_")
