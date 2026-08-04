"""CLI commands for managing Logistical and Creative Constraint Sets (CRUD & Active State)."""

from typing import List, Optional
import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from studio.models.constraints import (
    CharacterDetail,
    ConstraintType,
    CreativeConstraint,
    LogisticalConstraint,
)
from studio.utils.constraint_store import (
    delete_creative_constraint,
    delete_logistical_constraint,
    list_creative_constraints,
    list_logistical_constraints,
    load_creative_constraint,
    load_logistical_constraint,
    save_creative_constraint,
    save_logistical_constraint,
    seed_default_constraints,
)
from studio.utils.profile_store import load_profile, save_profile
from studio.utils.ui import (
    display_constraints_table,
    display_creative_detail,
    display_logistical_detail,
    print_banner,
    print_error,
    print_panel,
    print_success,
    print_warning,
)

constraints_app = typer.Typer(
    name="constraints",
    help="Manage, create, edit, list, and toggle active Logistical and Creative Constraint Sets.",
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
    """List all available Logistical and Creative Constraint Sets with active indicators."""
    seed_default_constraints()
    prof = load_profile()

    active_logistical = prof.active_logistical_constraint if prof else None
    active_creative = prof.active_creative_constraint if prof else None

    logistical_sets = list_logistical_constraints()
    creative_sets = list_creative_constraints()

    print_banner()
    display_constraints_table(
        logistical_sets=logistical_sets,
        creative_sets=creative_sets,
        active_logistical=active_logistical,
        active_creative=active_creative,
    )


@constraints_app.command("create")
def create_constraint(
    c_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Constraint type: 'logistical' or 'creative'"
    ),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Unique slug name (e.g. interior_indie)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Brief set summary"),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Create set non-interactively using defaults/flags"
    ),
) -> None:
    """Create a new Logistical or Creative Constraint Set."""
    print_banner()
    console.print("[bold cyan]✨ Create New Constraint Set[/bold cyan]\n")

    if not c_type:
        if non_interactive:
            c_type = "logistical"
        else:
            c_type = Prompt.ask(
                "Constraint Set Type",
                choices=["logistical", "creative"],
                default="logistical",
            )

    c_type_clean = c_type.strip().lower()
    if c_type_clean not in ["logistical", "creative"]:
        print_error("Invalid constraint type. Must be 'logistical' or 'creative'.")
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

    # --- Creative Creation ---
    else:
        if non_interactive:
            set_name = name or "new_creative_set"
            set_desc = description or "Non-interactive creative set"
            scenarios = ["A tense encounter at dusk."]
            philosophy = "Directorial vision emphasizing mood and subtext."
            economy = "Balanced pacing."
            progression = "Three-act emotional arc."
            visuals = "Natural contrast and organic audio."
        else:
            set_name = name or Prompt.ask("Set Slug Name (e.g. neo_noir_thriller)")
            set_desc = description or Prompt.ask("Set Summary/Description", default="Custom creative vision")

            console.print("\n[bold yellow]🎬 Story Scenarios & Philosophy[/bold yellow]")
            sc_ans = Prompt.ask("Pre-Baked Scenario 1", default="A high-stakes trade goes wrong in secret.")
            scenarios = [sc_ans] if sc_ans.strip() else []
            if Confirm.ask("Add a second story scenario?"):
                sc2 = Prompt.ask("Pre-Baked Scenario 2")
                if sc2.strip():
                    scenarios.append(sc2.strip())

            philosophy = Prompt.ask("Core Philosophy & Thematic Spine", default="Moral ambiguity and claustrophobic choices.")
            economy = Prompt.ask("Scene Economy & Pacing Directives", default="Quick cuts, tight close-ups, snappy dialog.")
            progression = Prompt.ask("Progression & Climax Structure", default="Slow build-up exploding into sudden action.")
            visuals = Prompt.ask("Visuals, Lighting & Post Guidelines", default="High contrast, neon reflections, pulsing soundtrack.")

        creative_set = CreativeConstraint(
            name=set_name,
            description=set_desc,
            scenarios=scenarios,
            core_philosophy=philosophy,
            scene_economy=economy,
            progression_and_climax=progression,
            visuals_and_post=visuals,
        )
        saved_path = save_creative_constraint(creative_set)
        print_success(f"Creative Constraint Set successfully created at [bold white]{saved_path}[/bold white]\n")
        display_creative_detail(creative_set, is_active=False)


