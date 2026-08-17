"""Stateful Terminal User Interface (TUI) for 48HFP-Studio using Textual."""

from pathlib import Path
from typing import Any, List, Optional
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Label, Static

from studio.inference import InferenceEngine, InferenceError
from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile
from studio.models.shotlist import ShotItem, ShotListBase
from studio.models.treatment import TreatmentOutput
from studio.screens import ApiSettingsScreen, DrawWizardScreen, ProfileSetupScreen
from studio.screens_library import ConstraintLibraryScreen
from studio.screens_load import LoadDraftsScreen
from studio.screens_quiz import OnboardingQuizScreen
from studio.screens_screenplay import ScreenplayWorkspace
from studio.screens_shotlist import ShotListWorkspace
from studio.screens_storyboard import StoryboardsWorkspace
from studio.screens_workspace import WorkspaceManagerScreen
from studio.utils.asset_store import save_shotlist_csv, save_storyboard_image
from studio.utils.draw_store import load_draw
from studio.utils.global_state import get_active_workspace
from studio.utils.profile_store import load_profile
from studio.utils.prompt_builder import PromptBuilder
from studio.utils.screenplay_store import save_screenplay_output
from studio.utils.treatment_store import (
    convert_treatment_to_markdown,
    save_treatment_output,
)
from studio.workspace import DEFAULT_WELCOME_MARKDOWN, RecipePane, StudioWorkspace


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
        self.update(f"🎬 48HFP-Studio v3.0{ws_str}{team_str}")

    def render(self) -> str:
        ws = get_active_workspace()
        ws_str = f" | Workspace: {ws.name}" if ws else ""
        team_str = f" | Team: {self.profile.team_name}" if self.profile else ""
        return f"🎬 48HFP-Studio v3.0{ws_str}{team_str}"


