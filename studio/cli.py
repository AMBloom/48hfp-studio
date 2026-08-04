"""Main Typer CLI application for 48HFP-Studio."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from studio import __version__
from studio.config import config_app
from studio.constraints import constraints_app
from studio.draw import draw_app
from studio.inference import InferenceEngine, InferenceError
from studio.utils.draw_store import draw_exists, load_draw
from studio.utils.profile_store import get_profile_path, load_profile, profile_exists
from studio.utils.prompt_builder import PromptBuilder
from studio.utils.treatment_store import save_treatment_output
from studio.utils.ui import display_prompt_panel, print_banner, print_panel

app = typer.Typer(
    name="48hfp",
    help="48HFP-Studio: Terminal-native AI co-pilot for short film festival pre-production.",
    no_args_is_help=True,
    add_completion=False,
)

# Register subcommand groups
app.add_typer(config_app, name="config")
app.add_typer(constraints_app, name="constraints")
app.add_typer(constraints_app, name="constraint")
app.add_typer(draw_app, name="draw")

console = Console()


def version_callback(value: bool) -> None:
    """Callback for --version flag."""
    if value:
        console.print(
            f"[bold cyan]48HFP-Studio[/bold cyan] version [bold white]{__version__}[/bold white]"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """48HFP-Studio CLI root callback."""
    pass


@app.command("prompt")
def prompt_command() -> None:
    """Compile and preview the complete hierarchical system prompt."""
    print_banner()
    prompt_text = PromptBuilder.compile_system_prompt()
    display_prompt_panel(prompt_text)


@app.command("generate")
def generate_command(
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Gemini model name override (defaults to GEMINI_MODEL env var or gemini-3.6-flash).",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Custom directory path to save generated treatment Markdown file.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Compile and preview prompt without sending request to Gemini API.",
    ),
) -> None:
    """Generate a structured pre-production film treatment using Gemini AI."""
    print_banner()

    prompt_text = PromptBuilder.compile_system_prompt()

    if dry_run:
        console.print("[bold yellow]⚡ DRY RUN MODE ACTIVE[/bold yellow]")
        display_prompt_panel(prompt_text)
        console.print(
            "\n[bold green]✔ System prompt compiled successfully. No API call made.[/bold green]"
        )
        return

    try:
        with console.status(
            "[bold cyan]🎬 Generating 48HFP Film Treatment via Gemini AI co-pilot...[/bold cyan]",
            spinner="dots",
        ):
            treatment = InferenceEngine.generate_treatment(
                prompt=prompt_text,
                model_name=model,
            )

        saved_path = save_treatment_output(treatment, outputs_dir=output_dir)

        tl = treatment.title_and_logline
        chk = treatment.compliance_checklist

        line_chk = "✔" if chk.verbatim_line_verified else "✘"
        prop_chk = "✔" if chk.prop_usage_verified else "✘"
        char_chk = "✔" if chk.character_linkage_verified else "✘"
        time_chk = "✔" if chk.pacing_runtime_verified else "✘"

        print_panel(
            content=(
                f"[bold green]✨ Film Treatment Generated & Safe-Written Successfully![/bold green]\n\n"
                f"📄 [bold white]Output File:[/bold white] [cyan]{saved_path}[/cyan]\n\n"
                f"🎬 [bold white]Title:[/bold white] [bold yellow]{tl.title}[/bold yellow]\n"
                f"🎭 [bold white]Genre Blend:[/bold white] {tl.genre_blend}\n"
                f"💡 [bold white]Logline:[/bold white] {tl.logline}\n\n"
                f"[bold white]Festival Compliance Checklist:[/bold white]\n"
                f"  [{'green' if chk.verbatim_line_verified else 'red'}]{line_chk}[/{'green' if chk.verbatim_line_verified else 'red'}] Verbatim Dialogue Line\n"
                f"  [{'green' if chk.prop_usage_verified else 'red'}]{prop_chk}[/{'green' if chk.prop_usage_verified else 'red'}] Required Prop Usage\n"
                f"  [{'green' if chk.character_linkage_verified else 'red'}]{char_chk}[/{'green' if chk.character_linkage_verified else 'red'}] Character Name & Trait\n"
                f"  [{'green' if chk.pacing_runtime_verified else 'red'}]{time_chk}[/{'green' if chk.pacing_runtime_verified else 'red'}] Runtime Pacing (4-7 mins)\n\n"
                f"[dim]Run '48hfp generate' again anytime to produce a new versioned treatment without overwriting.[/dim]"
            ),
            title="🚀 Generation Complete",
            border_style="green",
        )

    except InferenceError as err:
        print_panel(
            content=f"[bold red]Inference Error:[/bold red]\n{err}",
            title="❌ Generation Failed",
            border_style="red",
        )
        raise typer.Exit(code=1)


@app.command("info")
def info() -> None:
    """Display system status, CLI version, global profile, active constraints, and Friday Draw readiness."""
    print_banner()

    p_path = get_profile_path()
    p_status = profile_exists()

    if p_status:
        prof = load_profile()
        team_str = prof.team_name if prof else "Configured"
        admin_str = prof.admin_username if prof else "Unknown"
        active_log = (
            prof.active_logistical_constraint
            if prof and prof.active_logistical_constraint
            else "[yellow]None[/yellow]"
        )
        active_cre = (
            prof.active_creative_constraint
            if prof and prof.active_creative_constraint
            else "[yellow]None[/yellow]"
        )

        profile_info = (
            f"[bold green]✔ Configured[/bold green]\n"
            f"Team: [bold white]{team_str}[/bold white] | Admin: [bold white]{admin_str}[/bold white]\n"
            f"Profile File: [dim]{p_path}[/dim]\n\n"
            f"[bold white]Primed Active Constraints:[/bold white]\n"
            f"🚚 Logistical: [cyan]{active_log}[/cyan]\n"
            f"🎨 Creative: [magenta]{active_cre}[/magenta]"
        )
    else:
        profile_info = (
            f"[bold yellow]⚠ Not Configured[/bold yellow]\n"
            f"Run [bold cyan]48hfp config setup[/bold cyan] to onboard your team details.\n"
            f"Expected File: [dim]{p_path}[/dim]"
        )

    # Friday Draw status
    d_status = draw_exists()
    if d_status:
        draw_obj = load_draw()
        g1 = draw_obj.genre_1 if draw_obj else "N/A"
        g2 = draw_obj.genre_2 if draw_obj else "N/A"
        char = draw_obj.character_name if draw_obj else "N/A"
        draw_info = (
            f"[bold green]✔ Recorded[/bold green]\n"
            f"Genres: [bold yellow]{g1}[/bold yellow] / [bold yellow]{g2}[/bold yellow] | Char: [bold white]{char}[/bold white]"
        )
    else:
        draw_info = (
            f"[bold yellow]⚠ Not Recorded[/bold yellow]\n"
            f"Run [bold cyan]48hfp draw wizard[/bold cyan] at kickoff to capture genres, character, prop, line."
        )

    print_panel(
        content=f"[bold white]Status Overview[/bold white]\n\n"
        f"Version: [cyan]{__version__}[/cyan]\n\n"
        f"Global Profile:\n{profile_info}\n\n"
        f"Friday Night Kickoff Draw:\n{draw_info}\n",
        title="🎬 System Information",
        border_style="cyan",
    )
