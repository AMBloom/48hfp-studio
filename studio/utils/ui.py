"""Rich terminal formatting helpers and UI elements."""

from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from studio.models.constraints import (
    DirectorialVision,
    IdeaSeed,
    LogisticalConstraint,
    ThematicFramework,
)
from studio.models.draw import FridayDraw

console = Console()


def print_banner() -> None:
    """Print the styled 48HFP-Studio terminal header banner."""
    banner_text = Text()
    banner_text.append(" 🎬 48HFP-Studio ", style="bold gold1 on blue")
    banner_text.append(" v3.0.0 ", style="bold white on navy_blue")
    banner_text.append("\n Terminal-Native AI Co-Pilot for Short Film Festivals", style="italic cyan")

    console.print()
    console.print(Panel(banner_text, border_style="cyan", expand=False))
    console.print()


def print_success(message: str) -> None:
    """Print a success notification."""
    console.print(f"[bold green]✔[/bold green] [green]{message}[/green]")


def print_warning(message: str) -> None:
    """Print a warning notification."""
    console.print(f"[bold yellow]⚠[/bold yellow] [yellow]{message}[/yellow]")


def print_error(message: str) -> None:
    """Print an error notification."""
    console.print(f"[bold red]✖[/bold red] [red]{message}[/red]")


def print_panel(content: str, title: str = "48HFP-Studio", border_style: str = "cyan") -> None:
    """Print a styled Rich panel."""
    console.print(Panel(content, title=f"[bold]{title}[/bold]", border_style=border_style))


def display_profile_table(
    team_name: str,
    admin_username: str,
    location: str,
    crew: Optional[Dict[str, List[str]]] = None,
    cast: Optional[List[Dict[str, str]]] = None,
    available_gear: Optional[List[str]] = None,
    custom_details: Optional[str] = None,
    updated_at: Optional[str] = None,
    roles: Optional[Dict[str, List[str]]] = None,
) -> None:
    """Display the team configuration profile in formatted Rich tables and panels."""
    final_crew = crew or roles or {}

    # Overview Table
    summary_table = Table(title="📋 Production Team Summary", border_style="cyan", show_header=True)
    summary_table.add_column("Property", style="bold bright_white", width=20)
    summary_table.add_column("Value", style="cyan")

    summary_table.add_row("Team Name", team_name)
    summary_table.add_row("Team Admin", admin_username)
    summary_table.add_row("Location", location)
    if updated_at:
        summary_table.add_row("Last Updated", updated_at)

    console.print(summary_table)

    # Crew Table
    roles_table = Table(title="🎥 Crew Roster & Roles", border_style="magenta", show_header=True)
    roles_table.add_column("Role", style="bold yellow", width=25)
    roles_table.add_column("Assigned Member(s)", style="white")

    if final_crew:
        for role_name, members in final_crew.items():
            members_str = ", ".join(members) if members else "[dim]Unassigned[/dim]"
            roles_table.add_row(role_name, members_str)
    else:
        roles_table.add_row("No roles assigned", "[dim]Use '48hfp config setup' to add roles[/dim]")

    console.print(roles_table)

    # Cast Table
    if cast:
        cast_table = Table(title="🎭 Cast Roster", border_style="green", show_header=True)
        cast_table.add_column("Actor / Char Name", style="bold white", width=20)
        cast_table.add_column("Age Range", style="yellow", width=15)
        cast_table.add_column("Gender", style="cyan", width=12)
        cast_table.add_column("Physicality / Appearance", style="white")

        for actor in cast:
            cast_table.add_row(
                actor.get("name", "Unknown"),
                actor.get("age_range", "N/A"),
                actor.get("gender", "N/A"),
                actor.get("physicality", "N/A"),
            )
        console.print(cast_table)

    # Available Gear Table/Panel
    if available_gear:
        gear_str = "\n".join([f"• {g}" for g in available_gear])
        console.print(
            Panel(
                gear_str,
                title="[bold cyan]🛠️ Available Gear & Equipment Catalog[/bold cyan]",
                border_style="cyan",
            )
        )

    # Custom Details Panel
    if custom_details and custom_details.strip():
        console.print(
            Panel(
                custom_details.strip(),
                title="[bold yellow]📝 Custom Team Notes & Logistics[/bold yellow]",
                border_style="yellow",
            )
        )
    else:
        console.print(
            Panel(
                "[dim]No custom notes provided.[/dim]",
                title="[bold yellow]📝 Custom Team Notes & Logistics[/bold yellow]",
                border_style="dim",
            )
        )