class NavigationSidebar(Static):
    """Persistent Left Navigation Sidebar widget."""

    profile: reactive[Optional[TeamProfile]] = reactive(None)
    draw: reactive[Optional[FridayDraw]] = reactive(None)
    active_view: reactive[str] = reactive("treatment")

    DEFAULT_CSS = """
    NavigationSidebar {
        width: 34;
        height: 100%;
        background: $surface;
        color: $text;
        border-right: heavy $accent;
        padding: 1 2;
    }

    .nav-section-label {
        color: $accent;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }

    NavigationSidebar Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def watch_profile(self, profile: Optional[TeamProfile]) -> None:
        self.update_badges()

    def watch_draw(self, draw: Optional[FridayDraw]) -> None:
        self.update_badges()

    def update_badges(self) -> None:
        try:
            btn_prof = self.query_one("#btn_profile_modal", Button)
            btn_prof.label = f"👤 Profile: {self.profile.team_name[:12]}" if self.profile else "👤 Team Profile [P]"
        except Exception:
            pass
        try:
            btn_draw = self.query_one("#btn_draw_modal", Button)
            btn_draw.label = f"🎲 Draw: {self.draw.genre_1[:10]}" if self.draw else "🎲 Friday Draw [D]"
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        yield Label("📋 WORKSPACE VIEWS", classes="nav-section-label")
        yield Button(
            "📝 Treatment [1]",
            id="btn_nav_treatment",
            variant="primary" if self.active_view == "treatment" else "default",
        )
        yield Button(
            "📜 Screenplay [2]",
            id="btn_nav_screenplay",
            variant="primary" if self.active_view == "screenplay" else "default",
        )
        yield Button(
            "🎥 Shot List [3]",
            id="btn_nav_shotlist",
            variant="primary" if self.active_view == "shotlist" else "default",
        )
        yield Button(
            "🖼️ Storyboards [4]",
            id="btn_nav_storyboards",
            variant="primary" if self.active_view == "storyboards" else "default",
        )

        yield Label("⚙️ PROJECT SETUP", classes="nav-section-label")
        yield Button("👤 Team Profile [P]", id="btn_profile_modal")
        yield Button("📁 Workspace Manager [W]", id="btn_workspace_modal")
        yield Button("📂 Load Saved Drafts [O]", id="btn_load_drafts")
        yield Button("❓ Creative Quiz [Q]", id="btn_quiz_modal")
        yield Button("📚 Constraint Library [C]", id="btn_library_modal")
        yield Button("🎲 Friday Draw [D]", id="btn_draw_modal")
        yield Button("⚙️ Settings [S]", id="btn_settings_modal")

    def watch_active_view(self, active_view: str) -> None:
        try:
            b1 = self.query_one("#btn_nav_treatment", Button)
            b2 = self.query_one("#btn_nav_screenplay", Button)
            b3 = self.query_one("#btn_nav_shotlist", Button)
            b4 = self.query_one("#btn_nav_storyboards", Button)
            b1.variant = "primary" if active_view == "treatment" else "default"
            b2.variant = "primary" if active_view == "screenplay" else "default"
            b3.variant = "primary" if active_view == "shotlist" else "default"
            b4.variant = "primary" if active_view == "storyboards" else "default"
        except Exception:
            pass


class StudioApp(App):
    """Main Textual TUI Application for 48HFP-Studio."""

    TITLE = "48HFP-Studio v3.0"

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
    current_shotlist_data: reactive[Any] = reactive(None)
    is_generating_shotlist: reactive[bool] = reactive(False)
    current_storyboards_data: reactive[List[str]] = reactive([])
    is_generating_storyboards: reactive[bool] = reactive(False)

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
        ("1", "switch_to_treatment_view", "Treatment [1]"),
        ("2", "switch_to_screenplay_view", "Screenplay [2]"),
        ("3", "switch_to_shotlist_view", "Shot List [3]"),
        ("4", "switch_to_storyboard_view", "Storyboards [4]"),
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
        """Compose the 3-zone layout: Header HUD, Left Sidebar, Main Workspaces."""
        yield HeaderHUD(id="header-hud")
        with Horizontal(id="workspace-container"):
            yield NavigationSidebar(id="nav-sidebar")
            yield StudioWorkspace(id="main-workspace")
            yield ScreenplayWorkspace(id="screenplay-workspace")
            yield ShotListWorkspace(id="shotlist-workspace")
            yield StoryboardsWorkspace(id="storyboard-workspace")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize reactive application state from persistent stores on mount."""
        self.app_profile = load_profile()
        self.app_draw = load_draw()
        self.watch_active_view(self.active_view)

    def watch_active_view(self, active_view: str) -> None:
        """Toggle active workspace view among Treatment, Screenplay, Shot List, and Storyboards."""
        try:
            ws = self.query_one("#main-workspace", StudioWorkspace)
            sp = self.query_one("#screenplay-workspace", ScreenplayWorkspace)
            sl = self.query_one("#shotlist-workspace", ShotListWorkspace)
            sb = self.query_one("#storyboard-workspace", StoryboardsWorkspace)
            nav = self.query_one("#nav-sidebar", NavigationSidebar)

            ws.display = (active_view == "treatment")
            sp.display = (active_view == "screenplay")
            sl.display = (active_view == "shotlist")
            sb.display = (active_view == "storyboards")

            nav.active_view = active_view
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

    def watch_current_shotlist_data(self, data: Any) -> None:
        """Push current_shotlist_data down to ShotListWorkspace."""
        try:
            sl = self.query_one("#shotlist-workspace", ShotListWorkspace)
            sl.shotlist_data = data
        except Exception:
            pass

    def watch_is_generating_shotlist(self, is_gen: bool) -> None:
        """Push is_generating_shotlist state down to ScreenplayWorkspace and ShotListWorkspace."""
        try:
            sp = self.query_one("#screenplay-workspace", ScreenplayWorkspace)
            sp.is_generating_shotlist = is_gen
        except Exception:
            pass
        try:
            sl = self.query_one("#shotlist-workspace", ShotListWorkspace)
            sl.is_generating = is_gen
        except Exception:
            pass

    def watch_current_storyboards_data(self, data: List[str]) -> None:
        """Push current_storyboards_data down to StoryboardsWorkspace."""
        try:
            sb = self.query_one("#storyboard-workspace", StoryboardsWorkspace)
            sb.storyboards_data = data
        except Exception:
            pass

    def watch_is_generating_storyboards(self, is_gen: bool) -> None:
        """Push is_generating_storyboards state down to ShotListWorkspace and StoryboardsWorkspace."""
        try:
            sl = self.query_one("#shotlist-workspace", ShotListWorkspace)
            sl.is_generating_storyboards = is_gen
        except Exception:
            pass
        try:
            sb = self.query_one("#storyboard-workspace", StoryboardsWorkspace)
            sb.is_generating = is_gen
        except Exception:
            pass

    def watch_app_profile(self, profile: Optional[TeamProfile]) -> None:
        """Push app_profile state changes down to child widgets."""
        try:
            self.query_one(HeaderHUD).profile = profile
        except Exception:
            pass
        try:
            self.query_one(StudioWorkspace).profile = profile
        except Exception:
            pass
        try:
            self.query_one(NavigationSidebar).profile = profile
        except Exception:
            pass

    def watch_app_draw(self, draw: Optional[FridayDraw]) -> None:
        """Push app_draw state changes down to child widgets."""
        try:
            self.query_one(StudioWorkspace).draw = draw
        except Exception:
            pass
        try:
            self.query_one(HeaderHUD).draw = draw
        except Exception:
            pass
        try:
            self.query_one(NavigationSidebar).draw = draw
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
        """Switch active workspace view to Treatment view."""
        self.active_view = "treatment"

    def action_switch_to_screenplay_view(self) -> None:
        """Switch active workspace view to Screenplay view."""
        self.active_view = "screenplay"

    def action_switch_to_shotlist_view(self) -> None:
        """Switch active workspace view to Shot List view."""
        self.active_view = "shotlist"

    def action_switch_to_storyboard_view(self) -> None:
        """Switch active workspace view to Storyboards view."""
        self.active_view = "storyboards"

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
        elif d_type == "shotlist":
            self.current_shotlist_data = content
            self.active_view = "shotlist"
            self.notify(f"Loaded shot list draft from {file_path}", title="Shot List Loaded", severity="information")

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
            recipe_pane = self.query_one(RecipePane)
            ta = recipe_pane.query_one("#additional_instructions", TextArea)
            extra_directives = ta.text
        except Exception:
            pass

        try:
            draw_data = self.app_draw or load_draw()
            profile_data = self.app_profile or load_profile()

            prompt = PromptBuilder.compile_system_prompt(
                draw=draw_data,
                profile=profile_data,
                additional_instructions=extra_directives,
            )

            treatment_obj = InferenceEngine.generate_treatment(prompt)
            markdown_content = convert_treatment_to_markdown(treatment_obj, prompt_text=prompt)

            saved_path = save_treatment_output(treatment_obj, prompt_text=prompt)

            self.call_from_thread(
                self._on_treatment_success,
                treatment_obj,
                markdown_content,
                prompt,
                str(saved_path),
            )

        except InferenceError as err:
            err_msg = str(err)
            self.call_from_thread(self._on_treatment_error, err_msg)
        except Exception as err:
            err_msg = str(err)
            self.call_from_thread(self._on_treatment_error, err_msg)

    def _set_generating_state(self, state: bool) -> None:
        self.is_generating = state

    def _on_treatment_success(
        self,
        treatment_obj: TreatmentOutput,
        markdown_content: str,
        prompt: str,
        saved_path_str: str,
    ) -> None:
        self.is_generating = False
        self.current_treatment_obj = treatment_obj
        self.current_markdown = f"{markdown_content}\n\n---\n*Saved to `{saved_path_str}`*"
        self.current_prompt_text = prompt
        self.notify(
            f"Saved treatment to {saved_path_str}",
            title="Treatment Saved",
            severity="information",
        )

    def _on_treatment_error(self, err_msg: str) -> None:
        self.is_generating = False
        self.current_markdown = (
            f"# ❌ Generation Failed\n\n"
            f"**Error Details:**\n```\n{err_msg}\n```\n\n"
            f"Please check your API key under `Settings [S]` and verify that your constraints and Friday draw are valid."
        )
        self.notify(
            f"Treatment generation failed: {err_msg}",
            title="Generation Error",
            severity="error",
        )

    @work(thread=True)
    def action_revise_treatment(self) -> None:
        """Revise the active treatment based on director feedback instructions."""
        from textual.widgets import TextArea
        from studio.workspace import RevisionPane

        if not self.current_treatment_obj:
            self.notify(
                "No active treatment to revise. Generate a treatment first.",
                title="Revision Warning",
                severity="warning",
            )
            return

        revision_notes = ""
        try:
            rev_pane = self.query_one(RevisionPane)
            ta = rev_pane.query_one("#revision_notes_input", TextArea)
            revision_notes = ta.text
        except Exception:
            pass

        if not revision_notes.strip():
            self.notify(
                "Please enter revision instructions before submitting.",
                title="Instructions Required",
                severity="warning",
            )
            return

        self.call_from_thread(self._set_revising_state, True)

        try:
            profile_data = self.app_profile or load_profile()
            draw_data = self.app_draw or load_draw()
            compiled_prompt = PromptBuilder.compile_revision_prompt(
                current_treatment=self.current_treatment_obj,
                notes=revision_notes,
                original_prompt=self.current_prompt_text,
                draw=draw_data,
                profile=profile_data,
            )

            revised_treatment = InferenceEngine.generate_treatment(compiled_prompt)
            markdown_content = convert_treatment_to_markdown(revised_treatment, prompt_text=compiled_prompt)
            saved_path = save_treatment_output(revised_treatment, prompt_text=compiled_prompt)

            self.call_from_thread(
                self._on_revision_success,
                revised_treatment,
                markdown_content,
                compiled_prompt,
                str(saved_path),
            )

        except InferenceError as err:
            err_msg = str(err)
            self.call_from_thread(self._on_revision_error, err_msg)
        except Exception as err:
            err_msg = str(err)
            self.call_from_thread(self._on_revision_error, err_msg)

    def _set_revising_state(self, state: bool) -> None:
        self.is_revising = state

    def _on_revision_success(
        self,
        revised_treatment: TreatmentOutput,
        markdown_content: str,
        prompt: str,
        saved_path_str: str,
    ) -> None:
        self.is_revising = False
        self.current_treatment_obj = revised_treatment
        self.current_markdown = f"{markdown_content}\n\n---\n*Saved to `{saved_path_str}`*"
        self.current_prompt_text = prompt

        try:
            from textual.widgets import TextArea
            from studio.workspace import RevisionPane
            rev_pane = self.query_one(RevisionPane)
            ta = rev_pane.query_one("#revision_notes_input", TextArea)
            ta.text = ""
        except Exception:
            pass

        self.notify(
            f"Saved revised treatment to {saved_path_str}",
            title="Treatment Revised",
            severity="information",
        )

    def _on_revision_error(self, err_msg: str) -> None:
        self.is_revising = False
        self.current_markdown = (
            f"# ❌ Revision Failed\n\n"
            f"**Error Details:**\n```\n{err_msg}\n```"
        )
        self.notify(
            f"Treatment revision failed: {err_msg}",
            title="Revision Error",
            severity="error",
        )

    @work(thread=True)
    def action_generate_screenplay(self) -> None:
        """Compile screenplay prompt and generate full script in background worker thread."""
        if not self.current_treatment_obj:
            self.notify(
                "Please generate or load a treatment before generating a screenplay.",
                title="Treatment Required",
                severity="warning",
            )
            return

        self.call_from_thread(self._set_screenplay_generating_state, True)

        try:
            prompt = PromptBuilder.compile_screenplay_prompt(
                treatment=self.current_treatment_obj,
                draw=self.app_draw,
                profile=self.app_profile,
            )

            raw_fountain = InferenceEngine.generate_screenplay(prompt)
            title = "Untitled"
            if self.current_treatment_obj and self.current_treatment_obj.title_and_logline:
                title = self.current_treatment_obj.title_and_logline.title

            saved_path = save_screenplay_output(raw_fountain, title=title)

            self.call_from_thread(
                self._on_screenplay_success,
                raw_fountain,
                str(saved_path),
            )

        except InferenceError as err:
            err_msg = str(err)
            self.call_from_thread(self._on_screenplay_error, err_msg)
        except Exception as err:
            err_msg = str(err)
            self.call_from_thread(self._on_screenplay_error, err_msg)

    def _set_screenplay_generating_state(self, state: bool) -> None:
        self.is_generating_screenplay = state
        self.active_view = "screenplay"

    def _on_screenplay_success(
        self,
        fountain_text: str,
        saved_path_str: str,
    ) -> None:
        self.is_generating_screenplay = False
        self.current_screenplay_text = fountain_text
        self.active_view = "screenplay"
        self.notify(
            f"Saved screenplay to {saved_path_str}",
            title="Screenplay Saved",
            severity="information",
        )

    def _on_screenplay_error(self, err_msg: str) -> None:
        self.is_generating_screenplay = False
        self.notify(
            f"Screenplay generation failed: {err_msg}",
            title="Screenplay Error",
            severity="error",
        )

    @work(thread=True)
    def action_generate_shotlist(self) -> None:
        """Extract shot list items from active screenplay in background worker thread."""
        if not self.current_screenplay_text:
            self.notify(
                "Please generate or load a screenplay before generating a shot list.",
                title="Screenplay Required",
                severity="warning",
            )
            return

        self.call_from_thread(self._set_shotlist_generating_state, True)

        try:
            prompt = PromptBuilder.compile_shotlist_prompt(
                screenplay_text=self.current_screenplay_text,
                profile=self.app_profile,
                draw=self.app_draw,
            )

            shotlist_obj = InferenceEngine.generate_shotlist(prompt)
            title = "Untitled"
            if self.current_treatment_obj and self.current_treatment_obj.title_and_logline:
                title = self.current_treatment_obj.title_and_logline.title

            saved_path = save_shotlist_csv(shotlist_obj, title=title)

            self.call_from_thread(
                self._on_shotlist_success,
                shotlist_obj,
                str(saved_path),
            )

        except InferenceError as err:
            err_msg = str(err)
            self.call_from_thread(self._on_shotlist_error, err_msg)
        except Exception as err:
            err_msg = str(err)
            self.call_from_thread(self._on_shotlist_error, err_msg)

    def _set_shotlist_generating_state(self, state: bool) -> None:
        self.is_generating_shotlist = state
        self.active_view = "shotlist"

    def _on_shotlist_success(
        self,
        shotlist_obj: ShotListBase,
        saved_path_str: str,
    ) -> None:
        self.is_generating_shotlist = False
        self.current_shotlist_data = shotlist_obj
        self.active_view = "shotlist"
        self.notify(
            f"Saved shot list to {saved_path_str}",
            title="Shot List Saved",
            severity="information",
        )

    def _on_shotlist_error(self, err_msg: str) -> None:
        self.is_generating_shotlist = False
        self.notify(
            f"Shot list generation failed: {err_msg}",
            title="Shot List Error",
            severity="error",
        )

    @work(thread=True)
    def action_generate_storyboards(self) -> None:
        """Generate 16:9 monochrome pre-vis storyboards for active shot list in background worker thread."""
        if not self.current_shotlist_data:
            self.notify(
                "Please generate or load a shot list before generating storyboards.",
                title="Shot List Required",
                severity="warning",
            )
            return

        shots: List[ShotItem] = []
        if isinstance(self.current_shotlist_data, ShotListBase):
            shots = self.current_shotlist_data.shots
        elif isinstance(self.current_shotlist_data, list):
            for row in self.current_shotlist_data:
                if isinstance(row, ShotItem):
                    shots.append(row)
                elif isinstance(row, dict):
                    cast_raw = row.get("Cast", row.get("cast", []))
                    cast_list = cast_raw if isinstance(cast_raw, list) else [c.strip() for c in str(cast_raw or "").split(",") if c.strip()]
                    try:
                        shot_num = int(row.get("Shot", row.get("shot_number", 1)))
                    except Exception:
                        shot_num = 1
                    shots.append(ShotItem(
                        shot_number=shot_num,
                        scene_number=str(row.get("Scene", row.get("scene_number", "1"))),
                        location=str(row.get("Location", row.get("location", ""))),
                        setup=str(row.get("Setup", row.get("setup", ""))),
                        shot_size=str(row.get("Shot Size", row.get("shot_size", "MS"))),
                        camera_movement=str(row.get("Camera Movement", row.get("camera_movement", "Static"))),
                        cast=cast_list,
                        description=str(row.get("Description", row.get("description", ""))),
                    ))

        if not shots:
            self.notify(
                "No valid shots found in the active shot list.",
                title="Empty Shot List",
                severity="warning",
            )
            return

        self.call_from_thread(self._set_storyboard_generating_state, True)

        saved_paths: List[str] = []
        try:
            directorial_vision = None
            if self.app_profile and self.app_profile.active_directorial_vision:
                from studio.utils.constraint_store import load_directorial_vision
                directorial_vision = load_directorial_vision(self.app_profile.active_directorial_vision)

            title = "Untitled"
            if self.current_treatment_obj and self.current_treatment_obj.title_and_logline:
                title = self.current_treatment_obj.title_and_logline.title

            for shot in shots:
                prompt = PromptBuilder.compile_storyboard_prompt(shot, directorial_vision)
                image_bytes = InferenceEngine.generate_storyboard_image(prompt)
                saved_path = save_storyboard_image(
                    image_bytes=image_bytes,
                    shot_number=shot.shot_number,
                    scene_number=str(shot.scene_number),
                    title=title,
                )
                saved_paths.append(str(saved_path))

            self.call_from_thread(self._on_storyboard_success, saved_paths)

        except InferenceError as err:
            err_msg = str(err)
            self.call_from_thread(self._on_storyboard_error, err_msg)
        except Exception as err:
            err_msg = str(err)
            self.call_from_thread(self._on_storyboard_error, err_msg)

    def _set_storyboard_generating_state(self, state: bool) -> None:
        self.is_generating_storyboards = state
        self.active_view = "storyboards"

    def _on_storyboard_success(self, saved_paths: List[str]) -> None:
        self.is_generating_storyboards = False
        self.current_storyboards_data = saved_paths
        self.active_view = "storyboards"
        sb_dir = Path(saved_paths[0]).parent if saved_paths else "storyboards/"
        self.notify(
            f"Generated {len(saved_paths)} storyboard images in {sb_dir}",
            title="Storyboards Generated",
            severity="information",
        )

    def _on_storyboard_error(self, err_msg: str) -> None:
        self.is_generating_storyboards = False
        self.notify(
            f"Storyboard generation failed: {err_msg}",
            title="Storyboard Error",
            severity="error",
        )

    def update_draw(self, new_draw: Optional[FridayDraw]) -> None:
        """Callback invoked when DrawWizardScreen is dismissed."""
        if new_draw is not None:
            self.app_draw = load_draw() or new_draw
        try:
            self.query_one(NavigationSidebar).draw = self.app_draw
            self.query_one(StudioWorkspace).draw = self.app_draw
            self.query_one(RecipePane).draw = self.app_draw
            self.query_one(RecipePane).update_content()
            self.query_one(HeaderHUD).draw = self.app_draw
            self.query_one(HeaderHUD).update_content()
        except Exception:
            pass

    def update_profile(self, new_profile: Optional[TeamProfile]) -> None:
        """Callback invoked when ProfileSetupScreen or ConstraintLibraryScreen is dismissed."""
        if new_profile is not None:
            self.app_profile = load_profile() or new_profile
        try:
            self.query_one(NavigationSidebar).profile = self.app_profile
            self.query_one(StudioWorkspace).profile = self.app_profile
            self.query_one(RecipePane).profile = self.app_profile
            self.query_one(RecipePane).update_content()
            self.query_one(HeaderHUD).profile = self.app_profile
            self.query_one(HeaderHUD).update_content()
        except Exception:
            pass

    def update_workspace(self, new_workspace: Optional[Path]) -> None:
        """Callback invoked when WorkspaceManagerScreen is dismissed."""
        if new_workspace is not None:
            self.app_profile = load_profile()
            self.app_draw = load_draw()
            try:
                self.query_one(NavigationSidebar).profile = self.app_profile
                self.query_one(NavigationSidebar).draw = self.app_draw
                self.query_one(StudioWorkspace).profile = self.app_profile
                self.query_one(StudioWorkspace).draw = self.app_draw
                self.query_one(RecipePane).profile = self.app_profile
                self.query_one(RecipePane).draw = self.app_draw
                self.query_one(RecipePane).update_content()
                self.query_one(HeaderHUD).profile = self.app_profile
                self.query_one(HeaderHUD).draw = self.app_draw
                self.query_one(HeaderHUD).update_content()
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses from sidebar or workspace."""
        if event.button.id == "btn_nav_treatment":
            self.action_switch_to_treatment_view()
        elif event.button.id == "btn_nav_screenplay":
            self.action_switch_to_screenplay_view()
        elif event.button.id == "btn_nav_shotlist":
            self.action_switch_to_shotlist_view()
        elif event.button.id == "btn_nav_storyboards":
            self.action_switch_to_storyboard_view()
        elif event.button.id == "btn_profile_modal":
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
        elif event.button.id in ("btn_generate_screenplay", "btn_empty_generate_screenplay"):
            self.action_generate_screenplay()
        elif event.button.id in ("btn_generate_shotlist", "btn_empty_generate_shotlist"):
            self.action_generate_shotlist()
        elif event.button.id in ("btn_generate_storyboards", "btn_empty_generate_storyboards", "btn_regen_storyboards"):
            self.action_generate_storyboards()
        elif event.button.id == "btn_back_to_treatment":
            self.action_switch_to_treatment_view()
        elif event.button.id == "btn_back_to_screenplay":
            self.action_switch_to_screenplay_view()
        elif event.button.id == "btn_back_to_shotlist":
            self.action_switch_to_shotlist_view()


if __name__ == "__main__":
    app = StudioApp()
    app.run()
