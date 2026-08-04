"""Rich terminal formatting helpers and UI elements."""

from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from studio.models.constraints import CreativeConstraint, LogisticalConstraint
from studio.models.draw import FridayDraw

console = Console()


def print_banner() -> None:
    """Print the styled 48HFP-Studio terminal header banner."""
    banner_text = Text()
    banner_text.append(" 🎬 48HFP-Studio ", style="bold gold1 on blue")
    banner_text.append(" v0.1.0 ", style="bold white on navy_blue")
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
    roles: Dict[str, List[str]],
    custom_details: Optional[str] = None,
    updated_at: Optional[str] = None,
) -> None:
    """Display the team configuration profile in formatted Rich tables and panels."""
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

    # Roles Roster Table
    roles_table = Table(title="🎭 Team Roster & Roles", border_style="magenta", show_header=True)
    roles_table.add_column("Role", style="bold yellow", width=25)
    roles_table.add_column("Assigned Member(s)", style="white")

    if roles:
        for role_name, members in roles.items():
            members_str = ", ".join(members) if members else "[dim]Unassigned[/dim]"
            roles_table.add_row(role_name, members_str)
    else:
        roles_table.add_row("No roles assigned", "[dim]Use '48hfp config setup' to add roles[/dim]")

    console.print(roles_table)

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
    creative_sets: List[CreativeConstraint],
    active_logistical: Optional[str] = None,
    active_creative: Optional[str] = None,
) -> None:
    """Display overview table of all available constraint sets with active badges."""
    table = Table(title="📦 Unified Constraint Sets Library", border_style="cyan", show_header=True)
    table.add_column("Type", style="bold yellow", width=12)
    table.add_column("Name (Slug)", style="bold bright_white", width=24)
    table.add_column("Status", width=12, justify="center")
    table.add_column("Description", style="white")

    if not logistical_sets and not creative_sets:
        table.add_row("-", "No sets found", "-", "[dim]No constraint sets available.[/dim]")
    else:
        for lc in logistical_sets:
            is_active = active_logistical == lc.name
            status_badge = "[bold black on green] ACTIVE [/bold black on green]" if is_active else "[dim]Inactive[/dim]"
            desc = lc.description[:60] + "..." if len(lc.description) > 60 else lc.description
            table.add_row("Logistical", f"[cyan]{lc.name}[/cyan]", status_badge, desc or "[dim]No description[/dim]")

        for cc in creative_sets:
            is_active = active_creative == cc.name
            status_badge = "[bold black on green] ACTIVE [/bold black on green]" if is_active else "[dim]Inactive[/dim]"
            desc = cc.description[:60] + "..." if len(cc.description) > 60 else cc.description
            table.add_row("Creative", f"[magenta]{cc.name}[/magenta]", status_badge, desc or "[dim]No description[/dim]")

    console.print(table)


def display_logistical_detail(constraint: LogisticalConstraint, is_active: bool = False) -> None:
    """Display detailed breakdown panel for a Logistical Constraint Set."""
    status_header = " [bold black on green] ACTIVE SET [/bold black on green]" if is_active else ""
    title = f"🚚 Logistical Constraint Set: [bold cyan]{constraint.name}[/bold cyan]{status_header}"

    content = f"[bold white]Description:[/bold white] {constraint.description or 'None'}\n\n"
    content += f"[bold yellow]Locations:[/bold yellow] {', '.join(constraint.locations) if constraint.locations else 'None'}\n"
    content += f"[bold yellow]Sub-Locations:[/bold yellow] {', '.join(constraint.sub_locations) if constraint.sub_locations else 'None'}\n"
    content += f"[bold yellow]Location Details:[/bold yellow]\n{constraint.location_details or 'None'}\n\n"

    content += "[bold yellow]Main Character Details:[/bold yellow]\n"
    if constraint.main_character_details:
        mc = constraint.main_character_details
        content += f"  • Name: [bold white]{mc.name}[/bold white]\n"
        content += f"    Traits: {mc.actor_traits or 'N/A'}\n"
        content += f"    Wardrobe: {mc.wardrobe or 'N/A'}\n"
        content += f"    Notes: {mc.notes or 'N/A'}\n\n"
    else:
        content += "  [dim]None specified[/dim]\n\n"

    content += "[bold yellow]Other Characters:[/bold yellow]\n"
    if constraint.other_characters:
        for char in constraint.other_characters:
            content += f"  • [bold white]{char.name}[/bold white]: {char.actor_traits or 'No traits'} | Wardrobe: {char.wardrobe or 'N/A'}\n"
        content += "\n"
    else:
        content += "  [dim]None specified[/dim]\n\n"

    content += "[bold yellow]Props & Dialogue Elements:[/bold yellow]\n"
    if constraint.props_and_dialogue:
        for item in constraint.props_and_dialogue:
            content += f"  • {item}\n"
    else:
        content += "  [dim]None specified[/dim]\n"

    content += f"\n[dim]Created: {constraint.created_at} | Updated: {constraint.updated_at}[/dim]"

    console.print(Panel(content, title=title, border_style="green" if is_active else "cyan"))


def display_creative_detail(constraint: CreativeConstraint, is_active: bool = False) -> None:
    """Display detailed breakdown panel for a Creative Constraint Set."""
    status_header = " [bold black on green] ACTIVE SET [/bold black on green]" if is_active else ""
    title = f"🎨 Creative Constraint Set: [bold magenta]{constraint.name}[/bold magenta]{status_header}"

    content = f"[bold white]Description:[/bold white] {constraint.description or 'None'}\n\n"
    content += "[bold yellow]Pre-Baked Story Scenarios:[/bold yellow]\n"
    if constraint.scenarios:
        for idx, sc in enumerate(constraint.scenarios, 1):
            content += f"  {idx}. {sc}\n"
        content += "\n"
    else:
        content += "  [dim]None specified[/dim]\n\n"

    content += f"[bold yellow]Core Philosophy & Motivation:[/bold yellow]\n{constraint.core_philosophy or 'None'}\n\n"
    content += f"[bold yellow]Scene Economy & Pacing:[/bold yellow]\n{constraint.scene_economy or 'None'}\n\n"
    content += f"[bold yellow]Progression & Climax Structure:[/bold yellow]\n{constraint.progression_and_climax or 'None'}\n\n"
    content += f"[bold yellow]Visuals & Post-Production Guidelines:[/bold yellow]\n{constraint.visuals_and_post or 'None'}\n\n"

    content += f"[dim]Created: {constraint.created_at} | Updated: {constraint.updated_at}[/dim]"

    console.print(Panel(content, title=title, border_style="green" if is_active else "magenta"))


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
            title="[bold gold1]⚡ Compiled System Prompt (Recency Effect Enforced)[/bold gold1]",
            border_style="gold1",
            expand=True,
        )
    )
