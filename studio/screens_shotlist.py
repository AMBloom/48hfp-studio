"""TUI ShotList Workspace view and StudioBinder DataTable visualizer for 48HFP-Studio."""

from typing import Any, Dict, List, Union
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, DataTable, Label, Static

from studio.models.shotlist import ShotItem, ShotListBase


class ShotListWorkspace(Static):
    """TUI ShotList Workspace view featuring a StudioBinder-style DataTable and Toolbar navigation."""

    shotlist_data: reactive[Union[ShotListBase, List[Dict[str, Any]], List[ShotItem], None]] = reactive(None)
    is_generating_storyboards: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    ShotListWorkspace {
        width: 1fr;
        height: 100%;
        background: $background;
        layout: vertical;
        padding: 1;
    }

    #shotlist-toolbar {
        height: 3;
        width: 100%;
        background: $surface;
        border-bottom: solid $accent;
        padding: 0 1;
        align: center middle;
    }

    #shotlist-toolbar Button {
        margin: 0 1;
    }

    #shotlist-title {
        color: $accent;
        text-style: bold;
        padding: 0 2;
        content-align: center middle;
    }

    #table-container {
        width: 100%;
        height: 1fr;
        padding-top: 1;
    }

    DataTable {
        width: 100%;
        height: 1fr;
        background: $surface-darken-1;
        color: $text;
        border: heavy $accent;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="shotlist-toolbar"):
            yield Button("← Back to Screenplay", id="btn_back_to_screenplay", variant="default")
            yield Label("🎥 StudioBinder Shot List", id="shotlist-title")
            yield Button("🖼️ Generate Storyboards", id="btn_generate_storyboards", variant="primary")

        with Vertical(id="table-container"):
            yield DataTable(id="table-shotlist")

    def watch_is_generating_storyboards(self, is_gen: bool) -> None:
        try:
            btn = self.query_one("#btn_generate_storyboards", Button)
            btn.disabled = is_gen
            btn.label = "⏳ Generating..." if is_gen else "🖼️ Generate Storyboards"
        except Exception:
            pass

    def on_mount(self) -> None:
        table = self.query_one("#table-shotlist", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns(
            "Shot",
            "Scene",
            "Location",
            "Setup",
            "Shot Size",
            "Camera Movement",
            "Cast",
            "Description",
        )
        self.update_table()

    def watch_shotlist_data(self, new_data: Any) -> None:
        self.update_table()

    def update_table(self) -> None:
        try:
            table = self.query_one("#table-shotlist", DataTable)
        except Exception:
            return

        table.clear()

        if not self.shotlist_data:
            return

        items: List[Dict[str, Any]] = []

        if isinstance(self.shotlist_data, ShotListBase):
            title_lbl = self.query_one("#shotlist-title", Label)
            title_lbl.update(f"🎥 Shot List: {self.shotlist_data.title}")
            for item in self.shotlist_data.shots:
                cast_str = ", ".join(item.cast) if isinstance(item.cast, list) else str(item.cast or "")
                items.append({
                    "Shot": str(item.shot_number),
                    "Scene": str(item.scene_number),
                    "Location": item.location,
                    "Setup": item.setup,
                    "Shot Size": item.shot_size,
                    "Camera Movement": item.camera_movement,
                    "Cast": cast_str,
                    "Description": item.description,
                })
        elif isinstance(self.shotlist_data, list):
            for row in self.shotlist_data:
                if isinstance(row, ShotItem):
                    cast_str = ", ".join(row.cast) if isinstance(row.cast, list) else str(row.cast or "")
                    items.append({
                        "Shot": str(row.shot_number),
                        "Scene": str(row.scene_number),
                        "Location": row.location,
                        "Setup": row.setup,
                        "Shot Size": row.shot_size,
                        "Camera Movement": row.camera_movement,
                        "Cast": cast_str,
                        "Description": row.description,
                    })
                elif isinstance(row, dict):
                    cast_raw = row.get("Cast", row.get("cast", ""))
                    cast_str = ", ".join(cast_raw) if isinstance(cast_raw, list) else str(cast_raw or "")
                    items.append({
                        "Shot": str(row.get("Shot", row.get("shot_number", ""))),
                        "Scene": str(row.get("Scene", row.get("scene_number", ""))),
                        "Location": str(row.get("Location", row.get("location", ""))),
                        "Setup": str(row.get("Setup", row.get("setup", ""))),
                        "Shot Size": str(row.get("Shot Size", row.get("shot_size", ""))),
                        "Camera Movement": str(row.get("Camera Movement", row.get("camera_movement", ""))),
                        "Cast": cast_str,
                        "Description": str(row.get("Description", row.get("description", ""))),
                    })

        for row in items:
            table.add_row(
                row["Shot"],
                row["Scene"],
                row["Location"],
                row["Setup"],
                row["Shot Size"],
                row["Camera Movement"],
                row["Cast"],
                row["Description"],
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_back_to_screenplay":
            if hasattr(self.app, "action_switch_to_screenplay_view"):
                self.app.action_switch_to_screenplay_view()
        elif event.button.id == "btn_generate_storyboards":
            if hasattr(self.app, "action_generate_storyboards"):
                self.app.action_generate_storyboards()