@constraints_app.command("show")
def show_constraint(
    name: str = typer.Argument(..., help="Slug name of the constraint set"),
    c_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Constraint type: 'logistical' or 'creative'"
    ),
) -> None:
    """Display detailed view of a specific constraint set."""
    seed_default_constraints()
    prof = load_profile()

    lc = None
    cc = None

    if c_type:
        clean_type = c_type.strip().lower()
        if clean_type == "logistical":
            lc = load_logistical_constraint(name)
        elif clean_type == "creative":
            cc = load_creative_constraint(name)
    else:
        # Auto-detect type
        lc = load_logistical_constraint(name)
        if not lc:
            cc = load_creative_constraint(name)

    print_banner()
    if lc:
        is_active = prof and prof.active_logistical_constraint == lc.name
        display_logistical_detail(lc, is_active=is_active)
    elif cc:
        is_active = prof and prof.active_creative_constraint == cc.name
        display_creative_detail(cc, is_active=is_active)
    else:
        print_error(f"Constraint set '{name}' not found.")
        raise typer.Exit(code=1)


@constraints_app.command("edit")
def edit_constraint(
    name: str = typer.Argument(..., help="Slug name of the constraint set to edit"),
    c_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Constraint type: 'logistical' or 'creative'"
    ),
) -> None:
    """Interactively edit fields of an existing constraint set."""
    seed_default_constraints()
    lc = None
    cc = None

    if c_type:
        clean_type = c_type.strip().lower()
        if clean_type == "logistical":
            lc = load_logistical_constraint(name)
        elif clean_type == "creative":
            cc = load_creative_constraint(name)
    else:
        lc = load_logistical_constraint(name)
        if not lc:
            cc = load_creative_constraint(name)

    print_banner()
    if lc:
        console.print(f"[bold cyan]✏ Editing Logistical Constraint Set: {lc.name}[/bold cyan]\n")
        new_desc = Prompt.ask("Description", default=lc.description)
        new_locs_str = Prompt.ask("Locations (comma-separated)", default=", ".join(lc.locations))
        new_sub_str = Prompt.ask("Sub-Locations (comma-separated)", default=", ".join(lc.sub_locations))
        new_details = Prompt.ask("Location Details", default=lc.location_details)

        lc.description = new_desc
        lc.locations = [x.strip() for x in new_locs_str.split(",") if x.strip()]
        lc.sub_locations = [x.strip() for x in new_sub_str.split(",") if x.strip()]
        lc.location_details = new_details

        save_logistical_constraint(lc)
        print_success(f"Logistical Constraint Set '{lc.name}' updated!")
        display_logistical_detail(lc)

    elif cc:
        console.print(f"[bold magenta]✏ Editing Creative Constraint Set: {cc.name}[/bold magenta]\n")
        new_desc = Prompt.ask("Description", default=cc.description)
        new_phil = Prompt.ask("Core Philosophy", default=cc.core_philosophy)
        new_econ = Prompt.ask("Scene Economy", default=cc.scene_economy)
        new_prog = Prompt.ask("Progression & Climax", default=cc.progression_and_climax)
        new_vis = Prompt.ask("Visuals & Post", default=cc.visuals_and_post)

        cc.description = new_desc
        cc.core_philosophy = new_phil
        cc.scene_economy = new_econ
        cc.progression_and_climax = new_prog
        cc.visuals_and_post = new_vis

        save_creative_constraint(cc)
        print_success(f"Creative Constraint Set '{cc.name}' updated!")
        display_creative_detail(cc)
    else:
        print_error(f"Constraint set '{name}' not found.")
        raise typer.Exit(code=1)


