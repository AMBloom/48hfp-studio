"""Modal screens for in-TUI configuration setup, API settings, and Friday Draw wizard."""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv, set_key
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Select, TextArea

from studio.models.draw import (
    GENRES_GROUP_1,
    GENRES_GROUP_2,
    FridayDraw,
    create_default_draw,
)
from studio.models.profile import TeamProfile
from studio.utils.draw_store import save_draw
from studio.utils.profile_store import save_profile


STANDARD_FILM_ROLES = [
    "Director",
    "Producer",
    "Writer",
    "Cinematographer / DP",
    "Editor",
    "Sound Engineer",
    "Production Designer",
    "Gaffer / Grip",
    "Actor",
    "Production Assistant",
]


class ApiSettingsScreen(ModalScreen[Optional[dict]]):
    """Interactive Modal Screen for API Key and Gemini Model configuration persistence."""

    DEFAULT_CSS = """
    ApiSettingsScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #api-dialog {
        padding: 1 2;
        width: 80%;
        max-width: 70;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $accent;
    }

    .form-field {
        margin-bottom: 1;
    }

    .field-label {
        color: $text;
        text-style: bold;
        margin-bottom: 0;
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

    MODEL_CHOICES = [
        ("gemini-3.6-flash (Default)", "gemini-3.6-flash"),
        ("gemini-3.5-flash", "gemini-3.5-flash"),
        ("gemini-3.0-pro", "gemini-3.0-pro"),
    ]

    def compose(self) -> ComposeResult:
        load_dotenv()
        curr_key = os.environ.get("GEMINI_API_KEY", "")
        curr_model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

        with Container(id="api-dialog"):
            yield Label("⚙️ [bold cyan]API & INFERENCE SETTINGS[/bold cyan]\n", classes="title")
            with VerticalScroll():
                yield Label("Gemini API Key:", classes="field-label")
                yield Input(
                    value=curr_key,
                    placeholder="e.g. AIzaSy...",
                    id="api_key",
                    password=True,
                    classes="form-field",
                )

                yield Label("Gemini Model Family:", classes="field-label")
                yield Select(
                    self.MODEL_CHOICES,
                    value=curr_model if curr_model in [m[1] for m in self.MODEL_CHOICES] else "gemini-3.6-flash",
                    id="gemini_model",
                    classes="form-field",
                )

            with Horizontal(id="button-bar"):
                yield Button("Save Settings", variant="primary", id="save_api_settings_btn")
                yield Button("Cancel", variant="default", id="cancel_api_settings_btn")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_api_settings_btn":
            self.action_save()
        elif event.button.id == "cancel_api_settings_btn":
            self.action_cancel()

    def action_save(self) -> None:
        key_val = self.query_one("#api_key", Input).value.strip()
        model_select = self.query_one("#gemini_model", Select)
        model_val = (
            str(model_select.value)
            if model_select.value != Select.BLANK and model_select.value is not None
            else "gemini-3.6-flash"
        )

        dotenv_path = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(dotenv_path):
            with open(dotenv_path, "w", encoding="utf-8") as f:
                f.write("# 48HFP-Studio Environment Configuration\n")

        set_key(dotenv_path, "GEMINI_API_KEY", key_val)
        set_key(dotenv_path, "GEMINI_MODEL", model_val)

        os.environ["GEMINI_API_KEY"] = key_val
        os.environ["GEMINI_MODEL"] = model_val

        res = {"api_key": key_val, "model": model_val}
        self.notify("API settings persisted to .env", title="Settings Saved", severity="information")
        self.dismiss(res)


class DrawWizardScreen(ModalScreen[Optional[FridayDraw]]):
    """Interactive Modal Screen for entering or editing Friday Draw kickoff data."""

    DEFAULT_CSS = """
    DrawWizardScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #draw-dialog {
        padding: 1 2;
        width: 85%;
        max-width: 70;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $accent;
    }

    .form-field {
        margin-bottom: 1;
    }

    .field-label {
        color: $text;
        text-style: bold;
        margin-bottom: 0;
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

    def __init__(self, current_draw: Optional[FridayDraw] = None) -> None:
        super().__init__()
        self.current_draw = current_draw

    def compose(self) -> ComposeResult:
        with Container(id="draw-dialog"):
            yield Label("🎲 [bold yellow]FRIDAY NIGHT DRAW WIZARD[/bold yellow]\n", classes="title")
            with VerticalScroll():
                yield Label("Primary Genre (Group 1):", classes="field-label")
                g1_options = [(g, g) for g in GENRES_GROUP_1]
                g1_val = (
                    self.current_draw.genre_1
                    if self.current_draw and self.current_draw.genre_1 in GENRES_GROUP_1
                    else None
                )
                if g1_val:
                    yield Select(
                        g1_options,
                        value=g1_val,
                        prompt="Select Primary Genre...",
                        id="genre_1",
                        classes="form-field",
                    )
                else:
                    yield Select(
                        g1_options,
                        prompt="Select Primary Genre...",
                        id="genre_1",
                        classes="form-field",
                    )

                yield Label("Secondary Genre (Group 2):", classes="field-label")
                g2_options = [(g, g) for g in GENRES_GROUP_2]
                g2_val = (
                    self.current_draw.genre_2
                    if self.current_draw and self.current_draw.genre_2 in GENRES_GROUP_2
                    else None
                )
                if g2_val:
                    yield Select(
                        g2_options,
                        value=g2_val,
                        prompt="Select Secondary Genre...",
                        id="genre_2",
                        classes="form-field",
                    )
                else:
                    yield Select(
                        g2_options,
                        prompt="Select Secondary Genre...",
                        id="genre_2",
                        classes="form-field",
                    )

                yield Label("Character Name:", classes="field-label")
                yield Input(
                    value=self.current_draw.character_name if self.current_draw else "",
                    placeholder="e.g. Alex Smith",
                    id="character_name",
                    classes="form-field",
                )

                yield Label("Character Trait / Profession:", classes="field-label")
                yield Input(
                    value=self.current_draw.character_trait if self.current_draw else "",
                    placeholder="e.g. Photographer",
                    id="character_trait",
                    classes="form-field",
                )

                yield Label("Character Gender:", classes="field-label")
                yield Input(
                    value=self.current_draw.character_gender if self.current_draw else "",
                    placeholder="e.g. Female, Male, Any",
                    id="character_gender",
                    classes="form-field",
                )

                yield Label("Required Prop:", classes="field-label")
                yield Input(
                    value=self.current_draw.required_prop if self.current_draw else "",
                    placeholder="e.g. Red umbrella",
                    id="required_prop",
                    classes="form-field",
                )

                yield Label("Required Line of Dialogue:", classes="field-label")
                yield Input(
                    value=self.current_draw.required_line if self.current_draw else "",
                    placeholder="e.g. 'We have to move fast.'",
                    id="required_line",
                    classes="form-field",
                )

            with Horizontal(id="button-bar"):
                yield Button("Save Draw", variant="primary", id="save_draw_btn")
                yield Button("Cancel", variant="default", id="cancel_draw_btn")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_draw_btn":
            self.action_save()
        elif event.button.id == "cancel_draw_btn":
            self.action_cancel()

    def action_save(self) -> None:
        g1_select = self.query_one("#genre_1", Select)
        g2_select = self.query_one("#genre_2", Select)

        g1_val = (
            str(g1_select.value)
            if g1_select.value != Select.BLANK and g1_select.value is not None
            else None
        )
        g2_val = (
            str(g2_select.value)
            if g2_select.value != Select.BLANK and g2_select.value is not None
            else None
        )

        c_name = self.query_one("#character_name", Input).value
        c_trait = self.query_one("#character_trait", Input).value
        c_gender = self.query_one("#character_gender", Input).value
        req_prop = self.query_one("#required_prop", Input).value
        req_line = self.query_one("#required_line", Input).value

        draw = create_default_draw(
            genre_1=g1_val,
            genre_2=g2_val,
            character_name=c_name,
            character_trait=c_trait,
            character_gender=c_gender,
            required_prop=req_prop,
            required_line=req_line,
        )

        save_draw(draw)
        self.dismiss(draw)


class ProfileSetupScreen(ModalScreen[Optional[TeamProfile]]):
    """Interactive Modal Screen for setup or editing of Team Profile with Crew & Cast Roster Builders."""

    DEFAULT_CSS = """
    ProfileSetupScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #profile-dialog {
        padding: 1 2;
        width: 85%;
        max-width: 85;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $accent;
    }

    .form-field {
        margin-bottom: 1;
    }

    .field-label {
        color: $text;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }

    #roster-input-bar, #cast-input-bar-1, #cast-input-bar-2 {
        height: 3;
        margin-bottom: 1;
        layout: horizontal;
    }

    #roster_role {
        width: 35%;
        margin-right: 1;
    }

    #roster_member_name {
        width: 40%;
        margin-right: 1;
    }

    #add_member_btn {
        width: 23%;
    }

    #cast_name, #cast_age {
        width: 49%;
        margin-right: 1;
    }

    #cast_gender {
        width: 32%;
        margin-right: 1;
    }

    #cast_physicality {
        width: 42%;
        margin-right: 1;
    }

    #add_cast_btn {
        width: 23%;
    }

    #roster_table, #cast_table {
        height: 6;
        margin-bottom: 1;
        border: solid $accent-darken-2;
    }

    #roster-action-bar, #cast-action-bar {
        height: 3;
        margin-bottom: 1;
        align: right middle;
    }

    #available_gear {
        height: 4;
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

    def __init__(self, current_profile: Optional[TeamProfile] = None) -> None:
        super().__init__()
        self.current_profile = current_profile
        self.crew: Dict[str, List[str]] = {}
        if current_profile and (current_profile.crew or current_profile.roles):
            source_crew = current_profile.crew or current_profile.roles
            for k, v in source_crew.items():
                self.crew[k] = list(v)

        self.cast: List[Dict[str, str]] = []
        if current_profile and current_profile.cast:
            for item in current_profile.cast:
                self.cast.append(dict(item))

    def compose(self) -> ComposeResult:
        with Container(id="profile-dialog"):
            yield Label("👤 [bold cyan]TEAM PROFILE SETUP[/bold cyan]\n", classes="title")
            with VerticalScroll():
                yield Label("Team Name:", classes="field-label")
                yield Input(
                    value=self.current_profile.team_name if self.current_profile else "",
                    placeholder="e.g. Cyber Directors",
                    id="team_name",
                    classes="form-field",
                )

                yield Label("Admin Username:", classes="field-label")
                yield Input(
                    value=self.current_profile.admin_username if self.current_profile else "",
                    placeholder="e.g. alex_admin",
                    id="admin_username",
                    classes="form-field",
                )

                yield Label("Location:", classes="field-label")
                yield Input(
                    value=self.current_profile.location if self.current_profile else "",
                    placeholder="e.g. San Francisco, CA",
                    id="location",
                    classes="form-field",
                )

                yield Label("🎥 Crew Roster Builder:", classes="field-label")
                with Horizontal(id="roster-input-bar"):
                    role_options = [(r, r) for r in STANDARD_FILM_ROLES]
                    yield Select(role_options, prompt="Select Role...", id="roster_role")
                    yield Input(placeholder="Member Name", id="roster_member_name")
                    yield Button("Add Crew", variant="primary", id="add_member_btn")

                yield DataTable(id="roster_table", cursor_type="row")
                with Horizontal(id="roster-action-bar"):
                    yield Button("Remove Selected Crew", variant="error", id="remove_member_btn")

                yield Label("🎭 Cast Roster Builder (Name, Age, Gender, Physicality):", classes="field-label")
                with Horizontal(id="cast-input-bar-1"):
                    yield Input(placeholder="Actor / Character Name", id="cast_name")
                    yield Input(placeholder="Age Range (e.g. 20s-30s)", id="cast_age")
                with Horizontal(id="cast-input-bar-2"):
                    yield Input(placeholder="Gender (e.g. Female)", id="cast_gender")
                    yield Input(placeholder="Physicality / Appearance", id="cast_physicality")
                    yield Button("Add Cast", variant="primary", id="add_cast_btn")

                yield DataTable(id="cast_table", cursor_type="row")
                with Horizontal(id="cast-action-bar"):
                    yield Button("Remove Selected Cast", variant="error", id="remove_cast_btn")

                yield Label("🛠️ Available Gear & Equipment Catalog (one per line):", classes="field-label")
                gear_text = "\n".join(self.current_profile.available_gear) if self.current_profile and self.current_profile.available_gear else ""
                yield TextArea(gear_text, id="available_gear")

            with Horizontal(id="button-bar"):
                yield Button("Save Profile", variant="primary", id="save_profile_btn")
                yield Button("Cancel", variant="default", id="cancel_profile_btn")

    def on_mount(self) -> None:
        crew_table = self.query_one("#roster_table", DataTable)
        crew_table.add_columns("Role", "Member Name")
        self.refresh_roster_table()

        cast_table = self.query_one("#cast_table", DataTable)
        cast_table.add_columns("Name", "Age Range", "Gender", "Physicality")
        self.refresh_cast_table()

    def refresh_roster_table(self) -> None:
        table = self.query_one("#roster_table", DataTable)
        table.clear()
        for role, members in self.crew.items():
            for name in members:
                table.add_row(role, name)

    def refresh_cast_table(self) -> None:
        table = self.query_one("#cast_table", DataTable)
        table.clear()
        for item in self.cast:
            table.add_row(
                item.get("name", ""),
                item.get("age_range", ""),
                item.get("gender", ""),
                item.get("physicality", ""),
            )

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_profile_btn":
            self.action_save()
        elif event.button.id == "cancel_profile_btn":
            self.action_cancel()
        elif event.button.id == "add_member_btn":
            self.action_add_member()
        elif event.button.id == "remove_member_btn":
            self.action_remove_selected_member()
        elif event.button.id == "add_cast_btn":
            self.action_add_cast_member()
        elif event.button.id == "remove_cast_btn":
            self.action_remove_selected_cast_member()

    def action_add_member(self) -> None:
        role_select = self.query_one("#roster_role", Select)
        name_input = self.query_one("#roster_member_name", Input)

        role_val = role_select.value
        role = (
            str(role_val)
            if role_val is not None and role_val != Select.BLANK and str(role_val) != "<BLANK>"
            else None
        )
        name = name_input.value.strip()

        if not role:
            self.notify("Please select a crew role.", severity="warning")
            return
        if not name:
            self.notify("Please enter a member name.", severity="warning")
            return

        if role not in self.crew:
            self.crew[role] = []
        if name not in self.crew[role]:
            self.crew[role].append(name)

        name_input.value = ""
        self.refresh_roster_table()
        self.notify(f"Added '{name}' as {role}.", severity="information")

    def action_remove_selected_member(self) -> None:
        table = self.query_one("#roster_table", DataTable)
        if table.row_count == 0 or table.cursor_row is None:
            self.notify("No crew entry selected to remove.", severity="warning")
            return

        try:
            row_data = table.get_row_at(table.cursor_row)
            role, name = str(row_data[0]), str(row_data[1])
            if role in self.crew and name in self.crew[role]:
                self.crew[role].remove(name)
                if not self.crew[role]:
                    del self.crew[role]
                self.refresh_roster_table()
                self.notify(f"Removed '{name}' ({role}).", severity="information")
        except Exception as err:
            self.notify(f"Could not remove selected member: {err}", severity="error")

    def action_add_cast_member(self) -> None:
        name = self.query_one("#cast_name", Input).value.strip()
        age_range = self.query_one("#cast_age", Input).value.strip()
        gender = self.query_one("#cast_gender", Input).value.strip()
        physicality = self.query_one("#cast_physicality", Input).value.strip()

        if not name:
            self.notify("Please enter actor/character name.", severity="warning")
            return

        self.cast.append({
            "name": name,
            "age_range": age_range or "Unspecified",
            "gender": gender or "Unspecified",
            "physicality": physicality or "Unspecified",
        })

        self.query_one("#cast_name", Input).value = ""
        self.query_one("#cast_age", Input).value = ""
        self.query_one("#cast_gender", Input).value = ""
        self.query_one("#cast_physicality", Input).value = ""
        self.refresh_cast_table()
        self.notify(f"Added cast member '{name}'.", severity="information")

    def action_remove_selected_cast_member(self) -> None:
        table = self.query_one("#cast_table", DataTable)
        if table.row_count == 0 or table.cursor_row is None:
            self.notify("No cast entry selected to remove.", severity="warning")
            return

        try:
            idx = table.cursor_row
            if 0 <= idx < len(self.cast):
                removed = self.cast.pop(idx)
                self.refresh_cast_table()
                self.notify(f"Removed cast member '{removed.get('name')}'.", severity="information")
        except Exception as err:
            self.notify(f"Could not remove selected cast member: {err}", severity="error")

    def action_save(self) -> None:
        team_name = self.query_one("#team_name", Input).value.strip() or "Unnamed Team"
        admin_username = self.query_one("#admin_username", Input).value.strip() or "admin"
        location = self.query_one("#location", Input).value.strip() or "Unknown Location"

        gear_raw = self.query_one("#available_gear", TextArea).text
        gear_list = [g.strip() for g in gear_raw.splitlines() if g.strip()]

        custom_details = self.current_profile.custom_details if self.current_profile else ""
        active_log = (
            self.current_profile.active_logistical_constraint if self.current_profile else None
        )
        active_dir = (
            self.current_profile.active_directorial_vision if self.current_profile else None
        )
        active_them = (
            self.current_profile.active_thematic_framework if self.current_profile else None
        )
        active_idea = (
            self.current_profile.active_idea_seed if self.current_profile else None
        )

        profile = TeamProfile(
            team_name=team_name,
            admin_username=admin_username,
            location=location,
            crew=self.crew,
            cast=self.cast,
            available_gear=gear_list,
            custom_details=custom_details,
            active_logistical_constraint=active_log,
            active_directorial_vision=active_dir,
            active_thematic_framework=active_them,
            active_idea_seed=active_idea,
        )

        save_profile(profile)
        self.dismiss(profile)
