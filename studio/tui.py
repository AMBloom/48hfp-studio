"""Stateful Terminal User Interface (TUI) for 48HFP-Studio using Textual."""

from typing import Optional
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Label, Static

from studio.inference import InferenceEngine, InferenceError
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.screens import ApiSettingsScreen, DrawWizardScreen, ProfileSetupScreen
from studio.screens_library import ConstraintLibraryScreen
from studio.utils.draw_store import load_draw
from studio.utils.profile_store import load_profile
from studio.utils.prompt_builder import PromptBuilder
from studio.utils.treatment_store import (
    convert_treatment_to_markdown,
    save_treatment_output,
)
from studio.workspace import DEFAULT_WELCOME_MARKDOWN, StudioWorkspace


class HeaderHUD(Static):
    """Persistent Header HUD widget displaying application title and version."""

    profile: reactive[Optional[TeamProfile]] = reactive(None)
    draw: reactive[Optional[FridayDraw]] = reactive(None)

    DEFAULT_CSS = """
    HeaderHUD {
        dock: top;
        height: 3;
        background: $accent-darken-2;
        color: $text;
        content-align: center middle;
        text-style: bold;
        border-bottom: solid $accent;
    }
    """

    def watch_profile(self, profile: Optional[TeamProfile]) -> None:
        self.update_content()

    def watch_draw(self, draw: Optional[FridayDraw]) -> None:
        self.update_content()

    def on_mount(self) -> None:
        self.update_content()

    def update_content(self) -> None:
        team_str = f" | Team: {self.profile.team_name}" if self.profile else ""
        self.update(f"🎬 48HFP-Studio v2.0{team_str}")

    def render(self) -> str:
        team_str = f" | Team: {self.profile.team_name}" if self.profile else ""
        return f"🎬 48HFP-Studio v2.0{team_str}"


