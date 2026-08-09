"""Automated unit tests for Phase 8, Sprint 8.2: The Filmmaker Personality Quiz."""

from pathlib import Path
from typer.testing import CliRunner

from studio.cli_workspace import workspace_app
from studio.models.profile import TeamProfile
from studio.quiz import ARCHETYPE_LIBRARY, QUIZ_QUESTIONS, QuizEngine
from studio.screens_quiz import OnboardingQuizScreen
from studio.utils.constraint_store import (
    load_directorial_vision,
    load_thematic_framework,
    seed_default_constraints,
)
from studio.utils.global_state import set_active_workspace
from studio.utils.profile_store import load_profile

runner = CliRunner()


def test_seed_all_12_director_archetypes(tmp_path: Path) -> None:
    """Test that seed_default_constraints generates all 12 director archetype constraint sets."""
    set_active_workspace(tmp_path)
    seed_default_constraints()

    expected_slugs = [
        "wes_anderson",
        "wong_kar_wai",
        "david_lynch",
        "bong_joon_ho",
        "denis_villeneuve",
        "nicolas_winding_refn",
        "celine_sciamma",
        "jordan_peele",
        "alfonso_cuaron",
        "lars_von_trier",
        "paul_thomas_anderson",
        "greta_gerwig",
    ]

    for slug in expected_slugs:
        dir_v = load_directorial_vision(slug)
        them_f = load_thematic_framework(slug)

        assert dir_v is not None, f"DirectorialVision missing for slug {slug}"
        assert dir_v.name == slug
        assert len(dir_v.visual_economy) > 0

        assert them_f is not None, f"ThematicFramework missing for slug {slug}"
        assert them_f.name == slug
        assert len(them_f.core_philosophy) > 0


def test_quiz_engine_reachability_all_12_directors() -> None:
    """Test that every single one of the 12 director archetypes can win with a targeted answer vector."""
    for target_slug in ARCHETYPE_LIBRARY.keys():
        answers = {}
        for q in QUIZ_QUESTIONS:
            # Find the option with highest weight for target_slug
            best_opt_idx = 0
            best_weight = -1
            for opt_idx, opt in enumerate(q.options):
                w = opt.weights.get(target_slug, 0)
                if w > best_weight:
                    best_weight = w
                    best_opt_idx = opt_idx
            answers[q.id] = best_opt_idx

        result = QuizEngine.calculate_result(answers)
        assert (
            result.winner_slug == target_slug
        ), f"Target director '{target_slug}' was not reached (got '{result.winner_slug}')"


def test_cli_workspace_quiz_command(tmp_path: Path, monkeypatch) -> None:
    """Test CLI '48hfp workspace quiz' command execution and profile activation."""
    set_active_workspace(tmp_path)
    seed_default_constraints()

    # Mock Prompt.ask to select option 1 for all questions, Confirm.ask to return True
    monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *args, **kwargs: "1")
    monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *args, **kwargs: True)

    cli_result = runner.invoke(workspace_app, ["quiz"])
    assert cli_result.exit_code == 0, f"CLI quiz command failed: {cli_result.output}"
    assert "WINNING ARCHETYPE" in cli_result.output

    # Verify profile constraints activated
    profile = load_profile()
    assert profile is not None
    assert profile.active_directorial_vision is not None
    assert profile.active_thematic_framework is not None
    assert profile.active_directorial_vision == profile.active_thematic_framework


def test_tui_quiz_modal_instantiation() -> None:
    """Test OnboardingQuizScreen instantiation and answer tracking."""
    modal = OnboardingQuizScreen()
    assert modal.current_q_idx == 0
    assert not modal.is_completed

    # Simulate answering all questions with option 0
    for q in QUIZ_QUESTIONS:
        modal.answers[q.id] = 0

    res = QuizEngine.calculate_result(modal.answers)
    assert res.winner_slug in ARCHETYPE_LIBRARY


import pytest
from studio.tui import StudioApp


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_tui_quiz_modal_async_rendering(tmp_path: Path) -> None:
    """Test OnboardingQuizScreen mounting, question rendering, option selection, and result rendering in Textual."""
    set_active_workspace(tmp_path)
    seed_default_constraints()

    app = StudioApp()
    async with app.run_test() as pilot:
        quiz_screen = OnboardingQuizScreen()
        app.push_screen(quiz_screen)
        await pilot.pause()

        # Verify initial question view rendered
        assert quiz_screen.current_q_idx == 0
        assert not quiz_screen.is_completed

        # Click through options for all 10 questions
        for q_num in range(10):
            await pilot.click("#opt_btn_0")
            await pilot.pause()

        # Verify quiz completed and result view rendered without compose stack errors
        assert quiz_screen.is_completed
        assert quiz_screen.quiz_result is not None
        assert quiz_screen.query_one("#activate_quiz_btn") is not None

        # Click activate
        await pilot.click("#activate_quiz_btn")
        await pilot.pause()

        # Verify profile updated
        profile = load_profile()
        assert profile is not None
        assert profile.active_directorial_vision == quiz_screen.quiz_result.winner_slug

