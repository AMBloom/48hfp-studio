"""CLI commands for managing Logistical, Directorial, Thematic, and Idea Constraint Sets (CRUD & Active State)."""

from typing import List, Optional
import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from studio.models.constraints import (
    CharacterDetail,
    ConstraintType,
    DirectorialVision,
    IdeaSeed,
    LogisticalConstraint,
    ThematicFramework,
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
    save_directorial_vision,
    save_idea_seed,
    save_logistical_constraint,
    save_thematic_framework,
    seed_default_constraints,
)
from studio.utils.profile_store import load_profile, save_profile
from studio.utils.ui import (
    display_constraints_table,
    display_directorial_detail,
    display_idea_detail,
    display_logistical_detail,
    display_thematic_detail,
    print_banner,
    print_error,
    print_panel,
    print_success,
    print_warning,
)

constraints_app = typer.Typer(
    name="constraints",
    help="Manage, create, edit, list, and toggle active constraint sets.",
    no_args_is_help=False,
)
console = Console()


@constraints_app.callback(invoke_without_command=True)
def constraints_default(ctx: typer.Context) -> None:
    """Default action for '48hfp constraints': list all available sets."""
    if ctx.invoked_subcommand is None:
        list_constraints()


@constraints_app.command("list")
def list_constraints() -> None:
    """List all available constraint sets with active indicators."""
    seed_default_constraints()
    prof = load_profile()

    active_logistical = prof.active_logistical_constraint if prof else None
    active_directorial = prof.active_directorial_vision if prof else None
    active_thematic = prof.active_thematic_framework if prof else None
    active_idea = prof.active_idea_seed if prof else None

    logistical_sets = list_logistical_constraints()
    directorial_sets = list_directorial_visions()
    thematic_sets = list_thematic_frameworks()
    idea_sets = list_idea_seeds()

    print_banner()
    display_constraints_table(
        logistical_sets=logistical_sets,
        directorial_sets=directorial_sets,
        thematic_sets=thematic_sets,
        idea_sets=idea_sets,
        active_logistical=active_logistical,
        active_directorial=active_directorial,
        active_thematic=active_thematic,
        active_idea=active_idea,
    )