class NavigationSidebar(Static):
    """Persistent Left Navigation Sidebar widget."""

    profile: reactive[Optional[TeamProfile]] = reactive(None)

    DEFAULT_CSS = """
    NavigationSidebar {
        width: 34;
        height: 100%;
        background: $surface;
        color: $text;
        border-right: heavy $accent;
        padding: 1 2;
    }

    NavigationSidebar Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def watch_profile(self, profile: Optional[TeamProfile]) -> None:
        self.update_content()

    def on_mount(self) -> None:
        self.update_content()

    def compose(self) -> ComposeResult:
        yield Button("👤 Profile Setup [P]", id="btn_profile_modal", variant="default")
        yield Button("🎲 Friday Draw [D]", id="btn_draw_modal", variant="primary")
        yield Button("📚 Constraints [L]", id="btn_library_modal", variant="default")
        yield Button("⚙️ Settings [S]", id="btn_settings_modal", variant="default")

    def update_content(self) -> None:
        if self.profile:
            team_info = f"[bold green]{self.profile.team_name}[/bold green]"
            admin_info = f"Admin: [cyan]{self.profile.admin_username}[/cyan]"
            log_c = self.profile.active_logistical_constraint or "None"
            dir_v = self.profile.active_directorial_vision or "None"
            them_f = self.profile.active_thematic_framework or "None"
            idea_s = self.profile.active_idea_seed or "None"
            constraint_info = (
                f"Logistics: [yellow]{log_c}[/yellow]\n"
                f"Directorial: [magenta]{dir_v}[/magenta]\n"
                f"Thematic: [blue]{them_f}[/blue]\n"
                f"Idea Seed: [green]{idea_s}[/green]"
            )
        else:
            team_info = "[dim]Team: Unconfigured[/dim]"
            admin_info = "[dim]Admin: N/A[/dim]"
            constraint_info = "[dim]Constraints: None[/dim]"

        content = (
            "🧭 [bold cyan]NAVIGATION[/bold cyan]\n\n"
            "👤 [bold white]TEAM STATUS[/bold white]\n"
            f"• {team_info}\n"
            f"• {admin_info}\n"
            f"• {constraint_info}\n"
        )
        self.update(content)


class StudioApp(App):
    """Main Textual TUI Application for 48HFP-Studio."""

    TITLE = "48HFP-Studio v2.0"

    app_profile: reactive[Optional[TeamProfile]] = reactive(None)
    app_draw: reactive[Optional[FridayDraw]] = reactive(None)
    current_markdown: reactive[str] = reactive(DEFAULT_WELCOME_MARKDOWN)
    is_generating: reactive[bool] = reactive(False)

    CSS = """
    Screen {
        layout: vertical;
        background: $background;
    }

    #workspace-container {
        layout: horizontal;
        height: 1fr;
        width: 100%;
    }
    """

    BINDINGS = [
        ("d", "open_draw_wizard", "Friday Draw"),
        ("p", "open_profile_setup", "Profile Setup"),
        ("l", "open_library", "Constraint Library"),
        ("s", "open_api_settings", "API Settings"),
        ("g", "generate_treatment", "Generate Treatment"),
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the 3-zone layout: Header HUD, Left Sidebar, Main Workspace."""
        yield HeaderHUD(id="header-hud")
        with Horizontal(id="workspace-container"):
            yield NavigationSidebar(id="nav-sidebar")
            yield StudioWorkspace(id="main-workspace")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize reactive application state from persistent stores on mount."""
        self.app_profile = load_profile()
        self.app_draw = load_draw()

    def watch_app_profile(self, profile: Optional[TeamProfile]) -> None:
        """Push app_profile state changes down to child widgets."""
        try:
            self.query_one(NavigationSidebar).profile = profile
            self.query_one(HeaderHUD).profile = profile
            self.query_one(StudioWorkspace).profile = profile
        except Exception:
            pass

    def watch_app_draw(self, draw: Optional[FridayDraw]) -> None:
        """Push app_draw state changes down to child widgets."""
        try:
            self.query_one(StudioWorkspace).draw = draw
            self.query_one(HeaderHUD).draw = draw
        except Exception:
            pass

    def watch_current_markdown(self, markdown_text: str) -> None:
        """Push current_markdown state down to workspace."""
        try:
            self.query_one(StudioWorkspace).markdown_text = markdown_text
        except Exception:
            pass

    def watch_is_generating(self, is_generating: bool) -> None:
        """Push is_generating state down to workspace."""
        try:
            self.query_one(StudioWorkspace).is_generating = is_generating
        except Exception:
            pass

    def action_open_draw_wizard(self) -> None:
        """Push the DrawWizardScreen modal."""
        self.push_screen(DrawWizardScreen(self.app_draw), callback=self.update_draw)

    def action_open_profile_setup(self) -> None:
        """Push the ProfileSetupScreen modal."""
        self.push_screen(ProfileSetupScreen(self.app_profile), callback=self.update_profile)

    def action_open_library(self) -> None:
        """Push the ConstraintLibraryScreen modal."""
        self.push_screen(ConstraintLibraryScreen(self.app_profile), callback=self.update_profile)

    def action_open_api_settings(self) -> None:
        """Push the ApiSettingsScreen modal."""
        self.push_screen(ApiSettingsScreen())

    @work(thread=True)
    def action_generate_treatment(self) -> None:
        """Compile system prompt and generate film treatment in background worker thread."""
        self.call_from_thread(self._set_generating_state, True)
        extra_directives = None
        try:
            from textual.widgets import TextArea
            from studio.workspace import RecipePane
            recipe_pane = self.query_one(RecipePane)
            ta = recipe_pane.query_one("#additional_instructions", TextArea)
            extra_directives = ta.text
        except Exception:
            pass

        try:
            prompt = PromptBuilder.compile_system_prompt(
                draw=self.app_draw,
                profile=self.app_profile,
                additional_instructions=extra_directives,
            )
            treatment = InferenceEngine.generate_treatment(prompt=prompt)
            saved_path = save_treatment_output(treatment, prompt_text=prompt)
            md_content = convert_treatment_to_markdown(treatment, prompt_text=prompt)
            header = f"> 💾 **Saved to:** `{saved_path}`\n\n"
            final_md = header + md_content
            self.call_from_thread(self._on_treatment_success, final_md, str(saved_path))
        except InferenceError as err:
            err_msg = str(err)
            error_md = (
                f"# ❌ Generation Failed\n\n"
                f"> **Inference Error:**\n```\n{err_msg}\n```\n\n"
                f"Please verify your `GEMINI_API_KEY` environment variable or try again."
            )
            self.call_from_thread(self._on_treatment_error, error_md, err_msg)
        except Exception as err:
            err_msg = str(err)
            error_md = (
                f"# ❌ Unexpected Error\n\n"
                f"> **Error:**\n```\n{err_msg}\n```"
            )
            self.call_from_thread(self._on_treatment_error, error_md, err_msg)

    def _set_generating_state(self, state: bool) -> None:
        self.is_generating = state

    def _on_treatment_success(self, md_content: str, saved_path: str) -> None:
        self.current_markdown = md_content
        self.is_generating = False
        self.notify(
            f"Treatment saved to {saved_path}",
            title="Treatment Generated",
            severity="information",
        )

    def _on_treatment_error(self, error_md: str, err_msg: str) -> None:
        self.current_markdown = error_md
        self.is_generating = False
        self.notify(
            f"Generation failed: {err_msg}",
            title="Generation Error",
            severity="error",
        )

    def update_draw(self, new_draw: Optional[FridayDraw]) -> None:
        """Callback invoked when DrawWizardScreen is dismissed."""
        if new_draw is not None:
            self.app_draw = load_draw() or new_draw

    def update_profile(self, new_profile: Optional[TeamProfile]) -> None:
        """Callback invoked when ProfileSetupScreen or ConstraintLibraryScreen is dismissed."""
        if new_profile is not None:
            self.app_profile = load_profile() or new_profile

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses from sidebar or workspace."""
        if event.button.id == "btn_draw_modal":
            self.action_open_draw_wizard()
        elif event.button.id == "btn_profile_modal":
            self.action_open_profile_setup()
        elif event.button.id == "btn_library_modal":
            self.action_open_library()
        elif event.button.id == "btn_settings_modal":
            self.action_open_api_settings()
        elif event.button.id == "btn_generate_treatment":
            self.action_generate_treatment()


if __name__ == "__main__":
    app = StudioApp()
    app.run()
