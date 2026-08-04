"""CLI commands and interactive wizard for Friday Night Draw kickoff parameters."""

from typing import Optional
import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from studio.models.draw import (
    GENRES_GROUP_1,
    GENRES_GROUP_2,
    FridayDraw,
    create_default_draw,
)
from studio.utils.draw_store import (
    delete_draw,
    draw_exists,
    get_draw_path,
    load_draw,
    save_draw,
)
from studio.utils.prompt_builder import PromptBuilder
from studio.utils.ui import (
    display_draw_table,
    display_prompt_panel,
    print_banner,
    print_error,
    print_panel,
    print_success,
    print_warning,
)

draw_app = typer.Typer(
    name="draw",
    help="Capture ephemeral Friday Night Draw kickoff parameters (Genre, Character, Prop, Line).",
    no_args_is_help=False,
)
console = Console()


def _select_genre_interactive(group_name: str, genre_list: list[str]) -> str:
    """Helper to display genre list options and handle user selection or fallback."""
    console.print(f"\n[bold yellow]🎲 Choose {group_name}[/bold yellow]")
    console.print("[dim]Select a number (1-15), type a genre name, or press Enter for random default:[/dim]")

    for idx, g in enumerate(genre_list, 1):
        console.print(f"  [cyan]{idx:2d}.[/cyan] {g}")

    ans = Prompt.ask(f"\nSelect {group_name}", default="")
    ans_clean = ans.strip()

    if not ans_clean:
        fallback = create_default_draw().genre_1 if "Group 1" in group_name else create_default_draw().genre_2
        console.print(f"[dim]No input provided. Auto-selected fallback: [bold cyan]{fallback}[/bold cyan][/dim]")
        return fallback

    # Check if user entered a number
    if ans_clean.isdigit():
        num = int(ans_clean)
        if 1 <= num <= len(genre_list):
            selected = genre_list[num - 1]
            console.print(f"Selected: [bold green]{selected}[/bold green]")
            return selected

    # Check if exact/case-insensitive match
    matched = next((g for g in genre_list if g.lower() == ans_clean.lower()), None)
    if matched:
        console.print(f"Selected: [bold green]{matched}[/bold green]")
        return matched

    print_warning(f"'{ans_clean}' not in strict {group_name} list. Auto-generating compliant choice from list.")
    fallback = create_default_draw().genre_1 if "Group 1" in group_name else create_default_draw().genre_2
    return fallback


@draw_app.callback(invoke_without_command=True)
def draw_default(ctx: typer.Context) -> None:
    """Default action for '48hfp draw': show current draw or launch wizard."""
    if ctx.invoked_subcommand is None:
        if draw_exists():
            show_draw()
        else:
            print_warning("No Friday Draw kickoff data recorded yet.")
            if Confirm.ask("Would you like to run the Friday Draw Wizard now?"):
                run_wizard()


@draw_app.command("wizard")
@draw_app.command("setup")
def run_wizard(
    genre1: Optional[str] = typer.Option(None, "--genre1", "-g1", help="Primary Genre from Group 1"),
    genre2: Optional[str] = typer.Option(None, "--genre2", "-g2", help="Secondary Genre from Group 2"),
    character_name: Optional[str] = typer.Option(None, "--character-name", "-cn", help="Required Character Name"),
    character_trait: Optional[str] = typer.Option(None, "--character-trait", "-ct", help="Required Character Trait / Profession"),
    character_gender: Optional[str] = typer.Option(None, "--character-gender", "-cg", help="Required Character Gender / Sex"),
    prop: Optional[str] = typer.Option(None, "--prop", "-p", help="Required Physical Prop"),
    line: Optional[str] = typer.Option(None, "--line", "-l", help="Required Verbatim Line of Dialogue"),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Run wizard non-interactively using provided flags or defaults"
    ),
) -> None:
    """Interactive kickoff wizard to record Friday Draw parameters."""
    print_banner()
    console.print("[bold gold1]🎲 Friday Night Draw Kickoff Wizard[/bold gold1]\n")

    existing_draw = load_draw()
    if existing_draw and not non_interactive:
        print_warning("Existing Friday Draw data found!")
        display_draw_table(existing_draw)
        if not Confirm.ask("Do you want to overwrite this kickoff draw?"):
            print_success("Wizard cancelled. Existing draw preserved.")
            return

    if non_interactive:
        draw_obj = create_default_draw(
            genre_1=genre1,
            genre_2=genre2,
            character_name=character_name,
            character_trait=character_trait,
            character_gender=character_gender,
            required_prop=prop,
            required_line=line,
        )
    else:
        # Genre 1 Selection
        if genre1:
            final_g1 = genre1
        else:
            final_g1 = _select_genre_interactive("Group 1 Genre", GENRES_GROUP_1)

        # Genre 2 Selection
        if genre2:
            final_g2 = genre2
        else:
            final_g2 = _select_genre_interactive("Group 2 Genre", GENRES_GROUP_2)

        console.print("\n[bold yellow]👤 Required Character Details[/bold yellow]")
        c_name_input = character_name or Prompt.ask("Character Name", default="")
        c_trait_input = character_trait or Prompt.ask("Character Trait / Profession", default="")
        c_gender_input = character_gender or Prompt.ask("Character Gender / Sex", default="")

        console.print("\n[bold yellow]📦 Required Prop & Verbatim Line[/bold yellow]")
        prop_input = prop or Prompt.ask("Required Physical Prop", default="")
        line_input = line or Prompt.ask("Required Verbatim Dialogue Line", default="")

        draw_obj = create_default_draw(
            genre_1=final_g1,
            genre_2=final_g2,
            character_name=c_name_input,
            character_trait=c_trait_input,
            character_gender=c_gender_input,
            required_prop=prop_input,
            required_line=line_input,
        )

    saved_path = save_draw(draw_obj)
    print_success(f"\nFriday Draw kickoff parameters saved to [bold white]{saved_path}[/bold white]\n")
    display_draw_table(draw_obj)


@draw_app.command("show")
def show_draw() -> None:
    """Display active Friday Draw parameters."""
    draw_obj = load_draw()
    if not draw_obj:
        print_error(f"No active Friday Draw data found at {get_draw_path()}")
        console.print("Run [bold cyan]48hfp draw wizard[/bold cyan] to record kickoff data.")
        raise typer.Exit(code=1)

    print_banner()
    display_draw_table(draw_obj)


@draw_app.command("reset")
def reset_draw(
    force: bool = typer.Option(False, "--force", "-f", help="Bypass confirmation prompt")
) -> None:
    """Clear and delete active Friday Draw parameters."""
    if not draw_exists():
        print_warning("No active Friday Draw data found to delete.")
        return

    if not force and not Confirm.ask("Are you sure you want to reset and delete active Friday Draw data?"):
        console.print("Reset cancelled.")
        return

    if delete_draw():
        print_success("Active Friday Draw data successfully deleted.")


@draw_app.command("prompt")
def preview_prompt() -> None:
    """Compile and display the full hierarchical system prompt with Recency Effect."""
    print_banner()
    prompt_text = PromptBuilder.compile_system_prompt()
    display_prompt_panel(prompt_text)