@constraints_app.command("delete")
def delete_constraint(
    name: str = typer.Argument(..., help="Slug name of the constraint set to delete"),
    c_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Constraint type: 'logistical' or 'creative'"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation prompt"),
) -> None:
    """Delete a constraint set by name."""
    lc = load_logistical_constraint(name) if (not c_type or c_type.lower() == "logistical") else None
    cc = load_creative_constraint(name) if (not c_type or c_type.lower() == "creative") else None

    if not lc and not cc and not c_type:
        # Fallback search if c_type was specified as creative or auto-search
        cc = load_creative_constraint(name)

    if not lc and not cc:
        print_error(f"Constraint set '{name}' not found.")
        raise typer.Exit(code=1)

    target_type = "logistical" if lc else "creative"

    if not force:
        if not Confirm.ask(f"Are you sure you want to delete the {target_type} set '{name}'?"):
            print_warning("Deletion cancelled.")
            return

    prof = load_profile()
    if target_type == "logistical":
        deleted = delete_logistical_constraint(name)
        if prof and prof.active_logistical_constraint == name:
            prof.active_logistical_constraint = None
            save_profile(prof)
    else:
        deleted = delete_creative_constraint(name)
        if prof and prof.active_creative_constraint == name:
            prof.active_creative_constraint = None
            save_profile(prof)

    if deleted:
        print_success(f"Successfully deleted {target_type} constraint set '{name}'.")
    else:
        print_error(f"Failed to delete {target_type} constraint set '{name}'.")


@constraints_app.command("set-active")
def set_active_constraints(
    logistical: Optional[str] = typer.Option(None, "--logistical", "-l", help="Name of logistical set to activate"),
    creative: Optional[str] = typer.Option(None, "--creative", "-c", help="Name of creative set to activate"),
) -> None:
    """Set which Logistical and/or Creative Constraint Sets are active for generation."""
    seed_default_constraints()
    prof = load_profile()

    if not prof:
        print_error("No global team profile found. Run '48hfp config setup' first.")
        raise typer.Exit(code=1)

    if not logistical and not creative:
        print_warning("No constraint set specified. Provide --logistical and/or --creative options.")
        console.print("Example: [bold cyan]48hfp constraints set-active --logistical interior_indie_crew --creative a24_slow_burn[/bold cyan]")
        raise typer.Exit(code=1)

    print_banner()

    if logistical:
        lc = load_logistical_constraint(logistical)
        if not lc:
            print_error(f"Logistical constraint set '{logistical}' not found.")
            raise typer.Exit(code=1)
        prof.active_logistical_constraint = lc.name
        print_success(f"Active Logistical Constraint Set updated to: [bold cyan]{lc.name}[/bold cyan]")

    if creative:
        cc = load_creative_constraint(creative)
        if not cc:
            print_error(f"Creative constraint set '{creative}' not found.")
            raise typer.Exit(code=1)
        prof.active_creative_constraint = cc.name
        print_success(f"Active Creative Constraint Set updated to: [bold magenta]{cc.name}[/bold magenta]")

    save_profile(prof)
    console.print()
    show_active()


@constraints_app.command("show-active")
def show_active() -> None:
    """Display currently primed active Logistical and Creative constraint sets."""
    seed_default_constraints()
    prof = load_profile()

    print_banner()

    active_log_name = prof.active_logistical_constraint if prof else None
    active_cre_name = prof.active_creative_constraint if prof else None

    lc = load_logistical_constraint(active_log_name) if active_log_name else None
    cc = load_creative_constraint(active_cre_name) if active_cre_name else None

    log_status = f"[bold cyan]{lc.name}[/bold cyan]" if lc else "[yellow]None selected[/yellow]"
    cre_status = f"[bold magenta]{cc.name}[/bold magenta]" if cc else "[yellow]None selected[/yellow]"

    content = (
        f"[bold white]Primed Generation Context[/bold white]\n\n"
        f"🚚 Active Logistical Set: {log_status}\n"
        f"🎨 Active Creative Set: {cre_status}\n"
    )

    print_panel(content=content, title="⚡ Primed Active Constraint Sets", border_style="green")

    if lc:
        display_logistical_detail(lc, is_active=True)
    if cc:
        display_creative_detail(cc, is_active=True)