@constraints_app.command("create")
def create_constraint(
    c_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Constraint type: 'logistical', 'directorial', 'thematic', or 'idea'"
    ),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Unique slug name (e.g. interior_indie)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Brief set summary"),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Create set non-interactively using defaults/flags"
    ),
) -> None:
    """Create a new constraint set."""
    print_banner()
    console.print("[bold cyan]✨ Create New Constraint Set[/bold cyan]\n")

    if not c_type:
        if non_interactive:
            c_type = "logistical"
        else:
            c_type = Prompt.ask(
                "Constraint Set Type",
                choices=["logistical", "directorial", "thematic", "idea"],
                default="logistical",
            )

    c_type_clean = c_type.strip().lower()
    if c_type_clean not in ["logistical", "directorial", "thematic", "idea"]:
        print_error("Invalid constraint type. Must be 'logistical', 'directorial', 'thematic', or 'idea'.")
        raise typer.Exit(code=1)

    # --- Logistical Creation ---
    if c_type_clean == "logistical":
        if non_interactive:
            set_name = name or "new_logistical_set"
            set_desc = description or "Non-interactive logistical set"
            locations = ["Interior"]
            sub_locations = ["Main Room"]
            loc_details = "Standard lighting and layout."
            main_char = CharacterDetail(name="Lead Character")
            other_chars: List[CharacterDetail] = []
            props = ["Default Prop"]
        else:
            set_name = name or Prompt.ask("Set Slug Name (e.g. coffee_shop_night)")
            set_desc = description or Prompt.ask("Set Summary/Description", default="Custom logistical setup")

            console.print("\n[bold yellow]📍 Locations & Physical Reality[/bold yellow]")
            loc_ans = Prompt.ask("Filming Locations (comma-separated)", default="Interior, Coffee Shop, Night")
            locations = [x.strip() for x in loc_ans.split(",") if x.strip()]

            sub_loc_ans = Prompt.ask("Sub-Locations (comma-separated)", default="Counter, Back Seating, Patio")
            sub_locations = [x.strip() for x in sub_loc_ans.split(",") if x.strip()]

            loc_details = Prompt.ask("Location Details (layout, restrictions, lighting)", default="Dim ambient lighting.")

            console.print("\n[bold yellow]👤 Main Character Extension Details[/bold yellow]")
            mc_name = Prompt.ask("Main Character Name/Role", default="Protagonist")
            mc_traits = Prompt.ask("Actor Traits/Appearance", default="Casual, mid-30s")
            mc_wardrobe = Prompt.ask("Wardrobe", default="Dark hoodie, jeans")
            mc_notes = Prompt.ask("Acting Notes", default="Restless, observant")
            main_char = CharacterDetail(name=mc_name, actor_traits=mc_traits, wardrobe=mc_wardrobe, notes=mc_notes)

            other_chars = []
            if Confirm.ask("\nAdd an additional character to this set?"):
                while True:
                    oc_name = Prompt.ask("Character Name (or leave blank to finish)")
                    if not oc_name.strip():
                        break
                    oc_traits = Prompt.ask(f"Traits for {oc_name}")
                    oc_wardrobe = Prompt.ask(f"Wardrobe for {oc_name}")
                    oc_notes = Prompt.ask(f"Notes for {oc_name}")
                    other_chars.append(
                        CharacterDetail(name=oc_name, actor_traits=oc_traits, wardrobe=oc_wardrobe, notes=oc_notes)
                    )

            console.print("\n[bold yellow]🎭 Props & Dialogue Hooks[/bold yellow]")
            props_ans = Prompt.ask("Props / Dialogue Hooks (comma-separated)", default="Cold espresso, Ringing phone")
            props = [p.strip() for x in props_ans.split(",") if p.strip()]

        logistical_set = LogisticalConstraint(
            name=set_name,
            description=set_desc,
            locations=locations,
            sub_locations=sub_locations,
            location_details=loc_details,
            main_character_details=main_char,
            other_characters=other_chars,
            props_and_dialogue=props,
        )
        saved_path = save_logistical_constraint(logistical_set)
        print_success(f"Logistical Constraint Set successfully created at [bold white]{saved_path}[/bold white]\n")
        display_logistical_detail(logistical_set, is_active=False)

    # --- Directorial Creation ---
    elif c_type_clean == "directorial":
        if non_interactive:
            set_name = name or "new_directorial_vision"
            set_desc = description or "Non-interactive directorial vision"
            vis_econ = "Long static takes, deliberate cuts."
            light_col = "Natural ambient light."
            audio_land = "Subtle acoustic drones."
        else:
            set_name = name or Prompt.ask("Set Slug Name (e.g. neo_noir_thriller)")
            set_desc = description or Prompt.ask("Set Summary/Description", default="Custom directorial vision")
            vis_econ = Prompt.ask("Visual Economy & Camera Movement", default="Steady handheld, long takes.")
            light_col = Prompt.ask("Lighting Mood & Color Palette", default="High contrast neon reflections.")
            audio_land = Prompt.ask("Audio Landscape & Music Intent", default="Pulsing synth score.")

        directorial_set = DirectorialVision(
            name=set_name,
            description=set_desc,
            visual_economy=vis_econ,
            lighting_color=light_col,
            audio_landscape=audio_land,
        )
        saved_path = save_directorial_vision(directorial_set)
        print_success(f"Directorial Vision Set successfully created at [bold white]{saved_path}[/bold white]\n")
        display_directorial_detail(directorial_set, is_active=False)

    # --- Thematic Creation ---
    elif c_type_clean == "thematic":
        if non_interactive:
            set_name = name or "new_thematic_framework"
            set_desc = description or "Non-interactive thematic framework"
            core_phil = "Exploration of choices."
            emo_arc = "Escalating tension."
            world_r = "Domestic realism."
        else:
            set_name = name or Prompt.ask("Set Slug Name (e.g. identity_crisis)")
            set_desc = description or Prompt.ask("Set Summary/Description", default="Custom thematic framework")
            core_phil = Prompt.ask("Core Philosophy & Subtext", default="Moral ambiguity and claustrophobic choices.")
            emo_arc = Prompt.ask("Emotional Arc & Climax Dynamics", default="Quiet build-up exploding into emotional crisis.")
            world_r = Prompt.ask("World Rules & Internal Logic", default="Strict realism where secrets have consequences.")

        thematic_set = ThematicFramework(
            name=set_name,
            description=set_desc,
            core_philosophy=core_phil,
            emotional_arc=emo_arc,
            world_rules=world_r,
        )
        saved_path = save_thematic_framework(thematic_set)
        print_success(f"Thematic Framework Set successfully created at [bold white]{saved_path}[/bold white]\n")
        display_thematic_detail(thematic_set, is_active=False)

    # --- Idea Creation ---
    else:
        if non_interactive:
            set_name = name or "new_idea_seed"
            set_desc = description or "Non-interactive idea seed"
            inc_inc = "An unexpected letter arrives."
            comp = "A missing key causes a standoff."
            end_t = "A quiet resolution."
        else:
            set_name = name or Prompt.ask("Set Slug Name (e.g. midnight_knock)")
            set_desc = description or Prompt.ask("Set Summary/Description", default="Custom idea seed")
            inc_inc = Prompt.ask("Inciting Incident / Initial Spark", default="An unexpected stranger knocks during a storm.")
            comp = Prompt.ask("Complications & Midpoint Twists", default="Conflicting stories unravel trust.")
            end_t = Prompt.ask("Ending Targets & Resolution Notes", default="A surprise reveal in the final shot.")

        idea_set = IdeaSeed(
            name=set_name,
            description=set_desc,
            inciting_incident=inc_inc,
            complications=comp,
            ending_targets=end_t,
        )
        saved_path = save_idea_seed(idea_set)
        print_success(f"Idea Seed Set successfully created at [bold white]{saved_path}[/bold white]\n")
        display_idea_detail(idea_set, is_active=False)


