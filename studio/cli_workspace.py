"""CLI subcommands for project workspace initialization, switching, and status tracking."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from rich.prompt import Confirm, Prompt

from studio.models.profile import TeamProfile
from studio.quiz import QUIZ_QUESTIONS, QuizEngine
from studio.utils.constraint_store import (
    list_directorial_visions,
    list_idea_seeds,
    list_logistical_constraints,
    list_thematic_frameworks,
    seed_default_constraints,
)
from studio.utils.draw_store import draw_exists, load_draw
from studio.utils.global_state import (
    get_active_workspace,
    get_global_state_path,
    set_active_workspace,
)
from studio.utils.profile_store import load_profile, profile_exists, save_profile
from studio.utils.ui import print_banner, print_error, print_panel, print_success, print_warning

workspace_app = typer.Typer(
    name="workspace",
    help="Manage portable, named project workspaces for 48HFP short films.",
    no_args_is_help=False,
)
console = Console()


@workspace_app.callback(invoke_without_command=True)
def workspace_default(ctx: typer.Context) -> None:
    """Default action for '48hfp workspace': display current workspace status."""
    if ctx.invoked_subcommand is None:
        status_workspace()


@workspace_app.command("init")
def init_workspace(
    path: Path = typer.Argument(..., help="Name or directory path for the new project workspace"),
) -> None:
    """Initialize a new project workspace directory structure and set it as active."""
    print_banner()

    target_path = path.resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    # Create workspace subdirectory hierarchy
    (target_path / "constraints" / "logistical").mkdir(parents=True, exist_ok=True)
    (target_path / "constraints" / "directorial").mkdir(parents=True, exist_ok=True)
    (target_path / "constraints" / "thematic").mkdir(parents=True, exist_ok=True)
    (target_path / "constraints" / "ideas").mkdir(parents=True, exist_ok=True)
    (target_path / "projects").mkdir(parents=True, exist_ok=True)
    (target_path / "outputs").mkdir(parents=True, exist_ok=True)

    # Set active workspace in global state tracker
    set_active_workspace(target_path)

    # Seed starter constraints if workspace has none
    seed_default_constraints()

    print_success(f"Initialized new project workspace at [bold white]{target_path}[/bold white]\n")

    print_panel(
        content=(
            f"[bold white]Active Workspace:[/bold white] [cyan]{target_path}[/cyan]\n"
            f"[bold white]Project Name:[/bold white] [yellow]{target_path.name}[/yellow]\n\n"
            f"[bold white]Directory Structure Created:[/bold white]\n"
            f"  • [dim]{target_path}/profile.yaml[/dim]\n"
            f"  • [dim]{target_path}/draw.yaml[/dim]\n"
            f"  • [dim]{target_path}/constraints/[/dim] (logistical, directorial, thematic, ideas)\n"
            f"  • [dim]{target_path}/outputs/[/dim]\n\n"
            f"[dim]Run '48hfp config setup' or open '48hfp tui' to populate team profile.[/dim]"
        ),
        title="🎬 Workspace Initialized & Activated",
        border_style="green",
    )


@workspace_app.command("switch")
def switch_workspace(
    path: Path = typer.Argument(..., help="Path to existing project workspace directory"),
) -> None:
    """Switch the global active project workspace."""
    print_banner()

    target_path = path.resolve()
    if not target_path.exists() or not target_path.is_dir():
        print_error(f"Target workspace directory does not exist: [bold white]{target_path}[/bold white]")
        console.print("Run [bold cyan]48hfp workspace init <path>[/bold cyan] to create it first.")
        raise typer.Exit(code=1)

    set_active_workspace(target_path)
    print_success(f"Switched active workspace to [bold white]{target_path}[/bold white]\n")

    status_workspace()


@workspace_app.command("status")
def status_workspace() -> None:
    """Display currently active project workspace details and statistics."""
    active = get_active_workspace()
    state_file = get_global_state_path()

    if not active:
        print_panel(
            content=(
                f"[bold yellow]⚠ No Active Workspace Set[/bold yellow]\n\n"
                f"Global State Config: [dim]{state_file}[/dim]\n"
                f"Operating Mode: [cyan]Default (Current Working Directory / Legacy Fallback)[/cyan]\n\n"
                f"Run [bold cyan]48hfp workspace init <name_or_path>[/bold cyan] to create a project workspace,\n"
                f"or [bold cyan]48hfp workspace switch <path>[/bold cyan] to activate an existing one."
            ),
            title="📂 Workspace Status",
            border_style="yellow",
        )
        return

    # Gather workspace stats
    prof_status = "[green]Configured[/green]" if profile_exists() else "[yellow]Missing[/yellow]"
    p_obj = load_profile()
    team_name = p_obj.team_name if p_obj else "Unconfigured"

    d_status = "[green]Recorded[/green]" if draw_exists() else "[yellow]Missing[/yellow]"

    num_log = len(list_logistical_constraints())
    num_dir = len(list_directorial_visions())
    num_them = len(list_thematic_frameworks())
    num_ideas = len(list_idea_seeds())

    outputs_dir = active / "outputs"
    num_outputs = len(list(outputs_dir.glob("*.md"))) if outputs_dir.exists() else 0

    print_panel(
        content=(
            f"[bold white]Active Workspace:[/bold white] [bold cyan]{active}[/bold cyan]\n"
            f"[bold white]Project Name:[/bold white] [bold yellow]{active.name}[/bold yellow]\n"
            f"[bold white]Global State File:[/bold white] [dim]{state_file}[/dim]\n\n"
            f"[bold white]Project Components:[/bold white]\n"
            f"  • Team Profile: {prof_status} ({team_name})\n"
            f"  • Friday Draw: {d_status}\n"
            f"  • Constraint Sets: [cyan]{num_log}[/cyan] logistical, [magenta]{num_dir}[/magenta] directorial, [blue]{num_them}[/blue] thematic, [green]{num_ideas}[/green] ideas\n"
            f"  • Generated Treatments: [bold white]{num_outputs}[/bold white] files in outputs/"
        ),
        title="🎬 Active Project Workspace",
        border_style="cyan",
    )


@workspace_app.command("quiz")
def run_quiz() -> None:
    """Run the interactive Filmmaker Personality Quiz in the CLI."""
    print_banner()

    print_panel(
        content=(
            "[bold cyan]🔮 WELCOME TO THE FILMMAKER PERSONALITY QUIZ[/bold cyan]\n\n"
            "Answer 10 questions to discover your winning Director Archetype and\n"
            "activate tailored Directorial Vision & Thematic Framework constraints."
        ),
        title="🎬 Filmmaker Quiz",
        border_style="magenta",
    )

    answers = {}
    for idx, q in enumerate(QUIZ_QUESTIONS):
        console.print(
            f"\n[bold yellow]Question {idx + 1} of {len(QUIZ_QUESTIONS)}[/bold yellow] [dim]({q.category.upper()})[/dim]"
        )
        console.print(f"[bold white]{q.prompt}[/bold white]")

        for opt_idx, opt in enumerate(q.options):
            console.print(f"  [cyan]{opt_idx + 1}.[/cyan] {opt.text}")

        choice = Prompt.ask(
            "Select option",
            choices=[str(i + 1) for i in range(len(q.options))],
            default="1",
        )
        answers[q.id] = int(choice) - 1

    result = QuizEngine.calculate_result(answers)
    info = result.winner_info

    print_panel(
        content=(
            f"[bold green]🏆 WINNING ARCHETYPE: {info.director_name.upper()}[/bold green]\n"
            f"[italic]\"{info.title}\"[/italic]\n\n"
            f"💬 [bold white]Quote:[/bold white] \"{info.quote}\"\n\n"
            f"🎨 [bold white]Visual Economy:[/bold white] {info.visual_style}\n"
            f"🧠 [bold white]Thematic Focus:[/bold white] {info.thematic_core}"
        ),
        title="🎬 Quiz Results",
        border_style="green",
    )

    if Confirm.ask(
        f"Activate [bold yellow]{info.director_name}[/bold yellow] constraints in active profile?",
        default=True,
    ):
        profile = load_profile() or TeamProfile(
            team_name="Indie Crew",
            admin_username="director",
            location="Unknown",
        )
        profile.active_directorial_vision = result.winner_slug
        profile.active_thematic_framework = result.winner_slug
        save_profile(profile)

        print_success(
            f"Activated Directorial Vision & Thematic Framework constraints for [bold yellow]{info.director_name}[/bold yellow]!"
        )

