"""Stateful Terminal User Interface (TUI) for 48HFP-Studio using Textual."""

from pathlib import Path
from typing import Optional
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Label, Static

from studio.inference import InferenceEngine, InferenceError
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.models.treatment import TreatmentOutput
from studio.screens import ApiSettingsScreen, DrawWizardScreen, ProfileSetupScreen
from studio.screens_library import ConstraintLibraryScreen
from studio.screens_load import LoadDraftsScreen
from studio.screens_quiz import OnboardingQuizScreen
from studio.screens_screenplay import ScreenplayWorkspace
from studio.screens_workspace import WorkspaceManagerScreen
from studio.utils.draw_store import load_draw
from studio.utils.global_state import get_active_workspace
from studio.utils.profile_store import load_profile
from studio.utils.prompt_builder import PromptBuilder
from studio.utils.screenplay_store import save_screenplay_output
from studio.utils.treatment_store import (
    convert_treatment_to_markdown,
    save_treatment_output,
)
from studio.workspace import DEFAULT_WELCOME_MARKDOWN, StudioWorkspace


class HeaderHUD(Static):
    """Persistent Header HUD widget displaying application title, active workspace, and team profile."""

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
        ws = get_active_workspace()
        ws_str = f" | Workspace: {ws.name}" if ws else ""
        team_str = f" | Team: {self.profile.team_name}" if self.profile else ""
        self.update(f"🎬 48HFP-Studio v2.0{ws_str}{team_str}")

    def render(self) -> str:
        ws = get_active_workspace()
        ws_str = f" | Workspace: {ws.name}" if ws else ""
        team_str = f" | Team: {self.profile.team_name}" if self.profile else ""
        return f"🎬 48HFP-Studio v2.0{ws_str}{team_str}"


class NavigationSidebar(Static):
    """Persistent Left Navigation Sidebar widget."""

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

    def compose(self) -> ComposeResult:
        yield Button("👤 Profile Setup [P]", id="btn_profile_modal", variant="default")
        yield Button("📂 Workspace Manager [W]", id="btn_workspace_modal", variant="default")
        yield Button("📂 Load Drafts [O]", id="btn_load_drafts", variant="default")
        yield Button("🔮 Filmmaker Quiz [Z]", id="btn_quiz_modal", variant="default")
        yield Button("📚 Constraints [L]", id="btn_library_modal", variant="default")
        yield Button("🎲 Friday Draw [D]", id="btn_draw_modal", variant="primary")
        yield Button("⚙️ Settings [S]", id="btn_settings_modal", variant="default")