@constraints_app.command("show")
def show_constraint(
    name: str = typer.Argument(..., help="Slug name of the constraint set"),
    c_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Constraint type: 'logistical', 'directorial', 'thematic', or 'idea'"
    ),
) -> None:
    """Display detailed view of a specific constraint set."""
    seed_default_constraints()
    prof = load_profile()

    lc = load_logistical_constraint(name) if not c_type or c_type == "logistical" else None
    dv = load_directorial_vision(name) if not c_type or c_type == "directorial" else None
    tf = load_thematic_framework(name) if not c_type or c_type == "thematic" else None
    ids = load_idea_seed(name) if not c_type or c_type == "idea" else None

    if not any([lc, dv, tf, ids]) and not c_type:
        lc = load_logistical_constraint(name)
        dv = load_directorial_vision(name)
        tf = load_thematic_framework(name)
        ids = load_idea_seed(name)

    print_banner()
    if lc:
        is_act = prof and prof.active_logistical_constraint == lc.name
        display_logistical_detail(lc, is_active=is_act)
    elif dv:
        is_act = prof and prof.active_directorial_vision == dv.name
        display_directorial_detail(dv, is_active=is_act)
    elif tf:
        is_act = prof and prof.active_thematic_framework == tf.name
        display_thematic_detail(tf, is_active=is_act)
    elif ids:
        is_act = prof and prof.active_idea_seed == ids.name
        display_idea_detail(ids, is_active=is_act)
    else:
        print_error(f"Constraint set '{name}' not found.")
        raise typer.Exit(code=1)


