"""CLI commands for team configuration & global state management."""

from pathlib import Path
from typing import Dict, List, Optional
import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from studio.models.profile import TeamProfile
from studio.utils.profile_store import (
    get_profile_path,
    load_profile,
    profile_exists,
    save_profile,
)
from studio.utils.ui import (
    display_profile_table,
    print_banner,
    print_error,
    print_panel,
    print_success,
    print_warning,
)

config_app = typer.Typer(
    name="config",
    help="Manage global team configuration, roles, and profile settings.",
    no_args_is_help=False,
)
console = Console()

DEFAULT_ROLE_CATEGORIES = [
    "Producer",
    "Director",
    "Director of Photography (DP)",
    "Assistant Director (AD)",
    "Sound Operator",
    "Production Designer",
    "Hair & Makeup Artist",
    "Grip / Gaffer",
    "Actors / Talent",
]


@config_app.callback(invoke_without_command=True)
def config_default(ctx: typer.Context) -> None:
    """Default action for '48hfp config': display profile if it exists, or run setup."""
    if ctx.invoked_subcommand is None:
        if profile_exists():
            show_profile()
        else:
            print_warning("No team configuration found at ~/.48hfp_profile.yaml")
            if Confirm.ask("Would you like to set up your team configuration now?"):
                setup_config()


@config_app.command("setup")
def setup_config(
    team_name: Optional[str] = typer.Option(None, "--team-name", "-t", help="Production Team Name"),
    admin_username: Optional[str] = typer.Option(None, "--admin", "-a", help="Team Admin Username"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Team Location (City, Country)"),
    custom_details: Optional[str] = typer.Option(None, "--custom-details", "-c", help="Custom team details/notes"),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Run setup non-interactively with provided flags"
    ),
) -> None:
    """Interactive onboarding wizard to configure production team metadata and roles."""
    print_banner()
    console.print("[bold cyan]🚀 Team Profile & Configuration Onboarding[/bold cyan]\n")

    existing_profile = load_profile()
    if existing_profile and not non_interactive:
        print_warning("Existing team profile found!")
        display_profile_table(
            team_name=existing_profile.team_name,
            admin_username=existing_profile.admin_username,
            location=existing_profile.location,
            roles=existing_profile.roles,
            custom_details=existing_profile.custom_details,
            updated_at=existing_profile.updated_at,
        )
        if not Confirm.ask("\nDo you want to overwrite this profile?"):
            print_success("Setup cancelled. Existing profile preserved.")
            return

    # Non-interactive fallback or defaults
    if non_interactive:
        final_team_name = team_name or (existing_profile.team_name if existing_profile else "Default Team")
        final_admin = admin_username or (existing_profile.admin_username if existing_profile else "admin")
        final_location = location or (existing_profile.location if existing_profile else "Unknown City")
        final_custom = custom_details if custom_details is not None else (existing_profile.custom_details if existing_profile else "")
        roles_dict = existing_profile.roles if existing_profile else {
            "Producer": ["Admin"],
            "Director": ["Admin"],
            "DP": [],
            "Actors": [],
        }
    else:
        default_team = existing_profile.team_name if existing_profile else "48HFP Filmmakers"
        default_admin = existing_profile.admin_username if existing_profile else "Producer"
        default_loc = existing_profile.location if existing_profile else "Los Angeles, CA"
        default_custom = existing_profile.custom_details if existing_profile else ""

        final_team_name = team_name or Prompt.ask("Production Team Name", default=default_team)
        final_admin = admin_username or Prompt.ask("Team Admin Username", default=default_admin)
        final_location = location or Prompt.ask("Team Location (City, Country)", default=default_loc)

        # Onboard roles
        console.print("\n[bold yellow]🎭 Onboarding Team Roles & Roster[/bold yellow]")
        console.print("[dim]Enter member names separated by commas (or press Enter to skip).[/dim]\n")

        roles_dict: Dict[str, List[str]] = {}
        for role in DEFAULT_ROLE_CATEGORIES:
            existing_members = existing_profile.roles.get(role, []) if existing_profile else []
            default_str = ", ".join(existing_members)
            ans = Prompt.ask(f"Members for [bold green]{role}[/bold green]", default=default_str)
            if ans.strip():
                members = [m.strip() for m in ans.split(",") if m.strip()]
                roles_dict[role] = members
            else:
                roles_dict[role] = []

        # Allow custom roles
        if Confirm.ask("\nWould you like to add any additional custom roles?"):
            while True:
                custom_role = Prompt.ask("Custom Role Title (or leave blank to finish)")
                if not custom_role.strip():
                    break
                members_ans = Prompt.ask(f"Members assigned to [bold green]{custom_role}[/bold green]")
                members_list = [m.strip() for m in members_ans.split(",") if m.strip()]
                roles_dict[custom_role.strip()] = members_list

        # Custom notes/logistics
        console.print("\n[bold yellow]📝 Custom Details & Logistics[/bold yellow]")
        console.print("[dim]E.g., vehicle access, dietary restrictions, available camera gear.[/dim]")
        final_custom = custom_details if custom_details is not None else Prompt.ask("Custom Notes", default=default_custom)

    profile = TeamProfile(
        team_name=final_team_name,
        admin_username=final_admin,
        location=final_location,
        roles=roles_dict,
        custom_details=final_custom,
    )

    saved_path = save_profile(profile)
    print_success(f"Team profile successfully saved to [bold white]{saved_path}[/bold white]\n")

    display_profile_table(
        team_name=profile.team_name,
        admin_username=profile.admin_username,
        location=profile.location,
        roles=profile.roles,
        custom_details=profile.custom_details,
        updated_at=profile.updated_at,
    )


@config_app.command("show")
def show_profile() -> None:
    """Display current global team configuration profile."""
    profile = load_profile()
    if not profile:
        print_error(f"No profile found at {get_profile_path()}")
        console.print("Run [bold cyan]48hfp config setup[/bold cyan] to create your profile.")
        raise typer.Exit(code=1)

    print_banner()
    display_profile_table(
        team_name=profile.team_name,
        admin_username=profile.admin_username,
        location=profile.location,
        roles=profile.roles,
        custom_details=profile.custom_details,
        updated_at=profile.updated_at,
    )


@config_app.command("path")
def print_path() -> None:
    """Output the path to the persistent configuration YAML file."""
    path = get_profile_path()
    status = "[green]Exists[/green]" if profile_exists() else "[yellow]Not Found[/yellow]"
    console.print(f"Profile Path: [bold white]{path}[/bold white] ({status})")
