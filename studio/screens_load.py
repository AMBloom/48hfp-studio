"""Modal Screen for browsing and loading saved Treatments and Screenplays."""

from pathlib import Path
from typing import Dict, List, Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, TabbedContent, TabPane

from studio.utils.screenplay_store import list_saved_screenplays, list_saved_treatments


class LoadDraftsScreen(ModalScreen[Optional[Dict[str, str]]]):
    """Modal screen displaying saved treatments and screenplays for selection and loading."""

    DEFAULT_CSS = """
    LoadDraftsScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #load-dialog {
        padding: 1 2;
        width: 90%;
        max-width: 95;
        height: 80%;
        max-height: 35;
        background: $surface;
        border: thick $accent;
    }

    .title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    #draft-tabs {
        height: 1fr;
    }

    DataTable {
        height: 1fr;
        width: 100%;
    }

    #button-bar {
        margin-top: 1;
        height: 3;
        align: right middle;
    }

    #button-bar Button {
        margin-left: 2;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="load-dialog"):
            yield Label("📂 [bold cyan]LOAD SAVED DRAFTS[/bold cyan]", classes="title")

            with TabbedContent(id="draft-tabs"):
                with TabPane("📜 Treatments", id="tab-treatments"):
                    yield DataTable(id="table-treatments")
                with TabPane("🎬 Screenplays", id="tab-screenplays"):
                    yield DataTable(id="table-screenplays")

            with Horizontal(id="button-bar"):
                yield Button("Load Draft", variant="primary", id="btn_load_draft")
                yield Button("Cancel", variant="default", id="btn_cancel_load")

    def on_mount(self) -> None:
        table_tx = self.query_one("#table-treatments", DataTable)
        table_tx.cursor_type = "row"
        table_tx.add_columns("Ver", "Title", "Date Modified", "Filename")

        treatments = list_saved_treatments()
        for t in treatments:
            table_tx.add_row(
                t["version"],
                t["title"],
                t["formatted_date"],
                t["filename"],
                key=t["path"],
            )

        table_sc = self.query_one("#table-screenplays", DataTable)
        table_sc.cursor_type = "row"
        table_sc.add_columns("Ver", "Title", "Date Modified", "Filename")

        screenplays = list_saved_screenplays()
        for s in screenplays:
            table_sc.add_row(
                s["version"],
                s["title"],
                s["formatted_date"],
                s["filename"],
                key=s["path"],
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_load_draft":
            self.action_submit_load()
        elif event.button.id == "btn_cancel_load":
            self.action_cancel()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_submit_load(self) -> None:
        tabs = self.query_one("#draft-tabs", TabbedContent)
        active_tab = tabs.active

        if active_tab == "tab-treatments":
            table = self.query_one("#table-treatments", DataTable)
            draft_type = "treatment"
        else:
            table = self.query_one("#table-screenplays", DataTable)
            draft_type = "screenplay"

        if table.cursor_row < 0 or table.row_count == 0:
            self.notify("Please select a draft row to load.", severity="warning")
            return

        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            file_path = Path(str(row_key.value))

            if not file_path.exists():
                self.notify(f"File not found: {file_path}", severity="error")
                return

            content = file_path.read_text(encoding="utf-8")
            self.dismiss({
                "type": draft_type,
                "path": str(file_path),
                "content": content,
                "title": file_path.stem,
            })
        except Exception as err:
            self.notify(f"Failed to load draft: {err}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Double clicking or pressing Enter on a row directly loads the draft."""
        self.action_submit_load()
