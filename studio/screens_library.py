"""Modal screen for managing and selecting Logistical and Creative Constraint Sets."""

from typing import Optional, Tuple
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, Static

from studio.models.profile import TeamProfile
from studio.screens_constraints import (
    CreativeConstraintScreen,
    LogisticalConstraintScreen,
)
from studio.utils.constraint_store import (
    delete_creative_constraint,
    delete_logistical_constraint,
    list_creative_constraints,
    list_logistical_constraints,
    load_creative_constraint,
    load_logistical_constraint,
    seed_default_constraints,
)
from studio.utils.profile_store import save_profile


class ConstraintLibraryScreen(ModalScreen[Optional[TeamProfile]]):
    """Interactive Modal Screen for managing constraint sets and assigning active profile sets."""

    DEFAULT_CSS = """
    ConstraintLibraryScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #library-dialog {
        padding: 1 2;
        width: 100;
        height: 85%;
        background: $surface;
        border: thick $accent;
    }

    #tables-container {
        height: 1fr;
        layout: horizontal;
        margin-top: 1;
        margin-bottom: 1;
    }

    .table-box {
        width: 1fr;
        height: 100%;
        margin-right: 1;
    }

    .table-box-right {
        width: 1fr;
        height: 100%;
        margin-left: 1;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    DataTable {
        height: 1fr;
        border: solid $accent-darken-2;
    }

    #library-action-bar {
        height: 3;
        align: right middle;
    }

    #library-action-bar Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Close Library"),
    ]

    def __init__(self, current_profile: Optional[TeamProfile] = None) -> None:
        super().__init__()
        self.current_profile = current_profile
        self.last_focused_section: str = "logistical"

    def compose(self) -> ComposeResult:
        with Container(id="library-dialog"):
            yield Label(
                "📚 [bold cyan]CONSTRAINT SETS LIBRARY[/bold cyan]", classes="title"
            )
            yield Static(
                "[dim]Manage logistical shoot setups and creative directorial guidelines. Select a set and click 'Set Active'.[/dim]"
            )

            with Horizontal(id="tables-container"):
                with Vertical(classes="table-box"):
                    yield Label("📋 Logistical Constraint Sets", classes="section-title")
                    yield DataTable(id="logistical_table", cursor_type="row")

                with Vertical(classes="table-box-right"):
                    yield Label("🎨 Creative Constraint Sets", classes="section-title")
                    yield DataTable(id="creative_table", cursor_type="row")

            with Horizontal(id="library-action-bar"):
                yield Button("New Logistical", variant="default", id="btn_new_logistical")
                yield Button("New Creative", variant="default", id="btn_new_creative")
                yield Button("Edit Selected", variant="default", id="btn_edit_selected")
                yield Button("Delete Selected", variant="error", id="btn_delete_selected")
                yield Button("Set Active", variant="primary", id="btn_set_active")
                yield Button("Close", variant="default", id="btn_close_library")

    def on_mount(self) -> None:
        """Seed defaults if needed and populate tables on mount."""
        seed_default_constraints()

        log_table = self.query_one("#logistical_table", DataTable)
        log_table.add_columns("Name", "Locations", "Status")

        cre_table = self.query_one("#creative_table", DataTable)
        cre_table.add_columns("Name", "Core Philosophy", "Status")

        self.refresh_tables()

    def refresh_tables(self) -> None:
        """Fetch constraint sets from store and refresh DataTable rows."""
        log_table = self.query_one("#logistical_table", DataTable)
        cre_table = self.query_one("#creative_table", DataTable)

        log_table.clear()
        cre_table.clear()

        active_log = (
            self.current_profile.active_logistical_constraint
            if self.current_profile
            else None
        )
        active_cre = (
            self.current_profile.active_creative_constraint
            if self.current_profile
            else None
        )

        for c in list_logistical_constraints():
            is_active = active_log and c.name == active_log
            status = "✅ ACTIVE" if is_active else ""
            locs = ", ".join(c.locations[:2]) if c.locations else "N/A"
            log_table.add_row(c.name, locs, status, key=c.name)

        for c in list_creative_constraints():
            is_active = active_cre and c.name == active_cre
            status = "✅ ACTIVE" if is_active else ""
            phil = (
                c.core_philosophy[:25] + "..."
                if len(c.core_philosophy) > 25
                else c.core_philosophy or "N/A"
            )
            cre_table.add_row(c.name, phil, status, key=c.name)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Track which table was last focused/highlighted by user."""
        if event.data_table.has_focus:
            if event.data_table.id == "logistical_table":
                self.last_focused_section = "logistical"
            elif event.data_table.id == "creative_table":
                self.last_focused_section = "creative"

    def on_focus(self, event) -> None:
        """Track when a table or section receives focus."""
        widget_id = getattr(event.widget, "id", None)
        if widget_id == "logistical_table":
            self.last_focused_section = "logistical"
        elif widget_id == "creative_table":
            self.last_focused_section = "creative"

    def _get_selected_constraint(self) -> Tuple[str, Optional[str]]:
        """Return (category, name) of currently selected item in active table."""
        log_table = self.query_one("#logistical_table", DataTable)
        cre_table = self.query_one("#creative_table", DataTable)

        # Check explicit focus first
        if log_table.has_focus:
            section = "logistical"
            table = log_table
        elif cre_table.has_focus:
            section = "creative"
            table = cre_table
        else:
            section = self.last_focused_section
            table = log_table if section == "logistical" else cre_table

        if table.row_count == 0:
            return section, None

        cursor_row = table.cursor_row if table.cursor_row is not None else 0

        try:
            cell_val = str(table.get_cell_at((cursor_row, 0)))
            return section, cell_val
        except Exception:
            return section, None

    def action_cancel(self) -> None:
        self.dismiss(self.current_profile)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn_close_library":
            self.action_cancel()
        elif btn_id == "btn_new_logistical":
            self.action_new_logistical()
        elif btn_id == "btn_new_creative":
            self.action_new_creative()
        elif btn_id == "btn_edit_selected":
            self.action_edit_selected()
        elif btn_id == "btn_delete_selected":
            self.action_delete_selected()
        elif btn_id == "btn_set_active":
            self.action_set_active()

    def action_new_logistical(self) -> None:
        def on_saved(result):
            self.refresh_tables()

        self.app.push_screen(LogisticalConstraintScreen(), callback=on_saved)

    def action_new_creative(self) -> None:
        def on_saved(result):
            self.refresh_tables()

        self.app.push_screen(CreativeConstraintScreen(), callback=on_saved)

    def action_edit_selected(self) -> None:
        category, name = self._get_selected_constraint()
        if not name:
            self.notify("No constraint set selected.", severity="warning")
            return

        def on_saved(result):
            self.refresh_tables()

        if category == "logistical":
            c_log = load_logistical_constraint(name)
            if c_log:
                self.app.push_screen(
                    LogisticalConstraintScreen(c_log), callback=on_saved
                )
        else:
            c_cre = load_creative_constraint(name)
            if c_cre:
                self.app.push_screen(
                    CreativeConstraintScreen(c_cre), callback=on_saved
                )

    def action_delete_selected(self) -> None:
        category, name = self._get_selected_constraint()
        if not name:
            self.notify("No constraint set selected for deletion.", severity="warning")
            return

        if category == "logistical":
            deleted = delete_logistical_constraint(name)
            if deleted and self.current_profile and self.current_profile.active_logistical_constraint == name:
                self.current_profile.active_logistical_constraint = None
                save_profile(self.current_profile)
        else:
            deleted = delete_creative_constraint(name)
            if deleted and self.current_profile and self.current_profile.active_creative_constraint == name:
                self.current_profile.active_creative_constraint = None
                save_profile(self.current_profile)

        if deleted:
            self.notify(f"Deleted '{name}' constraint set.", severity="information")
            self.refresh_tables()
        else:
            self.notify(f"Failed to delete '{name}'.", severity="error")

    def action_set_active(self) -> None:
        category, name = self._get_selected_constraint()
        if not name:
            self.notify("No constraint set selected.", severity="warning")
            return

        if not self.current_profile:
            self.notify("No profile active. Please setup profile first.", severity="error")
            return

        if category == "logistical":
            self.current_profile.active_logistical_constraint = name
        else:
            self.current_profile.active_creative_constraint = name

        save_profile(self.current_profile)
        self.refresh_tables()
        self.notify(
            f"Set active {category} constraint to '{name}'.",
            title="Constraint Activated",
            severity="information",
        )