@constraints_app.command("edit")
def edit_constraint(
    name: str = typer.Argument(..., help="Slug name of the constraint set to edit"),
    c_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Constraint type: 'logistical', 'directorial', 'thematic', or 'idea'"
    ),
) -> None:
    """Interactively edit fields of an existing constraint set."""
    seed_default_constraints()
    lc = load_logistical_constraint(name) if not c_type or c_type == "logistical" else None
    dv = load_directorial_vision(name) if not c_type or c_type == "directorial" else None
    tf = load_thematic_framework(name) if not c_type or c_type == "thematic" else None
    ids = load_idea_seed(name) if not c_type or c_type == "idea" else None

    if not any([lc, dv, tf, ids]) and not c_type:
        lc = load_logistical_constraint(name)
        dv = load_directorial_vision(name)
        tf = load_thematic_framework(name)
        ids = load_idea_seed(name)

    print_banner()
    if lc:
        console.print(f"[bold cyan]✏ Editing Logistical Constraint Set: {lc.name}[/bold cyan]\n")
        lc.description = Prompt.ask("Description", default=lc.description)
        save_logistical_constraint(lc)
        print_success(f"Logistical Constraint Set '{lc.name}' updated!")
        display_logistical_detail(lc)
    elif dv:
        console.print(f"[bold magenta]✏ Editing Directorial Vision: {dv.name}[/bold magenta]\n")
        dv.description = Prompt.ask("Description", default=dv.description)
        dv.visual_economy = Prompt.ask("Visual Economy", default=dv.visual_economy)
        dv.lighting_color = Prompt.ask("Lighting & Color", default=dv.lighting_color)
        dv.audio_landscape = Prompt.ask("Audio Landscape", default=dv.audio_landscape)
        save_directorial_vision(dv)
        print_success(f"Directorial Vision Set '{dv.name}' updated!")
        display_directorial_detail(dv)
    elif tf:
        console.print(f"[bold blue]✏ Editing Thematic Framework: {tf.name}[/bold blue]\n")
        tf.description = Prompt.ask("Description", default=tf.description)
        tf.core_philosophy = Prompt.ask("Core Philosophy", default=tf.core_philosophy)
        tf.emotional_arc = Prompt.ask("Emotional Arc", default=tf.emotional_arc)
        tf.world_rules = Prompt.ask("World Rules", default=tf.world_rules)
        save_thematic_framework(tf)
        print_success(f"Thematic Framework Set '{tf.name}' updated!")
        display_thematic_detail(tf)
    elif ids:
        console.print(f"[bold yellow]✏ Editing Idea Seed: {ids.name}[/bold yellow]\n")
        ids.description = Prompt.ask("Description", default=ids.description)
        ids.inciting_incident = Prompt.ask("Inciting Incident", default=ids.inciting_incident)
        ids.complications = Prompt.ask("Complications", default=ids.complications)
        ids.ending_targets = Prompt.ask("Ending Targets", default=ids.ending_targets)
        save_idea_seed(ids)
        print_success(f"Idea Seed Set '{ids.name}' updated!")
        display_idea_detail(ids)
    else:
        print_error(f"Constraint set '{name}' not found.")
        raise typer.Exit(code=1)


@constraints_app.command("delete")
def delete_constraint(
    name: str = typer.Argument(..., help="Slug name of the constraint set to delete"),
    c_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Constraint type: 'logistical', 'directorial', 'thematic', or 'idea'"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation prompt"),
) -> None:
    """Delete a constraint set by name."""
    lc = load_logistical_constraint(name) if not c_type or c_type == "logistical" else None
    dv = load_directorial_vision(name) if not c_type or c_type == "directorial" else None
    tf = load_thematic_framework(name) if not c_type or c_type == "thematic" else None
    ids = load_idea_seed(name) if not c_type or c_type == "idea" else None

    if not any([lc, dv, tf, ids]) and not c_type:
        lc = load_logistical_constraint(name)
        dv = load_directorial_vision(name)
        tf = load_thematic_framework(name)
        ids = load_idea_seed(name)

    if not any([lc, dv, tf, ids]):
        print_error(f"Constraint set '{name}' not found.")
        raise typer.Exit(code=1)

    target_type = "logistical" if lc else "directorial" if dv else "thematic" if tf else "idea"

    if not force:
        if not Confirm.ask(f"Are you sure you want to delete the {target_type} set '{name}'?"):
            print_warning("Deletion cancelled.")
            return

    prof = load_profile()
    deleted = False
    if target_type == "logistical":
        deleted = delete_logistical_constraint(name)
        if prof and prof.active_logistical_constraint == name:
            prof.active_logistical_constraint = None
            save_profile(prof)
    elif target_type == "directorial":
        deleted = delete_directorial_vision(name)
        if prof and prof.active_directorial_vision == name:
            prof.active_directorial_vision = None
            save_profile(prof)
    elif target_type == "thematic":
        deleted = delete_thematic_framework(name)
        if prof and prof.active_thematic_framework == name:
            prof.active_thematic_framework = None
            save_profile(prof)
    elif target_type == "idea":
        deleted = delete_idea_seed(name)
        if prof and prof.active_idea_seed == name:
            prof.active_idea_seed = None
            save_profile(prof)

    if deleted:
        print_success(f"Successfully deleted {target_type} constraint set '{name}'.")
    else:
        print_error(f"Failed to delete {target_type} constraint set '{name}'.")


