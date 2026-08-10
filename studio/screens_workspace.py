"""Modal screen for native TUI Workspace Manager with directory browser."""

from pathlib import Path
from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Input, Label

from studio.utils.constraint_store import seed_default_constraints
from studio.utils.global_state import get_active_workspace, set_active_workspace


class WorkspaceManagerScreen(ModalScreen[Optional[Path]]):
    """Interactive Modal Screen for selecting, browsing, and initializing project workspaces."""

    DEFAULT_CSS = """
    WorkspaceManagerScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #workspace-dialog {
        padding: 1 2;
        width: 85%;
        max-width: 80;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $accent;
    }

    .title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .field-label {
        color: $text;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }

    #tree-container {
        height: 12;
        border: solid $accent-darken-2;
        margin-bottom: 1;
    }

    #dir_tree {
        width: 100%;
        height: 100%;
    }

    #workspace_path_input {
        margin-bottom: 1;
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
        active_ws = get_active_workspace()
        active_str = str(active_ws) if active_ws else "Unset (CWD)"

        with Container(id="workspace-dialog"):
            yield Label("📂 [bold cyan]WORKSPACE MANAGER[/bold cyan]", classes="title")
            yield Label(f"Current Active Workspace: [bold yellow]{active_str}[/bold yellow]\n", classes="field-label")

            yield Label("📁 Browse Working Directory Folders:", classes="field-label")
            with Container(id="tree-container"):
                yield DirectoryTree(Path.cwd(), id="dir_tree")

            yield Label("Selected / Custom Workspace Directory Path:", classes="field-label")
            yield Input(
                value=str(active_ws or Path.cwd()),
                placeholder="Enter or select folder path...",
                id="workspace_path_input",
            )

            with Horizontal(id="button-bar"):
                yield Button("Set / Init Workspace", variant="primary", id="btn_set_workspace")
                yield Button("Cancel", variant="default", id="btn_cancel_workspace")

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Update the input path when a directory is clicked/selected in the DirectoryTree."""
        self.query_one("#workspace_path_input", Input).value = str(event.path)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Update the input path to parent directory when a file is selected in the DirectoryTree."""
        self.query_one("#workspace_path_input", Input).value = str(event.path.parent)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Submit the workspace path when Enter is pressed in the Input field."""
        if event.input.id == "workspace_path_input":
            self.action_submit_workspace()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle modal action buttons."""
        if event.button.id == "btn_set_workspace":
            self.action_submit_workspace()
        elif event.button.id == "btn_cancel_workspace":
            self.action_cancel()

    def action_cancel(self) -> None:
        """Dismiss modal without changing workspace."""
        self.dismiss(None)

    def action_submit_workspace(self) -> None:
        """Resolve workspace path, create dir if missing, set active, seed constraints, and dismiss."""
        raw_val = self.query_one("#workspace_path_input", Input).value.strip()
        if not raw_val:
            raw_val = str(Path.cwd())

        target_path = Path(raw_val).expanduser().resolve()

        try:
            target_path.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            self.notify(f"Could not create directory '{target_path}': {err}", severity="error")
            return

        set_active_workspace(target_path)
        seed_default_constraints()

        self.notify(f"Active workspace set to: {target_path}", title="Workspace Updated", severity="information")
        self.dismiss(target_path)