class StudioApp(App):
    """Main Textual TUI Application for 48HFP-Studio."""

    TITLE = "48HFP-Studio v2.0"

    app_profile: reactive[Optional[TeamProfile]] = reactive(None)
    app_draw: reactive[Optional[FridayDraw]] = reactive(None)
    current_markdown: reactive[str] = reactive(DEFAULT_WELCOME_MARKDOWN)
    is_generating: reactive[bool] = reactive(False)
    current_treatment_obj: reactive[Optional[TreatmentOutput]] = reactive(None)
    current_prompt_text: reactive[Optional[str]] = reactive(None)
    is_revising: reactive[bool] = reactive(False)

    active_view: reactive[str] = reactive("treatment")
    current_screenplay_text: reactive[str] = reactive("")
    is_generating_screenplay: reactive[bool] = reactive(False)

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
        ("p", "open_profile_setup", "Profile Setup"),
        ("w", "open_workspace_manager", "Workspace Manager"),
        ("o", "open_load_drafts", "Load Drafts"),
        ("z", "open_quiz", "Filmmaker Quiz"),
        ("l", "open_library", "Constraint Library"),
        ("d", "open_draw_wizard", "Friday Draw"),
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
            yield ScreenplayWorkspace(id="screenplay-workspace")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize reactive application state from persistent stores on mount."""
        self.app_profile = load_profile()
        self.app_draw = load_draw()
        self.watch_active_view(self.active_view)

    def watch_active_view(self, active_view: str) -> None:
        """Toggle workspace view between Treatment workspace and Screenplay workspace."""
        try:
            ws = self.query_one("#main-workspace", StudioWorkspace)
            sp = self.query_one("#screenplay-workspace", ScreenplayWorkspace)
            if active_view == "screenplay":
                ws.display = False
                sp.display = True
            else:
                ws.display = True
                sp.display = False
        except Exception:
            pass

    def watch_current_screenplay_text(self, text: str) -> None:
        """Push current_screenplay_text down to ScreenplayWorkspace."""
        try:
            sp = self.query_one("#screenplay-workspace", ScreenplayWorkspace)
            sp.fountain_text = text
        except Exception:
            pass

    def watch_is_generating_screenplay(self, is_gen: bool) -> None:
        """Push is_generating_screenplay state down to workspaces."""
        try:
            ws = self.query_one("#main-workspace", StudioWorkspace)
            sp = self.query_one("#screenplay-workspace", ScreenplayWorkspace)
            ws.is_generating_screenplay = is_gen
            sp.is_generating = is_gen
        except Exception:
            pass

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

    def watch_current_treatment_obj(self, treatment: Optional[TreatmentOutput]) -> None:
        """Push current_treatment_obj state down to workspace."""
        try:
            self.query_one(StudioWorkspace).has_treatment = (treatment is not None)
        except Exception:
            pass

    def watch_is_revising(self, is_revising: bool) -> None:
        """Push is_revising state down to workspace."""
        try:
            self.query_one(StudioWorkspace).is_revising = is_revising
        except Exception:
            pass

    def action_switch_to_treatment_view(self) -> None:
        """Switch active workspace view back to Treatment view."""
        self.active_view = "treatment"

    def action_switch_to_screenplay_view(self) -> None:
        """Switch active workspace view to Screenplay view."""
        self.active_view = "screenplay"

    def action_open_draw_wizard(self) -> None:
        """Push the DrawWizardScreen modal."""
        self.push_screen(DrawWizardScreen(self.app_draw), callback=self.update_draw)

    def action_open_workspace_manager(self) -> None:
        """Push the WorkspaceManagerScreen modal."""
        self.push_screen(WorkspaceManagerScreen(), callback=self.update_workspace)

    def action_open_load_drafts(self) -> None:
        """Push the LoadDraftsScreen modal."""
        self.push_screen(LoadDraftsScreen(), callback=self.on_load_draft_selected)

    def on_load_draft_selected(self, result: Optional[dict]) -> None:
        """Callback invoked when LoadDraftsScreen is dismissed."""
        if not result:
            return
        d_type = result.get("type")
        content = result.get("content", "")
        file_path = result.get("path", "")

        if d_type == "treatment":
            self.current_markdown = content
            self.active_view = "treatment"
            self.notify(f"Loaded treatment draft from {file_path}", title="Treatment Loaded", severity="information")
        elif d_type == "screenplay":
            self.current_screenplay_text = content
            self.active_view = "screenplay"
            self.notify(f"Loaded screenplay draft from {file_path}", title="Screenplay Loaded", severity="information")

    def action_open_profile_setup(self) -> None:
        """Push the ProfileSetupScreen modal."""
        self.push_screen(ProfileSetupScreen(self.app_profile), callback=self.update_profile)

    def action_open_quiz(self) -> None:
        """Push the OnboardingQuizScreen modal."""
        self.push_screen(OnboardingQuizScreen(), callback=self.update_profile)

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
            self.call_from_thread(self._on_treatment_success, final_md, str(saved_path), treatment, prompt)
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

    @work(thread=True)
    def action_revise_treatment(self) -> None:
        """Revise current treatment with user notes in background worker thread."""
        if not self.current_treatment_obj:
            self.notify("No active treatment to revise.", title="Revision Error", severity="error")
            return

        notes = ""
        try:
            from textual.widgets import TextArea
            from studio.workspace import RevisionPane
            rev_pane = self.query_one(RevisionPane)
            notes_ta = rev_pane.query_one("#revision_notes_input", TextArea)
            notes = notes_ta.text
        except Exception:
            pass

        if not notes or not notes.strip():
            self.notify("Please enter revision notes before submitting.", title="Revision Note Required", severity="warning")
            return

        self.call_from_thread(self._set_revising_state, True)

        try:
            revised_prompt = PromptBuilder.compile_revision_prompt(
                current_treatment=self.current_treatment_obj,
                notes=notes,
                original_prompt=self.current_prompt_text,
                draw=self.app_draw,
                profile=self.app_profile,
            )
            revised_treatment = InferenceEngine.generate_treatment(prompt=revised_prompt)
            saved_path = save_treatment_output(revised_treatment, prompt_text=revised_prompt)
            md_content = convert_treatment_to_markdown(revised_treatment, prompt_text=revised_prompt)
            header = f"> 💾 **Saved to:** `{saved_path}`\n\n"
            final_md = header + md_content
            self.call_from_thread(
                self._on_revision_success,
                final_md,
                str(saved_path),
                revised_treatment,
                revised_prompt,
            )
        except InferenceError as err:
            err_msg = str(err)
            self.call_from_thread(self._on_revision_error, err_msg)
        except Exception as err:
            err_msg = str(err)
            self.call_from_thread(self._on_revision_error, err_msg)

    @work(thread=True)
    def action_generate_screenplay(self) -> None:
        """Compile screenplay prompt and generate Fountain script in background worker thread."""
        if not self.current_treatment_obj:
            self.notify(
                "Please generate or load a film treatment before generating a screenplay.",
                title="Treatment Required",
                severity="warning",
            )
            return

        self.call_from_thread(self._set_screenplay_generating_state, True)
        self.call_from_thread(self.action_switch_to_screenplay_view)

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
            prompt = PromptBuilder.compile_screenplay_prompt(
                treatment=self.current_treatment_obj,
                draw=self.app_draw,
                profile=self.app_profile,
                additional_instructions=extra_directives,
            )
            raw_screenplay = InferenceEngine.generate_screenplay(prompt=prompt)
            title = self.current_treatment_obj.title_and_logline.title
            saved_path = save_screenplay_output(raw_screenplay, title=title)
            self.call_from_thread(
                self._on_screenplay_success,
                raw_screenplay,
                str(saved_path),
            )
        except InferenceError as err:
            err_msg = str(err)
            self.call_from_thread(self._on_screenplay_error, err_msg)
        except Exception as err:
            err_msg = str(err)
            self.call_from_thread(self._on_screenplay_error, err_msg)

    def _set_generating_state(self, state: bool) -> None:
        self.is_generating = state

    def _set_revising_state(self, state: bool) -> None:
        self.is_revising = state

    def _set_screenplay_generating_state(self, state: bool) -> None:
        self.is_generating_screenplay = state

    def _on_treatment_success(
        self,
        md_content: str,
        saved_path: str,
        treatment: TreatmentOutput,
        prompt: str,
    ) -> None:
        self.current_treatment_obj = treatment
        self.current_prompt_text = prompt
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

    def _on_revision_success(
        self,
        md_content: str,
        saved_path: str,
        treatment: TreatmentOutput,
        prompt: str,
    ) -> None:
        self.current_treatment_obj = treatment
        self.current_prompt_text = prompt
        self.current_markdown = md_content
        self.is_revising = False
        try:
            from textual.widgets import TextArea
            from studio.workspace import RevisionPane
            rev_pane = self.query_one(RevisionPane)
            notes_ta = rev_pane.query_one("#revision_notes_input", TextArea)
            notes_ta.text = ""
        except Exception:
            pass

        self.notify(
            f"Revised treatment saved to {saved_path}",
            title="Treatment Revised",
            severity="information",
        )

    def _on_revision_error(self, err_msg: str) -> None:
        self.is_revising = False
        self.notify(
            f"Revision failed: {err_msg}",
            title="Revision Error",
            severity="error",
        )

    def _on_screenplay_success(self, screenplay_text: str, saved_path: str) -> None:
        self.current_screenplay_text = screenplay_text
        self.is_generating_screenplay = False
        self.notify(
            f"Screenplay saved to {saved_path}",
            title="Screenplay Generated",
            severity="information",
        )

    def _on_screenplay_error(self, err_msg: str) -> None:
        self.is_generating_screenplay = False
        self.notify(
            f"Screenplay generation failed: {err_msg}",
            title="Screenplay Error",
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

    def update_workspace(self, new_workspace: Optional[Path]) -> None:
        """Callback invoked when WorkspaceManagerScreen is dismissed."""
        if new_workspace is not None:
            self.app_profile = load_profile()
            self.app_draw = load_draw()
            try:
                self.query_one(HeaderHUD).update_content()
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses from sidebar or workspace."""
        if event.button.id == "btn_profile_modal":
            self.action_open_profile_setup()
        elif event.button.id == "btn_workspace_modal":
            self.action_open_workspace_manager()
        elif event.button.id == "btn_load_drafts":
            self.action_open_load_drafts()
        elif event.button.id == "btn_quiz_modal":
            self.action_open_quiz()
        elif event.button.id == "btn_library_modal":
            self.action_open_library()
        elif event.button.id == "btn_draw_modal":
            self.action_open_draw_wizard()
        elif event.button.id == "btn_settings_modal":
            self.action_open_api_settings()
        elif event.button.id == "btn_generate_treatment":
            self.action_generate_treatment()
        elif event.button.id == "btn_submit_revision":
            self.action_revise_treatment()
        elif event.button.id == "btn_generate_screenplay":
            self.action_generate_screenplay()


if __name__ == "__main__":
    app = StudioApp()
    app.run()