@constraints_app.command("set-active")
def set_active_constraints(
    logistical: Optional[str] = typer.Option(None, "--logistical", "-l", help="Name of logistical set to activate"),
    directorial: Optional[str] = typer.Option(None, "--directorial", "-d", help="Name of directorial vision to activate"),
    thematic: Optional[str] = typer.Option(None, "--thematic", "-t", help="Name of thematic framework to activate"),
    idea: Optional[str] = typer.Option(None, "--idea", "-i", help="Name of idea seed to activate"),
) -> None:
    """Set which constraint sets are active for generation."""
    seed_default_constraints()
    prof = load_profile()

    if not prof:
        print_error("No global team profile found. Run '48hfp config setup' first.")
        raise typer.Exit(code=1)

    if not any([logistical, directorial, thematic, idea]):
        print_warning("No constraint set specified.")
        raise typer.Exit(code=1)

    print_banner()

    if logistical:
        lc = load_logistical_constraint(logistical)
        if not lc:
            print_error(f"Logistical constraint set '{logistical}' not found.")
            raise typer.Exit(code=1)
        prof.active_logistical_constraint = lc.name
        print_success(f"Active Logistical Constraint Set updated to: [bold cyan]{lc.name}[/bold cyan]")

    if directorial:
        dv = load_directorial_vision(directorial)
        if not dv:
            print_error(f"Directorial vision set '{directorial}' not found.")
            raise typer.Exit(code=1)
        prof.active_directorial_vision = dv.name
        print_success(f"Active Directorial Vision updated to: [bold magenta]{dv.name}[/bold magenta]")

    if thematic:
        tf = load_thematic_framework(thematic)
        if not tf:
            print_error(f"Thematic framework set '{thematic}' not found.")
            raise typer.Exit(code=1)
        prof.active_thematic_framework = tf.name
        print_success(f"Active Thematic Framework updated to: [bold blue]{tf.name}[/bold blue]")

    if idea:
        ids = load_idea_seed(idea)
        if not ids:
            print_error(f"Idea seed set '{idea}' not found.")
            raise typer.Exit(code=1)
        prof.active_idea_seed = ids.name
        print_success(f"Active Idea Seed updated to: [bold green]{ids.name}[/bold green]")

    save_profile(prof)
    console.print()
    show_active()


@constraints_app.command("show-active")
def show_active() -> None:
    """Display currently primed active constraint sets."""
    seed_default_constraints()
    prof = load_profile()

    print_banner()

    log_name = prof.active_logistical_constraint if prof else None
    dir_name = prof.active_directorial_vision if prof else None
    them_name = prof.active_thematic_framework if prof else None
    idea_name = prof.active_idea_seed if prof else None

    lc = load_logistical_constraint(log_name) if log_name else None
    dv = load_directorial_vision(dir_name) if dir_name else None
    tf = load_thematic_framework(them_name) if them_name else None
    ids = load_idea_seed(idea_name) if idea_name else None

    log_status = f"[bold cyan]{lc.name}[/bold cyan]" if lc else "[yellow]None selected[/yellow]"
    dir_status = f"[bold magenta]{dv.name}[/bold magenta]" if dv else "[yellow]None selected[/yellow]"
    them_status = f"[bold blue]{tf.name}[/bold blue]" if tf else "[yellow]None selected[/yellow]"
    idea_status = f"[bold green]{ids.name}[/bold green]" if ids else "[yellow]None selected[/yellow]"

    content = (
        f"[bold white]Primed Generation Context[/bold white]\n\n"
        f"🚚 Active Logistical Set: {log_status}\n"
        f"🎬 Active Directorial Vision: {dir_status}\n"
        f"🧠 Active Thematic Framework: {them_status}\n"
        f"💡 Active Idea Seed: {idea_status}\n"
    )

    print_panel(content=content, title="⚡ Primed Active Constraint Sets", border_style="green")

    if lc:
        display_logistical_detail(lc, is_active=True)
    if dv:
        display_directorial_detail(dv, is_active=True)
    if tf:
        display_thematic_detail(tf, is_active=True)
    if ids:
        display_idea_detail(ids, is_active=True)

