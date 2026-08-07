"""Modal screens for creating and editing Logistical and Creative Constraint Sets."""

from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

from studio.models.constraints import (
    CharacterDetail,
    CreativeConstraint,
    LogisticalConstraint,
)
from studio.utils.constraint_store import (
    save_creative_constraint,
    save_logistical_constraint,
)


class LogisticalConstraintScreen(ModalScreen[Optional[LogisticalConstraint]]):
    """Interactive Modal Screen for entering or editing a Logistical Constraint Set."""

    DEFAULT_CSS = """
    LogisticalConstraintScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #logistical-dialog {
        padding: 1 2;
        width: 72;
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

    TextArea {
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

    def __init__(self, constraint: Optional[LogisticalConstraint] = None) -> None:
        super().__init__()
        self.constraint = constraint

    def compose(self) -> ComposeResult:
        c = self.constraint
        with Container(id="logistical-dialog"):
            yield Label(
                "📋 [bold yellow]LOGISTICAL CONSTRAINT SET[/bold yellow]\n", classes="title"
            )
            with VerticalScroll():
                yield Label("Constraint Set Name (Slug):", classes="field-label")
                yield Input(
                    value=c.name if c else "",
                    placeholder="e.g. interior_indie_crew",
                    id="name",
                    classes="form-field",
                )

                yield Label("Description:", classes="field-label")
                yield Input(
                    value=c.description if c else "",
                    placeholder="e.g. Indoor shoot setup with small crew",
                    id="description",
                    classes="form-field",
                )

                yield Label("Locations (comma-separated):", classes="field-label")
                yield Input(
                    value=", ".join(c.locations) if c else "",
                    placeholder="e.g. Interior, Apartment, Day/Night",
                    id="locations",
                    classes="form-field",
                )

                yield Label("Sub-Locations (comma-separated):", classes="field-label")
                yield Input(
                    value=", ".join(c.sub_locations) if c else "",
                    placeholder="e.g. Living Room, Kitchen, Balcony",
                    id="sub_locations",
                    classes="form-field",
                )

                yield Label("Location Details:", classes="field-label")
                yield TextArea(
                    c.location_details if c else "",
                    id="location_details",
                )

                yield Label("Main Character Name:", classes="field-label")
                main_char = c.main_character_details if c else None
                yield Input(
                    value=main_char.name if main_char else "",
                    placeholder="e.g. Protagonist",
                    id="main_char_name",
                    classes="form-field",
                )

                yield Label("Main Character Actor Traits:", classes="field-label")
                yield Input(
                    value=main_char.actor_traits if main_char else "",
                    placeholder="e.g. Late 20s, expressive eyes",
                    id="main_char_traits",
                    classes="form-field",
                )

                yield Label("Main Character Wardrobe:", classes="field-label")
                yield Input(
                    value=main_char.wardrobe if main_char else "",
                    placeholder="e.g. Denim jacket, sneakers",
                    id="main_char_wardrobe",
                    classes="form-field",
                )

                yield Label("Main Character Notes:", classes="field-label")
                yield Input(
                    value=main_char.notes if main_char else "",
                    placeholder="e.g. Anxious under pressure",
                    id="main_char_notes",
                    classes="form-field",
                )

                yield Label("Props & Dialogue Hooks (one per line):", classes="field-label")
                yield TextArea(
                    "\n".join(c.props_and_dialogue) if c else "",
                    id="props_and_dialogue",
                )

            with Horizontal(id="button-bar"):
                yield Button(
                    "Save Logistical Constraint",
                    variant="primary",
                    id="save_logistical_btn",
                )
                yield Button("Cancel", variant="default", id="cancel_logistical_btn")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_logistical_btn":
            self.action_save()
        elif event.button.id == "cancel_logistical_btn":
            self.action_cancel()

    def action_save(self) -> None:
        name_val = self.query_one("#name", Input).value.strip() or "unnamed_logistical"
        desc_val = self.query_one("#description", Input).value.strip()

        loc_raw = self.query_one("#locations", Input).value
        loc_list = [x.strip() for x in loc_raw.split(",") if x.strip()]

        sub_loc_raw = self.query_one("#sub_locations", Input).value
        sub_loc_list = [x.strip() for x in sub_loc_raw.split(",") if x.strip()]

        loc_details = self.query_one("#location_details", TextArea).text

        c_name = self.query_one("#main_char_name", Input).value.strip()
        c_traits = self.query_one("#main_char_traits", Input).value.strip()
        c_wardrobe = self.query_one("#main_char_wardrobe", Input).value.strip()
        c_notes = self.query_one("#main_char_notes", Input).value.strip()

        main_char = None
        if c_name or c_traits or c_wardrobe or c_notes:
            main_char = CharacterDetail(
                name=c_name or "Character",
                actor_traits=c_traits,
                wardrobe=c_wardrobe,
                notes=c_notes,
            )

        props_raw = self.query_one("#props_and_dialogue", TextArea).text
        props_list = [x.strip() for x in props_raw.splitlines() if x.strip()]

        other_chars = self.constraint.other_characters if self.constraint else []

        constraint = LogisticalConstraint(
            name=name_val,
            description=desc_val,
            locations=loc_list,
            sub_locations=sub_loc_list,
            location_details=loc_details,
            main_character_details=main_char,
            other_characters=other_chars,
            props_and_dialogue=props_list,
        )

        save_logistical_constraint(constraint)
        self.dismiss(constraint)


class CreativeConstraintScreen(ModalScreen[Optional[CreativeConstraint]]):
    """Interactive Modal Screen for entering or editing a Creative Constraint Set."""

    DEFAULT_CSS = """
    CreativeConstraintScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #creative-dialog {
        padding: 1 2;
        width: 72;
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

    TextArea {
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

    def __init__(self, constraint: Optional[CreativeConstraint] = None) -> None:
        super().__init__()
        self.constraint = constraint

    def compose(self) -> ComposeResult:
        c = self.constraint
        with Container(id="creative-dialog"):
            yield Label(
                "🎨 [bold magenta]CREATIVE CONSTRAINT SET[/bold magenta]\n", classes="title"
            )
            with VerticalScroll():
                yield Label("Constraint Set Name (Slug):", classes="field-label")
                yield Input(
                    value=c.name if c else "",
                    placeholder="e.g. a24_slow_burn",
                    id="name",
                    classes="form-field",
                )

                yield Label("Description:", classes="field-label")
                yield Input(
                    value=c.description if c else "",
                    placeholder="e.g. Indie psychological drama",
                    id="description",
                    classes="form-field",
                )

                yield Label("Scenarios (one per line):", classes="field-label")
                yield TextArea(
                    "\n".join(c.scenarios) if c else "",
                    id="scenarios",
                )

                yield Label("Core Philosophy / Thematic Spine:", classes="field-label")
                yield TextArea(
                    c.core_philosophy if c else "",
                    id="core_philosophy",
                )

                yield Label("Scene Economy / Pacing Directives:", classes="field-label")
                yield TextArea(
                    c.scene_economy if c else "",
                    id="scene_economy",
                )

                yield Label("Progression & Climax Dynamics:", classes="field-label")
                yield TextArea(
                    c.progression_and_climax if c else "",
                    id="progression_and_climax",
                )

                yield Label("Visuals, Audio & Post-Production Intent:", classes="field-label")
                yield TextArea(
                    c.visuals_and_post if c else "",
                    id="visuals_and_post",
                )

            with Horizontal(id="button-bar"):
                yield Button(
                    "Save Creative Constraint",
                    variant="primary",
                    id="save_creative_btn",
                )
                yield Button("Cancel", variant="default", id="cancel_creative_btn")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_creative_btn":
            self.action_save()
        elif event.button.id == "cancel_creative_btn":
            self.action_cancel()

    def action_save(self) -> None:
        name_val = self.query_one("#name", Input).value.strip() or "unnamed_creative"
        desc_val = self.query_one("#description", Input).value.strip()

        scenarios_raw = self.query_one("#scenarios", TextArea).text
        scenarios_list = [x.strip() for x in scenarios_raw.splitlines() if x.strip()]

        phil = self.query_one("#core_philosophy", TextArea).text
        economy = self.query_one("#scene_economy", TextArea).text
        progression = self.query_one("#progression_and_climax", TextArea).text
        visuals = self.query_one("#visuals_and_post", TextArea).text

        constraint = CreativeConstraint(
            name=name_val,
            description=desc_val,
            scenarios=scenarios_list,
            core_philosophy=phil,
            scene_economy=economy,
            progression_and_climax=progression,
            visuals_and_post=visuals,
        )

        save_creative_constraint(constraint)
        self.dismiss(constraint)
