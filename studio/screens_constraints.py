"""Modal screens for creating and editing Logistical and Creative Constraint Sets."""

from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

from studio.models.constraints import (
    CharacterDetail,
    DirectorialVision,
    IdeaSeed,
    LogisticalConstraint,
    ThematicFramework,
)
from studio.utils.constraint_store import (
    save_directorial_vision,
    save_idea_seed,
    save_logistical_constraint,
    save_thematic_framework,
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
        width: 85%;
        max-width: 75;
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

    VerticalScroll {
        height: 1fr;
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

                yield Label("Available Set Dressing & Wardrobe (one per line):", classes="field-label")
                set_dressing_items = c.available_set_dressing if c else []
                yield TextArea(
                    "\n".join(set_dressing_items),
                    id="available_set_dressing",
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

        loc_details = self.query_one("#location_details", TextArea).text.strip()

        dressing_raw = self.query_one("#available_set_dressing", TextArea).text
        dressing_list = [x.strip() for x in dressing_raw.splitlines() if x.strip()]

        other_chars = self.constraint.other_characters if self.constraint else []

        constraint = LogisticalConstraint(
            name=name_val,
            description=desc_val,
            locations=loc_list,
            sub_locations=sub_loc_list,
            location_details=loc_details,
            other_characters=other_chars,
            available_set_dressing=dressing_list,
        )

        save_logistical_constraint(constraint)
        self.dismiss(constraint)


class DirectorialVisionScreen(ModalScreen[Optional[DirectorialVision]]):
    """Interactive Modal Screen for entering or editing a Directorial Vision set."""

    DEFAULT_CSS = """
    DirectorialVisionScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #directorial-dialog {
        padding: 1 2;
        width: 85%;
        max-width: 75;
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

    VerticalScroll {
        height: 1fr;
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

    def __init__(self, constraint: Optional[DirectorialVision] = None) -> None:
        super().__init__()
        self.constraint = constraint

    def compose(self) -> ComposeResult:
        c = self.constraint
        with Container(id="directorial-dialog"):
            yield Label(
                "🎬 [bold magenta]DIRECTORIAL VISION SET[/bold magenta]\n", classes="title"
            )
            with VerticalScroll():
                yield Label("Vision Set Name (Slug):", classes="field-label")
                yield Input(
                    value=c.name if c else "",
                    placeholder="e.g. a24_slow_burn",
                    id="name",
                    classes="form-field",
                )

                yield Label("Description:", classes="field-label")
                yield Input(
                    value=c.description if c else "",
                    placeholder="e.g. Indie psychological drama vision",
                    id="description",
                    classes="form-field",
                )

                yield Label("Visual Economy & Camera Pacing:", classes="field-label")
                yield TextArea(
                    c.visual_economy if c else "",
                    id="visual_economy",
                )

                yield Label("Lighting Mood & Color Palette:", classes="field-label")
                yield TextArea(
                    c.lighting_color if c else "",
                    id="lighting_color",
                )

                yield Label("Audio Landscape & Music Intent:", classes="field-label")
                yield TextArea(
                    c.audio_landscape if c else "",
                    id="audio_landscape",
                )

            with Horizontal(id="button-bar"):
                yield Button(
                    "Save Directorial Vision",
                    variant="primary",
                    id="save_directorial_btn",
                )
                yield Button("Cancel", variant="default", id="cancel_directorial_btn")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_directorial_btn":
            self.action_save()
        elif event.button.id == "cancel_directorial_btn":
            self.action_cancel()

    def action_save(self) -> None:
        name_val = self.query_one("#name", Input).value.strip() or "unnamed_directorial"
        desc_val = self.query_one("#description", Input).value.strip()

        vis_econ = self.query_one("#visual_economy", TextArea).text
        light_col = self.query_one("#lighting_color", TextArea).text
        audio_land = self.query_one("#audio_landscape", TextArea).text

        constraint = DirectorialVision(
            name=name_val,
            description=desc_val,
            visual_economy=vis_econ,
            lighting_color=light_col,
            audio_landscape=audio_land,
        )

        save_directorial_vision(constraint)
        self.dismiss(constraint)


class ThematicFrameworkScreen(ModalScreen[Optional[ThematicFramework]]):
    """Interactive Modal Screen for entering or editing a Thematic Framework set."""

    DEFAULT_CSS = """
    ThematicFrameworkScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #thematic-dialog {
        padding: 1 2;
        width: 85%;
        max-width: 75;
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

    VerticalScroll {
        height: 1fr;
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

    def __init__(self, constraint: Optional[ThematicFramework] = None) -> None:
        super().__init__()
        self.constraint = constraint

    def compose(self) -> ComposeResult:
        c = self.constraint
        with Container(id="thematic-dialog"):
            yield Label(
                "🧠 [bold cyan]THEMATIC FRAMEWORK SET[/bold cyan]\n", classes="title"
            )
            with VerticalScroll():
                yield Label("Framework Set Name (Slug):", classes="field-label")
                yield Input(
                    value=c.name if c else "",
                    placeholder="e.g. existential_dread",
                    id="name",
                    classes="form-field",
                )

                yield Label("Description:", classes="field-label")
                yield Input(
                    value=c.description if c else "",
                    placeholder="e.g. Exploration of isolation",
                    id="description",
                    classes="form-field",
                )

                yield Label("Core Philosophy & Subtext:", classes="field-label")
                yield TextArea(
                    c.core_philosophy if c else "",
                    id="core_philosophy",
                )

                yield Label("Emotional Arc & Trajectory:", classes="field-label")
                yield TextArea(
                    c.emotional_arc if c else "",
                    id="emotional_arc",
                )

                yield Label("World Rules & Internal Logic:", classes="field-label")
                yield TextArea(
                    c.world_rules if c else "",
                    id="world_rules",
                )

            with Horizontal(id="button-bar"):
                yield Button(
                    "Save Thematic Framework",
                    variant="primary",
                    id="save_thematic_btn",
                )
                yield Button("Cancel", variant="default", id="cancel_thematic_btn")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_thematic_btn":
            self.action_save()
        elif event.button.id == "cancel_thematic_btn":
            self.action_cancel()

    def action_save(self) -> None:
        name_val = self.query_one("#name", Input).value.strip() or "unnamed_thematic"
        desc_val = self.query_one("#description", Input).value.strip()

        core_phil = self.query_one("#core_philosophy", TextArea).text
        emo_arc = self.query_one("#emotional_arc", TextArea).text
        world_r = self.query_one("#world_rules", TextArea).text

        constraint = ThematicFramework(
            name=name_val,
            description=desc_val,
            core_philosophy=core_phil,
            emotional_arc=emo_arc,
            world_rules=world_r,
        )

        save_thematic_framework(constraint)
        self.dismiss(constraint)


class IdeaSeedScreen(ModalScreen[Optional[IdeaSeed]]):
    """Interactive Modal Screen for entering or editing an Idea Seed set."""

    DEFAULT_CSS = """
    IdeaSeedScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #idea-dialog {
        padding: 1 2;
        width: 85%;
        max-width: 75;
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

    VerticalScroll {
        height: 1fr;
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

    def __init__(self, constraint: Optional[IdeaSeed] = None) -> None:
        super().__init__()
        self.constraint = constraint

    def compose(self) -> ComposeResult:
        c = self.constraint
        with Container(id="idea-dialog"):
            yield Label(
                "💡 [bold green]IDEA SEED SET[/bold green]\n", classes="title"
            )
            with VerticalScroll():
                yield Label("Idea Seed Name (Slug):", classes="field-label")
                yield Input(
                    value=c.name if c else "",
                    placeholder="e.g. late_night_visitor",
                    id="name",
                    classes="form-field",
                )

                yield Label("Description:", classes="field-label")
                yield Input(
                    value=c.description if c else "",
                    placeholder="e.g. Unexpected arrival scenario",
                    id="description",
                    classes="form-field",
                )

                yield Label("Inciting Incident / Initial Spark:", classes="field-label")
                yield TextArea(
                    c.inciting_incident if c else "",
                    id="inciting_incident",
                )

                yield Label("Complications & Midpoint Twists:", classes="field-label")
                yield TextArea(
                    c.complications if c else "",
                    id="complications",
                )

                yield Label("Ending Targets & Resolution Notes:", classes="field-label")
                yield TextArea(
                    c.ending_targets if c else "",
                    id="ending_targets",
                )

                yield Label("Max Recommended Actors (Optional):", classes="field-label")
                yield Input(
                    value=str(c.max_actors) if c and c.max_actors is not None else "",
                    placeholder="e.g. 2, 3 (leave blank for flexible/unlimited)",
                    id="max_actors",
                    classes="form-field",
                )

            with Horizontal(id="button-bar"):
                yield Button(
                    "Save Idea Seed",
                    variant="primary",
                    id="save_idea_btn",
                )
                yield Button("Cancel", variant="default", id="cancel_idea_btn")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_idea_btn":
            self.action_save()
        elif event.button.id == "cancel_idea_btn":
            self.action_cancel()

    def action_save(self) -> None:
        name_val = self.query_one("#name", Input).value.strip() or "unnamed_idea"
        desc_val = self.query_one("#description", Input).value.strip()

        inc_inc = self.query_one("#inciting_incident", TextArea).text
        comp = self.query_one("#complications", TextArea).text
        end_t = self.query_one("#ending_targets", TextArea).text

        max_act_raw = self.query_one("#max_actors", Input).value.strip()
        max_act_val = int(max_act_raw) if max_act_raw.isdigit() and int(max_act_raw) > 0 else None

        constraint = IdeaSeed(
            name=name_val,
            description=desc_val,
            inciting_incident=inc_inc,
            complications=comp,
            ending_targets=end_t,
            max_actors=max_act_val,
        )

        save_idea_seed(constraint)
        self.dismiss(constraint)


