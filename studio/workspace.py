"""Split-pane Workspace widgets for 48HFP-Studio TUI."""

from typing import Optional
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Label, LoadingIndicator, Markdown, Static, TextArea

from studio.models.draw import FridayDraw
from studio.models.profile import TeamProfile

DEFAULT_WELCOME_MARKDOWN = """# 🎬 Film Treatment Workspace

Welcome to **48HFP-Studio Treatment Generator**.

### How it works:
1. Ensure your **Team Profile** and **Friday Draw** parameters are configured using the sidebar buttons `[P]` and `[D]`.
2. Click **⚡ Generate Treatment [G]** or press `G` on your keyboard.
3. The AI engine will compile the system prompt and stream your structured Markdown film treatment here.

---
*Ready for kickoff!*
"""


class RecipePane(Static):
    """Left Split Pane displaying Team Profile, Friday Draw parameters, and Generation controls."""

    profile: reactive[Optional[TeamProfile]] = reactive(None)
    draw: reactive[Optional[FridayDraw]] = reactive(None)
    is_generating: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    RecipePane {
        width: 1fr;
        height: 100%;
        background: $surface;
        color: $text;
        border-right: heavy $accent;
        padding: 1 2;
        layout: vertical;
    }

    #recipe-scroll {
        width: 100%;
        height: 1fr;
        overflow-x: hidden;
        overflow-y: auto;
        padding-right: 2;
    }

    #recipe-content {
        width: 100%;
        margin-bottom: 1;
    }

    .field-label {
        color: $text;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }

    #additional_instructions {
        width: 100%;
        height: 5;
        max-height: 6;
        margin-top: 1;
        margin-bottom: 1;
    }

    #btn_generate_treatment {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
    }
    """

    def watch_profile(self, profile: Optional[TeamProfile]) -> None:
        self.update_content()

    def watch_draw(self, draw: Optional[FridayDraw]) -> None:
        self.update_content()

    def watch_is_generating(self, is_generating: bool) -> None:
        try:
            btn = self.query_one("#btn_generate_treatment", Button)
            btn.disabled = is_generating
            if is_generating:
                btn.label = "⏳ Generating Treatment..."
            else:
                btn.label = "⚡ Generate Treatment [G]"
        except Exception:
            pass

    def on_mount(self) -> None:
        self.update_content()

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="recipe-scroll"):
            yield Static(id="recipe-content")
            yield Label("📝 [bold yellow]ADDITIONAL FILMMAKER DIRECTIVES[/bold yellow]", classes="field-label")
            yield TextArea(
                placeholder="Optional custom instructions for this generation run...",
                id="additional_instructions",
            )
        yield Button(
            "⚡ Generate Treatment [G]",
            id="btn_generate_treatment",
            variant="success",
        )

    def update_content(self) -> None:
        try:
            content_widget = self.query_one("#recipe-content", Static)
        except Exception:
            return

        lines = ["📜 [bold cyan]PROMPT RECIPE SUMMARY[/bold cyan]\n"]

        # Team & Constraints
        lines.append("👤 [bold white]TEAM & CONSTRAINTS[/bold white]")
        if self.profile:
            lines.append(f"• Team: [green]{self.profile.team_name}[/green]")
            lines.append(f"• Location: [yellow]{self.profile.location}[/yellow]")
            log_c = self.profile.active_logistical_constraint or "None"
            dir_v = self.profile.active_directorial_vision or "None"
            them_f = self.profile.active_thematic_framework or "None"
            idea_s = self.profile.active_idea_seed or "None"
            lines.append(f"• Logistics: [cyan]{log_c}[/cyan]")
            lines.append(f"• Directorial: [magenta]{dir_v}[/magenta]")
            lines.append(f"• Thematic: [blue]{them_f}[/blue]")
            lines.append(f"• Idea Seed: [yellow]{idea_s}[/yellow]")
        else:
            lines.append("• [dim]Team Profile: Unconfigured[/dim]")

        lines.append("")

        # Friday Draw
        if self.draw:
            lines.append("🎲 [bold green]ACTIVE FRIDAY DRAW[/bold green]")
            lines.append(f"• Genre 1: [cyan]{self.draw.genre_1}[/cyan]")
            lines.append(f"• Genre 2: [cyan]{self.draw.genre_2}[/cyan]")
            lines.append(
                f"• Character: [yellow]{self.draw.character_name}[/yellow] "
                f"([dim]{self.draw.character_trait}[/dim])"
            )
            lines.append(f"• Required Prop: [magenta]{self.draw.required_prop}[/magenta]")
            lines.append(f"• Required Line: [italic green]\"{self.draw.required_line}\"[/italic green]")
        else:
            lines.append("🎲 [bold red]NO DRAW RECORDED[/bold red]")
            lines.append("[dim]Run `48hfp draw` or click 'Open Draw Wizard' [D] to record draw data.[/dim]")

        content_widget.update("\n".join(lines))
        content_widget.refresh()


class OutputPane(Static):
    """Right Split Pane displaying the generated Markdown treatment or loading indicator."""

    markdown_text: reactive[str] = reactive(DEFAULT_WELCOME_MARKDOWN)
    is_generating: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    OutputPane {
        width: 2fr;
        height: 100%;
        background: $background;
        color: $text;
        padding: 1 2;
    }

    #output-scroll {
        height: 100%;
    }

    #treatment-loading {
        height: 3;
        margin-top: 4;
        content-align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="output-scroll"):
            yield LoadingIndicator(id="treatment-loading")
            yield Markdown(self.markdown_text, id="treatment-markdown")

    def on_mount(self) -> None:
        self.apply_generating_state()

    def watch_markdown_text(self, new_text: str) -> None:
        try:
            md_widget = self.query_one("#treatment-markdown", Markdown)
            md_widget.update(new_text)
        except Exception:
            pass

    def watch_is_generating(self, is_gen: bool) -> None:
        self.apply_generating_state()

    def apply_generating_state(self) -> None:
        try:
            loader = self.query_one("#treatment-loading", LoadingIndicator)
            md_widget = self.query_one("#treatment-markdown", Markdown)
            if self.is_generating:
                loader.display = True
                md_widget.display = False
            else:
                loader.display = False
                md_widget.display = True
        except Exception:
            pass


class StudioWorkspace(Static):
    """Split-Pane Container workspace widget housing RecipePane and OutputPane."""

    profile: reactive[Optional[TeamProfile]] = reactive(None)
    draw: reactive[Optional[FridayDraw]] = reactive(None)
    markdown_text: reactive[str] = reactive(DEFAULT_WELCOME_MARKDOWN)
    is_generating: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    StudioWorkspace {
        width: 1fr;
        height: 100%;
        background: $background;
    }

    #split-workspace {
        width: 100%;
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="split-workspace"):
            yield RecipePane(id="recipe-pane")
            yield OutputPane(id="output-pane")

    def watch_profile(self, profile: Optional[TeamProfile]) -> None:
        try:
            self.query_one(RecipePane).profile = profile
        except Exception:
            pass

    def watch_draw(self, draw: Optional[FridayDraw]) -> None:
        try:
            self.query_one(RecipePane).draw = draw
        except Exception:
            pass

    def watch_markdown_text(self, markdown_text: str) -> None:
        try:
            self.query_one(OutputPane).markdown_text = markdown_text
        except Exception:
            pass

    def watch_is_generating(self, is_generating: bool) -> None:
        try:
            self.query_one(RecipePane).is_generating = is_generating
            self.query_one(OutputPane).is_generating = is_generating
        except Exception:
            pass

    def update_content(self) -> None:
        """Trigger update_content on child RecipePane for backward compatibility."""
        try:
            self.query_one(RecipePane).update_content()
        except Exception:
            pass