def display_constraints_table(
    logistical_sets: List[LogisticalConstraint],
    directorial_sets: List[DirectorialVision],
    thematic_sets: List[ThematicFramework],
    idea_sets: List[IdeaSeed],
    active_logistical: Optional[str] = None,
    active_directorial: Optional[str] = None,
    active_thematic: Optional[str] = None,
    active_idea: Optional[str] = None,
) -> None:
    """Display overview table of all available constraint sets with active badges."""
    table = Table(title="📦 Tri-Split Constraint Sets Library", border_style="cyan", show_header=True)
    table.add_column("Type", style="bold yellow", width=16)
    table.add_column("Name (Slug)", style="bold bright_white", width=24)
    table.add_column("Status", width=12, justify="center")
    table.add_column("Description", style="white")

    all_empty = not any([logistical_sets, directorial_sets, thematic_sets, idea_sets])
    if all_empty:
        table.add_row("-", "No sets found", "-", "[dim]No constraint sets available.[/dim]")
    else:
        for lc in logistical_sets:
            is_active = active_logistical == lc.name
            status_badge = "[bold black on green] ACTIVE [/bold black on green]" if is_active else "[dim]Inactive[/dim]"
            desc = lc.description[:60] + "..." if len(lc.description) > 60 else lc.description
            table.add_row("Logistical", f"[cyan]{lc.name}[/cyan]", status_badge, desc or "[dim]No description[/dim]")

        for dv in directorial_sets:
            is_active = active_directorial == dv.name
            status_badge = "[bold black on green] ACTIVE [/bold black on green]" if is_active else "[dim]Inactive[/dim]"
            desc = dv.description[:60] + "..." if len(dv.description) > 60 else dv.description
            table.add_row("Directorial Vision", f"[magenta]{dv.name}[/magenta]", status_badge, desc or "[dim]No description[/dim]")

        for tf in thematic_sets:
            is_active = active_thematic == tf.name
            status_badge = "[bold black on green] ACTIVE [/bold black on green]" if is_active else "[dim]Inactive[/dim]"
            desc = tf.description[:60] + "..." if len(tf.description) > 60 else tf.description
            table.add_row("Thematic Framework", f"[blue]{tf.name}[/blue]", status_badge, desc or "[dim]No description[/dim]")

        for ids in idea_sets:
            is_active = active_idea == ids.name
            status_badge = "[bold black on green] ACTIVE [/bold black on green]" if is_active else "[dim]Inactive[/dim]"
            desc = ids.description[:60] + "..." if len(ids.description) > 60 else ids.description
            table.add_row("Idea Seed", f"[green]{ids.name}[/green]", status_badge, desc or "[dim]No description[/dim]")

    console.print(table)


def display_logistical_detail(constraint: LogisticalConstraint, is_active: bool = False) -> None:
    """Display detailed breakdown panel for a Logistical Constraint Set."""
    status_header = " [bold black on green] ACTIVE SET [/bold black on green]" if is_active else ""
    title = f"🚚 Logistical Constraint Set: [bold cyan]{constraint.name}[/bold cyan]{status_header}"

    content = f"[bold white]Description:[/bold white] {constraint.description or 'None'}\n\n"
    content += f"[bold yellow]Locations:[/bold yellow] {', '.join(constraint.locations) if constraint.locations else 'None'}\n"
    content += f"[bold yellow]Sub-Locations:[/bold yellow] {', '.join(constraint.sub_locations) if constraint.sub_locations else 'None'}\n"
    content += f"[bold yellow]Location Details:[/bold yellow]\n{constraint.location_details or 'None'}\n\n"

    content += "[bold yellow]Other Characters:[/bold yellow]\n"
    if constraint.other_characters:
        for char in constraint.other_characters:
            content += f"  • [bold white]{char.name}[/bold white]: {char.actor_traits or 'No traits'} | Wardrobe: {char.wardrobe or 'N/A'}\n"
        content += "\n"
    else:
        content += "  [dim]None specified[/dim]\n\n"

    content += "[bold yellow]Available Set Dressing & Wardrobe:[/bold yellow]\n"
    dressing = constraint.available_set_dressing
    if dressing:
        for item in dressing:
            content += f"  • {item}\n"
    else:
        content += "  [dim]None specified[/dim]\n"

    content += f"\n[dim]Created: {constraint.created_at} | Updated: {constraint.updated_at}[/dim]"

    console.print(Panel(content, title=title, border_style="green" if is_active else "cyan"))


