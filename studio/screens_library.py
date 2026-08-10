"""Modal screen for managing and selecting tri-split constraint sets."""

from typing import Optional, Tuple
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, Static, TabbedContent, TabPane

from studio.models.profile import TeamProfile
from studio.screens_constraints import (
    DirectorialVisionScreen,
    IdeaSeedScreen,
    LogisticalConstraintScreen,
    ThematicFrameworkScreen,
)
from studio.utils.constraint_store import (
    delete_directorial_vision,
    delete_idea_seed,
    delete_logistical_constraint,
    delete_thematic_framework,
    list_directorial_visions,
    list_idea_seeds,
    list_logistical_constraints,
    list_thematic_frameworks,
    load_directorial_vision,
    load_idea_seed,
    load_logistical_constraint,
    load_thematic_framework,
    seed_default_constraints,
)
from studio.utils.profile_store import save_profile


class ConstraintLibraryScreen(ModalScreen[Optional[TeamProfile]]):
    """Interactive Modal Screen for managing constraint sets across tabbed categories."""

    DEFAULT_CSS = """
    ConstraintLibraryScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #library-dialog {
        padding: 1 2;
        width: 95vw;
        max-width: 140;
        height: 90vh;
        layout: vertical;
        background: $surface;
        border: thick $accent;
    }

    TabbedContent {
        height: 1fr;
        margin-top: 1;
        margin-bottom: 3;
    }

    TabPane {
        padding: 1;
    }

    DataTable {
        height: 1fr;
        border: solid $accent-darken-2;
    }

    #library-action-bar {
        height: 3;
        dock: bottom;
        margin-bottom: 1;
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

    def compose(self) -> ComposeResult:
        with Container(id="library-dialog"):
            yield Label(
                "📚 [bold cyan]CONSTRAINT SETS LIBRARY[/bold cyan]", classes="title"
            )
            yield Static(
                "[dim]Manage logistical, directorial, thematic, and idea constraints. Select a set and click 'Set Active'.[/dim]"
            )

            with TabbedContent(id="library_tabs"):
                with TabPane("📋 Logistical", id="tab_logistical"):
                    yield DataTable(id="logistical_table", cursor_type="row")
                with TabPane("🎬 Directorial Vision", id="tab_directorial"):
                    yield DataTable(id="directorial_table", cursor_type="row")
                with TabPane("🧠 Thematic Framework", id="tab_thematic"):
                    yield DataTable(id="thematic_table", cursor_type="row")
                with TabPane("💡 Idea Seeds", id="tab_ideas"):
                    yield DataTable(id="ideas_table", cursor_type="row")

            with Horizontal(id="library-action-bar"):
                yield Button("New", variant="default", id="btn_new")
                yield Button("Edit Selected", variant="default", id="btn_edit_selected")
                yield Button("Delete Selected", variant="error", id="btn_delete_selected")
                yield Button("Set Active", variant="primary", id="btn_set_active")
                yield Button("Close", variant="default", id="btn_close_library")

    def on_mount(self) -> None:
        """Seed defaults if needed and populate tables on mount."""
        seed_default_constraints()

        log_table = self.query_one("#logistical_table", DataTable)
        log_table.add_columns("Name", "Locations", "Status")

        dir_table = self.query_one("#directorial_table", DataTable)
        dir_table.add_columns("Name", "Visual Economy", "Status")

        them_table = self.query_one("#thematic_table", DataTable)
        them_table.add_columns("Name", "Core Philosophy", "Status")

        idea_table = self.query_one("#ideas_table", DataTable)
        idea_table.add_columns("Name", "Inciting Incident", "Status")

        self.refresh_tables()

    def refresh_tables(self) -> None:
        """Fetch constraint sets from store and refresh DataTable rows across all tabs."""
        log_table = self.query_one("#logistical_table", DataTable)
        dir_table = self.query_one("#directorial_table", DataTable)
        them_table = self.query_one("#thematic_table", DataTable)
        idea_table = self.query_one("#ideas_table", DataTable)

        def get_current_key(table: DataTable) -> Optional[str]:
            if table.row_count > 0 and table.cursor_row is not None:
                try:
                    return str(table.get_cell_at((table.cursor_row, 0)))
                except Exception:
                    pass
            return None

        log_key = get_current_key(log_table)
        dir_key = get_current_key(dir_table)
        them_key = get_current_key(them_table)
        idea_key = get_current_key(idea_table)

        log_table.clear()
        dir_table.clear()
        them_table.clear()
        idea_table.clear()

        prof = self.current_profile
        active_log = prof.active_logistical_constraint if prof else None
        active_dir = prof.active_directorial_vision if prof else None
        active_them = prof.active_thematic_framework if prof else None
        active_idea = prof.active_idea_seed if prof else None

        for c in list_logistical_constraints():
            status = "✅ ACTIVE" if active_log and c.name == active_log else ""
            locs = ", ".join(c.locations[:2]) if c.locations else "N/A"
            log_table.add_row(c.name, locs, status, key=c.name)

        for c in list_directorial_visions():
            status = "✅ ACTIVE" if active_dir and c.name == active_dir else ""
            vis = c.visual_economy[:30] + "..." if len(c.visual_economy) > 30 else c.visual_economy or "N/A"
            dir_table.add_row(c.name, vis, status, key=c.name)

        for c in list_thematic_frameworks():
            status = "✅ ACTIVE" if active_them and c.name == active_them else ""
            phil = c.core_philosophy[:30] + "..." if len(c.core_philosophy) > 30 else c.core_philosophy or "N/A"
            them_table.add_row(c.name, phil, status, key=c.name)

        for c in list_idea_seeds():
            status = "✅ ACTIVE" if active_idea and c.name == active_idea else ""
            inc = c.inciting_incident[:30] + "..." if len(c.inciting_incident) > 30 else c.inciting_incident or "N/A"
            idea_table.add_row(c.name, inc, status, key=c.name)

        def restore_cursor(table: DataTable, key: Optional[str]) -> None:
            if key and table.row_count > 0:
                try:
                    row_idx = table.get_row_index(key)
                    table.move_cursor(row=row_idx)
                except Exception:
                    pass

        restore_cursor(log_table, log_key)
        restore_cursor(dir_table, dir_key)
        restore_cursor(them_table, them_key)
        restore_cursor(idea_table, idea_key)

    def _get_active_category(self) -> str:
        """Return the category string corresponding to the currently active TabPane."""
        try:
            tabbed = self.query_one("#library_tabs", TabbedContent)
            active_id = tabbed.active
            if active_id == "tab_directorial":
                return "directorial"
            elif active_id == "tab_thematic":
                return "thematic"
            elif active_id == "tab_ideas":
                return "ideas"
        except Exception:
            pass
        return "logistical"

    def _get_table_for_category(self, category: str) -> DataTable:
        """Return the DataTable corresponding to a given category."""
        if category == "directorial":
            return self.query_one("#directorial_table", DataTable)
        elif category == "thematic":
            return self.query_one("#thematic_table", DataTable)
        elif category == "ideas":
            return self.query_one("#ideas_table", DataTable)
        return self.query_one("#logistical_table", DataTable)

    def _get_selected_constraint(self) -> Tuple[str, Optional[str]]:
        """Return (category, name) of currently selected item in the active tab table."""
        category = self._get_active_category()
        table = self._get_table_for_category(category)

        if table.row_count > 0 and table.cursor_row is not None:
            try:
                cell_val = str(table.get_cell_at((table.cursor_row, 0)))
                if cell_val:
                    return category, cell_val
            except Exception:
                pass

        if table.row_count > 0:
            try:
                return category, str(table.get_cell_at((0, 0)))
            except Exception:
                pass

        return category, None

    def action_cancel(self) -> None:
        self.dismiss(self.current_profile)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn_close_library":
            self.action_cancel()
        elif btn_id in ["btn_new", "btn_new_logistical"]:
            self.action_new()
        elif btn_id == "btn_edit_selected":
            self.action_edit_selected()
        elif btn_id == "btn_delete_selected":
            self.action_delete_selected()
        elif btn_id == "btn_set_active":
            self.action_set_active()

    def action_new(self) -> None:
        category = self._get_active_category()

        def on_saved(result):
            self.refresh_tables()

        if category == "logistical":
            self.app.push_screen(LogisticalConstraintScreen(), callback=on_saved)
        elif category == "directorial":
            self.app.push_screen(DirectorialVisionScreen(), callback=on_saved)
        elif category == "thematic":
            self.app.push_screen(ThematicFrameworkScreen(), callback=on_saved)
        elif category == "ideas":
            self.app.push_screen(IdeaSeedScreen(), callback=on_saved)

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
                self.app.push_screen(LogisticalConstraintScreen(c_log), callback=on_saved)
        elif category == "directorial":
            c_dir = load_directorial_vision(name)
            if c_dir:
                self.app.push_screen(DirectorialVisionScreen(c_dir), callback=on_saved)
        elif category == "thematic":
            c_them = load_thematic_framework(name)
            if c_them:
                self.app.push_screen(ThematicFrameworkScreen(c_them), callback=on_saved)
        elif category == "ideas":
            c_idea = load_idea_seed(name)
            if c_idea:
                self.app.push_screen(IdeaSeedScreen(c_idea), callback=on_saved)

    def action_delete_selected(self) -> None:
        category, name = self._get_selected_constraint()
        if not name:
            self.notify("No constraint set selected for deletion.", severity="warning")
            return

        deleted = False
        prof = self.current_profile

        if category == "logistical":
            deleted = delete_logistical_constraint(name)
            if deleted and prof and prof.active_logistical_constraint == name:
                prof.active_logistical_constraint = None
                save_profile(prof)
        elif category == "directorial":
            deleted = delete_directorial_vision(name)
            if deleted and prof and prof.active_directorial_vision == name:
                prof.active_directorial_vision = None
                save_profile(prof)
        elif category == "thematic":
            deleted = delete_thematic_framework(name)
            if deleted and prof and prof.active_thematic_framework == name:
                prof.active_thematic_framework = None
                save_profile(prof)
        elif category == "ideas":
            deleted = delete_idea_seed(name)
            if deleted and prof and prof.active_idea_seed == name:
                prof.active_idea_seed = None
                save_profile(prof)

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
        elif category == "directorial":
            self.current_profile.active_directorial_vision = name
        elif category == "thematic":
            self.current_profile.active_thematic_framework = name
        elif category == "ideas":
            self.current_profile.active_idea_seed = name

        save_profile(self.current_profile)
        self.refresh_tables()
        self.notify(
            f"Set active {category} constraint to '{name}'.",
            title="Constraint Activated",
            severity="information",
        )

