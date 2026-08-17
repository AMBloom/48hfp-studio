"""TUI Storyboards Workspace view and Pre-Vis Gallery visualizer for 48HFP-Studio."""

from pathlib import Path
from typing import List
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Label, Static


class StoryboardsWorkspace(Static):
    """TUI Storyboards Workspace view featuring a Pre-Vis Gallery and Toolbar navigation."""

    storyboards_data: reactive[List[str]] = reactive([])
    is_generating: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    StoryboardsWorkspace {
        width: 1fr;
        height: 100%;
        background: $background;
        layout: vertical;
        padding: 1;
    }

    #storyboard-toolbar {
        height: 3;
        width: 100%;
        background: $surface;
        border-bottom: solid $accent;
        padding: 0 1;
        align: center middle;
    }

    #storyboard-toolbar Button {
        margin: 0 1;
    }

    #storyboard-title {
        color: $accent;
        text-style: bold;
        padding: 0 2;
        content-align: center middle;
    }

    #storyboard-empty-container {
        width: 100%;
        height: 1fr;
        align: center middle;
        padding: 4;
        background: $surface-darken-1;
        border: heavy $accent;
    }

    #storyboard-empty-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        content-align: center middle;
    }

    #storyboard-empty-desc {
        color: $text-muted;
        margin-bottom: 2;
        content-align: center middle;
        text-align: center;
    }

    #btn_empty_generate_storyboards {
        min-width: 40;
    }

    #storyboard-gallery-scroll {
        width: 100%;
        height: 1fr;
        padding: 1;
    }

    .storyboard-card {
        width: 100%;
        height: auto;
        background: $surface;
        border: solid $accent;
        padding: 1 2;
        margin-bottom: 1;
    }

    .storyboard-card-header {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .storyboard-card-path {
        color: $text-muted;
        text-style: italic;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="storyboard-toolbar"):
            yield Button("← Back to Shot List [3]", id="btn_back_to_shotlist", variant="default")
            yield Label("🖼️ Pre-Vis Storyboard Gallery", id="storyboard-title")
            yield Button("🔄 Re-Generate Storyboards", id="btn_regen_storyboards", variant="primary")

        with Vertical(id="storyboard-empty-container"):
            yield Label("🖼️ [bold cyan]No Storyboards Generated Yet[/bold cyan]", id="storyboard-empty-title")
            yield Label(
                "Generate 16:9 monochrome pre-vis storyboard sketches for each shot in your active shot list.",
                id="storyboard-empty-desc",
            )
            yield Button(
                "🖼️ Generate Storyboards from Active Shot List",
                id="btn_empty_generate_storyboards",
                variant="success",
            )

        with VerticalScroll(id="storyboard-gallery-scroll"):
            yield Container(id="gallery-cards-container")

    def on_mount(self) -> None:
        self.apply_view_state()
        self.update_gallery()

    def watch_storyboards_data(self, paths: List[str]) -> None:
        self.apply_view_state()
        self.update_gallery()

    def watch_is_generating(self, is_gen: bool) -> None:
        try:
            btn_toolbar = self.query_one("#btn_regen_storyboards", Button)
            btn_empty = self.query_one("#btn_empty_generate_storyboards", Button)
            if is_gen:
                btn_toolbar.label = "⏳ Generating..."
                btn_toolbar.disabled = True
                btn_empty.label = "⏳ Generating Storyboards..."
                btn_empty.disabled = True
            else:
                btn_toolbar.label = "🔄 Re-Generate Storyboards"
                btn_toolbar.disabled = False
                btn_empty.label = "🖼️ Generate Storyboards from Active Shot List"
                btn_empty.disabled = False
        except Exception:
            pass

    def apply_view_state(self) -> None:
        try:
            toolbar = self.query_one("#storyboard-toolbar", Horizontal)
            empty_box = self.query_one("#storyboard-empty-container", Vertical)
            gallery = self.query_one("#storyboard-gallery-scroll", VerticalScroll)

            toolbar.display = True
            if not self.storyboards_data:
                empty_box.display = True
                gallery.display = False
            else:
                empty_box.display = False
                gallery.display = True
        except Exception:
            pass

    def update_gallery(self) -> None:
        try:
            container = self.query_one("#gallery-cards-container", Container)
        except Exception:
            return

        container.remove_children()
        if not self.storyboards_data:
            return

        for idx, img_path_str in enumerate(self.storyboards_data, start=1):
            p = Path(img_path_str)
            card = Container(classes="storyboard-card")
            card.mount(
                Label(f"🎬 Shot #{idx:03d} Pre-Vis Sketch", classes="storyboard-card-header"),
                Label(f"File: {p.name}", classes="storyboard-card-path"),
                Label(f"Location: {p.parent}", classes="storyboard-card-path"),
            )
            container.mount(card)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_back_to_shotlist":
            if hasattr(self.app, "action_switch_to_shotlist_view"):
                self.app.action_switch_to_shotlist_view()
        elif event.button.id in ("btn_regen_storyboards", "btn_empty_generate_storyboards"):
            if hasattr(self.app, "action_generate_storyboards"):
                self.app.action_generate_storyboards()