def display_directorial_detail(constraint: DirectorialVision, is_active: bool = False) -> None:
    """Display detailed breakdown panel for a Directorial Vision Set."""
    status_header = " [bold black on green] ACTIVE SET [/bold black on green]" if is_active else ""
    title = f"🎬 Directorial Vision: [bold magenta]{constraint.name}[/bold magenta]{status_header}"

    content = f"[bold white]Description:[/bold white] {constraint.description or 'None'}\n\n"
    content += f"[bold yellow]Visual Economy & Camera Movement:[/bold yellow]\n{constraint.visual_economy or 'None'}\n\n"
    content += f"[bold yellow]Lighting & Color Grading Intent:[/bold yellow]\n{constraint.lighting_color or 'None'}\n\n"
    content += f"[bold yellow]Audio Landscape & Music Intent:[/bold yellow]\n{constraint.audio_landscape or 'None'}\n\n"
    content += f"[dim]Created: {constraint.created_at} | Updated: {constraint.updated_at}[/dim]"

    console.print(Panel(content, title=title, border_style="green" if is_active else "magenta"))


def display_thematic_detail(constraint: ThematicFramework, is_active: bool = False) -> None:
    """Display detailed breakdown panel for a Thematic Framework Set."""
    status_header = " [bold black on green] ACTIVE SET [/bold black on green]" if is_active else ""
    title = f"🧠 Thematic Framework: [bold blue]{constraint.name}[/bold blue]{status_header}"

    content = f"[bold white]Description:[/bold white] {constraint.description or 'None'}\n\n"
    content += f"[bold yellow]Core Philosophy & Subtext:[/bold yellow]\n{constraint.core_philosophy or 'None'}\n\n"
    content += f"[bold yellow]Emotional Arc & Climax Dynamics:[/bold yellow]\n{constraint.emotional_arc or 'None'}\n\n"
    content += f"[bold yellow]World Rules & Atmospheric Logic:[/bold yellow]\n{constraint.world_rules or 'None'}\n\n"
    content += f"[dim]Created: {constraint.created_at} | Updated: {constraint.updated_at}[/dim]"

    console.print(Panel(content, title=title, border_style="green" if is_active else "blue"))


def display_idea_detail(constraint: IdeaSeed, is_active: bool = False) -> None:
    """Display detailed breakdown panel for an Idea Seed Set."""
    status_header = " [bold black on green] ACTIVE SET [/bold black on green]" if is_active else ""
    title = f"💡 Idea Seed: [bold green]{constraint.name}[/bold green]{status_header}"

    content = f"[bold white]Description:[/bold white] {constraint.description or 'None'}\n\n"
    content += f"[bold yellow]Inciting Incident / Initial Spark:[/bold yellow]\n{constraint.inciting_incident or 'None'}\n\n"
    content += f"[bold yellow]Complications & Midpoint Twists:[/bold yellow]\n{constraint.complications or 'None'}\n\n"
    content += f"[bold yellow]Ending Targets & Resolution Notes:[/bold yellow]\n{constraint.ending_targets or 'None'}\n\n"
    content += f"[dim]Created: {constraint.created_at} | Updated: {constraint.updated_at}[/dim]"

    console.print(Panel(content, title=title, border_style="green" if is_active else "yellow"))


def display_draw_table(draw: FridayDraw) -> None:
    """Display active Friday Draw parameters in formatted Rich table and panel."""
    table = Table(title="🎲 Friday Night Draw Kickoff Data", border_style="gold1", show_header=True)
    table.add_column("Constraint Category", style="bold bright_white", width=24)
    table.add_column("Draw Value", style="bold yellow")

    table.add_row("Primary Genre (Group 1)", draw.genre_1)
    table.add_row("Secondary Genre (Group 2)", draw.genre_2)
    table.add_row("Required Character Name", draw.character_name)
    table.add_row("Character Trait / Profession", draw.character_trait)
    table.add_row("Character Gender / Sex", draw.character_gender)
    table.add_row("Required Prop", draw.required_prop)
    table.add_row("Required Verbatim Line", f'"{draw.required_line}"')

    console.print(table)
    console.print(f"[dim]Recorded At: {draw.created_at}[/dim]\n")


def display_prompt_panel(prompt_text: str) -> None:
    """Display formatted panel preview for inspecting compiled LLM system prompts."""
    console.print(
        Panel(
            prompt_text,
            title="[bold gold1]⚡ Compiled System Prompt[/bold gold1]",
            border_style="gold1",
            expand=True,
        )
    )
