"""Modal screens for in-TUI configuration setup and Friday Draw wizard."""

from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

from studio.models.draw import (
    GENRES_GROUP_1,
    GENRES_GROUP_2,
    FridayDraw,
    create_default_draw,
)
from studio.models.profile import TeamProfile
from studio.utils.draw_store import save_draw
from studio.utils.profile_store import save_profile


class DrawWizardScreen(ModalScreen[Optional[FridayDraw]]):
    """Interactive Modal Screen for entering or editing Friday Draw kickoff data."""

    DEFAULT_CSS = """
    DrawWizardScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #draw-dialog {
        padding: 1 2;
        width: 68;
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
    """Interactive Modal Screen for setup or editing of Team Profile."""

    DEFAULT_CSS = """
    ProfileSetupScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #profile-dialog {
        padding: 1 2;
        width: 60;
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

    def __init__(self, current_profile: Optional[TeamProfile] = None) -> None:
        super().__init__()
        self.current_profile = current_profile

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

            with Horizontal(id="button-bar"):
                yield Button("Save Profile", variant="primary", id="save_profile_btn")
                yield Button("Cancel", variant="default", id="cancel_profile_btn")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_profile_btn":
            self.action_save()
        elif event.button.id == "cancel_profile_btn":
            self.action_cancel()

    def action_save(self) -> None:
        team_name = self.query_one("#team_name", Input).value.strip() or "Unnamed Team"
        admin_username = self.query_one("#admin_username", Input).value.strip() or "admin"
        location = self.query_one("#location", Input).value.strip() or "Unknown Location"

        roles = self.current_profile.roles if self.current_profile else {}
        custom_details = self.current_profile.custom_details if self.current_profile else ""
        active_log = (
            self.current_profile.active_logistical_constraint if self.current_profile else None
        )
        active_cre = (
            self.current_profile.active_creative_constraint if self.current_profile else None
        )

        profile = TeamProfile(
            team_name=team_name,
            admin_username=admin_username,
            location=location,
            roles=roles,
            custom_details=custom_details,
            active_logistical_constraint=active_log,
            active_creative_constraint=active_cre,
        )

        save_profile(profile)
        self.dismiss(profile)
