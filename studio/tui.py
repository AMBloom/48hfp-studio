"""Stateful Terminal User Interface (TUI) for 48HFP-Studio using Textual."""

from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Label

from studio.models.profile import TeamProfile
from studio.models.draw import FridayDraw
from studio.utils.profile_store import load_profile
from studio.utils.draw_store import load_draw


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
        width: 32;
        height: 100%;
        background: $surface;
        color: $text;
        border-right: heavy $accent;
        padding: 1 2;
    }
    """

    def watch_profile(self, profile: Optional[TeamProfile]) -> None:
        self.update_content()

    def on_mount(self) -> None:
        self.update_content()

    def update_content(self) -> None:
        if self.profile:
            team_info = f"[bold green]{self.profile.team_name}[/bold green]"
            admin_info = f"Admin: [cyan]{self.profile.admin_username}[/cyan]"
            log_c = self.profile.active_logistical_constraint or "None"
            cre_c = self.profile.active_creative_constraint or "None"
            constraint_info = (
                f"Logistics: [yellow]{log_c}[/yellow]\n"
                f"Creative: [magenta]{cre_c}[/magenta]"
            )
        else:
            team_info = "[dim]Team: Unconfigured[/dim]"
            admin_info = "[dim]Admin: N/A[/dim]"
            constraint_info = "[dim]Constraints: None[/dim]"

        content = (
            "🧭 [bold cyan]NAVIGATION[/bold cyan]\n\n"
            "👤 [bold white]TEAM PROFILE[/bold white]\n"
            f"• {team_info}\n"
            f"• {admin_info}\n"
            f"• {constraint_info}\n\n"
            "📌 [bold white]MENU[/bold white]\n"
            "• [bold white]Dashboard[/bold white]\n"
            "• [dim]Team Profile[/dim]\n"
            "• [dim]Friday Draw[/dim]\n"
            "• [dim]Constraints[/dim]\n"
            "• [dim]Treatment Generator[/dim]"
        )
        self.update(content)


class StudioWorkspace(Static):
    """Main Content Studio Workspace widget."""

    draw: reactive[Optional[FridayDraw]] = reactive(None)
    profile: reactive[Optional[TeamProfile]] = reactive(None)

    DEFAULT_CSS = """
    StudioWorkspace {
        width: 1fr;
        height: 100%;
        background: $background;
        color: $text;
        padding: 2 4;
    }
    """

    def watch_draw(self, draw: Optional[FridayDraw]) -> None:
        self.update_content()

    def watch_profile(self, profile: Optional[TeamProfile]) -> None:
        self.update_content()

    def on_mount(self) -> None:
        self.update_content()

    def update_content(self) -> None:
        if self.draw:
            draw_summary = (
                "🎲 [bold green]ACTIVE FRIDAY DRAW[/bold green]\n"
                f"• [bold white]Genre 1:[/bold white] [cyan]{self.draw.genre_1}[/cyan]\n"
                f"• [bold white]Genre 2:[/bold white] [cyan]{self.draw.genre_2}[/cyan]\n"
                f"• [bold white]Character:[/bold white] [yellow]{self.draw.character_name}[/yellow] "
                f"([dim]{self.draw.character_trait}, {self.draw.character_gender}[/dim])\n"
                f"• [bold white]Required Prop:[/bold white] [magenta]{self.draw.required_prop}[/magenta]\n"
                f"• [bold white]Required Line:[/bold white] [italic green]\"{self.draw.required_line}\"[/italic green]\n"
            )
        else:
            draw_summary = (
                "🎲 [bold red]NO DRAW RECORDED[/bold red]\n"
                "[dim]Run `48hfp draw` or perform kickoff in TUI to record draw data.[/dim]\n"
            )

        header = "🎬 [bold yellow]48HFP-STUDIO WORKSPACE[/bold yellow]\n\n"
        welcome = "[bold white]Welcome to 48HFP-Studio v2.0 TUI Edition[/bold white]\n\n"
        footer = "\n[dim]Press Ctrl+C or Q to exit.[/dim]"

        self.update(f"{header}{welcome}{draw_summary}{footer}")


class StudioApp(App):
    """Main Textual TUI Application for 48HFP-Studio."""

    TITLE = "48HFP-Studio v2.0"

    app_profile: reactive[Optional[TeamProfile]] = reactive(None)
    app_draw: reactive[Optional[FridayDraw]] = reactive(None)

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


if __name__ == "__main__":
    app = StudioApp()
    app.run()

