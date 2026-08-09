"""Textual Modal Screen for the Filmmaker Personality Quiz."""

from typing import Dict, Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from studio.models.profile import TeamProfile
from studio.quiz import QUIZ_QUESTIONS, QuizEngine, QuizResult
from studio.utils.profile_store import load_profile, save_profile


class OnboardingQuizScreen(ModalScreen[Optional[str]]):
    """Interactive Modal Screen walking users through the Filmmaker Personality Quiz."""

    DEFAULT_CSS = """
    OnboardingQuizScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.75);
    }

    #quiz-dialog {
        padding: 1 2;
        width: 85%;
        max-width: 80;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $accent;
    }

    .quiz-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
        content-align: center middle;
    }

    .quiz-progress {
        color: $text-muted;
        text-style: italic;
        margin-bottom: 1;
    }

    .quiz-prompt {
        color: $text;
        text-style: bold;
        margin-bottom: 1;
    }

    .option-btn {
        width: 100%;
        margin-bottom: 1;
        text-align: left;
    }

    .quiz-nav-bar {
        margin-top: 1;
        height: 3;
        align: right middle;
    }

    .quiz-nav-bar Button {
        margin-left: 1;
    }

    .result-header {
        color: $warning;
        text-style: bold;
        margin-bottom: 1;
        content-align: center middle;
    }

    .result-director {
        color: $accent-lighten-2;
        text-style: bold;
        margin-bottom: 0;
    }

    .result-tagline {
        color: $text;
        text-style: italic;
        margin-bottom: 1;
    }

    .result-box {
        background: $panel;
        padding: 1;
        border: solid $accent;
        margin-bottom: 1;
    }

    .result-section-label {
        color: $accent-lighten-1;
        text-style: bold;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.current_q_idx: int = 0
        self.answers: Dict[int, int] = {}
        self.is_completed: bool = False
        self.quiz_result: Optional[QuizResult] = None

    def compose(self) -> ComposeResult:
        with Container(id="quiz-dialog"):
            yield Label("🔮 [bold cyan]FILMMAKER PERSONALITY QUIZ[/bold cyan]", classes="quiz-title")
            yield Vertical(id="quiz-body-container")

    def on_mount(self) -> None:
        self.render_question_view()

    def render_question_view(self) -> None:
        """Render the active quiz question prompt and option buttons."""
        body = self.query_one("#quiz-body-container", Vertical)
        body.remove_children()

        q = QUIZ_QUESTIONS[self.current_q_idx]
        total_q = len(QUIZ_QUESTIONS)

        progress_label = Label(f"Question {self.current_q_idx + 1} of {total_q} [{q.category.upper()}]", classes="quiz-progress")
        prompt_label = Label(q.prompt, classes="quiz-prompt")

        option_buttons = []
        for idx, opt in enumerate(q.options):
            btn_variant = "primary" if self.answers.get(q.id) == idx else "default"
            option_buttons.append(
                Button(
                    f"[{chr(65 + idx)}] {opt.text}",
                    variant=btn_variant,
                    id=f"opt_btn_{idx}",
                    classes="option-btn",
                )
            )
        scroll = VerticalScroll(*option_buttons)

        nav_buttons = []
        if self.current_q_idx > 0:
            nav_buttons.append(Button("← Previous", id="prev_q_btn", variant="default"))
        nav_buttons.append(Button("Cancel", id="cancel_quiz_btn", variant="error"))
        nav = Horizontal(*nav_buttons, classes="quiz-nav-bar")

        body.mount(progress_label, prompt_label, scroll, nav)

    def render_result_view(self) -> None:
        """Render the quiz completion result and activation button."""
        body = self.query_one("#quiz-body-container", Vertical)
        body.remove_children()

        if not self.quiz_result:
            return

        info = self.quiz_result.winner_info

        header_label = Label("🎬 [bold yellow]YOUR WINNING DIRECTOR ARCHETYPE[/bold yellow]", classes="result-header")
        director_label = Label(f"🏆 [bold green]{info.director_name}[/bold green]", classes="result-director")
        tagline_label = Label(f"\"{info.title}\"", classes="result-tagline")

        static_content = Static(
            f"💬 [bold white]Quote:[/bold white]\n[italic]\"{info.quote}\"[/italic]\n\n"
            f"🎨 [bold white]Visual Economy & Camera Style:[/bold white]\n{info.visual_style}\n\n"
            f"🧠 [bold white]Thematic Core & Philosophy:[/bold white]\n{info.thematic_core}"
        )
        result_box = Container(static_content, classes="result-box")
        scroll = VerticalScroll(result_box)

        nav_buttons = [
            Button(
                f"Activate {info.director_name} Constraints",
                id="activate_quiz_btn",
                variant="primary",
            ),
            Button("Close / Skip", id="close_quiz_btn", variant="default"),
        ]
        nav = Horizontal(*nav_buttons, classes="quiz-nav-bar")

        body.mount(header_label, director_label, tagline_label, scroll, nav)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""

        if btn_id.startswith("opt_btn_"):
            selected_idx = int(btn_id.replace("opt_btn_", ""))
            q = QUIZ_QUESTIONS[self.current_q_idx]
            self.answers[q.id] = selected_idx

            if self.current_q_idx < len(QUIZ_QUESTIONS) - 1:
                self.current_q_idx += 1
                self.render_question_view()
            else:
                self.is_completed = True
                self.quiz_result = QuizEngine.calculate_result(self.answers)
                self.render_result_view()

        elif btn_id == "prev_q_btn":
            if self.current_q_idx > 0:
                self.current_q_idx -= 1
                self.render_question_view()

        elif btn_id == "cancel_quiz_btn" or btn_id == "close_quiz_btn":
            self.action_cancel()

        elif btn_id == "activate_quiz_btn":
            self.action_activate_constraints()

    def action_activate_constraints(self) -> None:
        """Save winning director constraints into active TeamProfile."""
        if not self.quiz_result:
            self.dismiss(None)
            return

        winner_slug = self.quiz_result.winner_slug
        winner_info = self.quiz_result.winner_info

        profile = load_profile() or TeamProfile(
            team_name="Indie Crew",
            admin_username="director",
            location="Unknown",
        )

        profile.active_directorial_vision = winner_slug
        profile.active_thematic_framework = winner_slug
        save_profile(profile)

        self.notify(
            f"Activated '{winner_info.director_name}' constraints!",
            title="Constraints Activated",
            severity="information",
        )
        self.dismiss(winner_slug)
