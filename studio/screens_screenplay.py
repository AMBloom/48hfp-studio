"""Paginated TUI Screenplay Workspace and Fountain Syntax Highlighter for 48HFP-Studio."""

import math
import re
import textwrap
from typing import List

from rich.highlighter import RegexHighlighter
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Label, LoadingIndicator, Static


class FountainHighlighter(RegexHighlighter):
    """Rich RegexHighlighter for standard Fountain screenplay syntax."""

    base_style = "fountain."
    highlights = [
        r"^(?P<heading>(?:INT|EXT|EST|INT\./EXT|EXT\./INT|INT/EXT|EXT/INT)[\.\s\b][^\n]*)$",
        r"^(?P<transition>[A-Z ]+TO:)$",
        r"^(?P<parenthetical>\([^\)]+\))$",
        r"^(?P<character>[A-Z0-9 '\-\.]{2,}(?:\s*\([^\)]+\))?)$",
    ]


def highlight_fountain_lines(lines: List[str]) -> Text:
    """Helper function converting list of Fountain script lines into styled Rich Text."""
    text = Text()
    in_dialogue = False

    # Regex patterns for screenplay elements
    heading_re = re.compile(
        r"^(?:INT|EXT|EST|INT\./EXT|EXT\./INT|INT/EXT|EXT/INT)[\.\s].*$",
        re.IGNORECASE,
    )
    transition_re = re.compile(r"^[A-Z ]+TO:$")
    parenthetical_re = re.compile(r"^\s*\([^\)]+\)\s*$")
    character_re = re.compile(r"^\s*[A-Z0-9 '\-\.]{2,}(?:\s*\([^\)]+\))?\s*$")
    boneyard_re = re.compile(r"^/\*.*\*/$")
    section_re = re.compile(r"^#+.*$")
    page_break_re = re.compile(r"^={3,}\s*$")

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            in_dialogue = False
            text.append("\n")
            continue

        if page_break_re.match(stripped):
            in_dialogue = False
            text.append(line, style="dim cyan")
        elif heading_re.match(stripped):
            in_dialogue = False
            text.append(line, style="bold cyan")
        elif transition_re.match(stripped):
            in_dialogue = False
            text.append(line, style="bold white")
        elif parenthetical_re.match(stripped):
            in_dialogue = True
            text.append(line, style="italic magenta")
        elif section_re.match(stripped):
            in_dialogue = False
            text.append(line, style="bold yellow")
        elif boneyard_re.match(stripped):
            in_dialogue = False
            text.append(line, style="dim green")
        elif character_re.match(stripped) and not stripped.endswith("."):
            in_dialogue = True
            text.append(line, style="bold yellow")
        else:
            if in_dialogue:
                text.append(line, style="bold green")
            else:
                text.append(line, style="bright_white")

        if i < len(lines) - 1:
            text.append("\n")

    return text


class ScreenplayWorkspace(Static):
    """Paginated Screenplay TUI View featuring a portrait paper page container (~76 chars max width)."""

    PAGE_WIDTH = 68
    LINES_PER_PAGE = 52

    fountain_text: reactive[str] = reactive("")
    current_page: reactive[int] = reactive(1)
    is_generating: reactive[bool] = reactive(False)
    is_generating_shotlist: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    ScreenplayWorkspace {
        width: 1fr;
        height: 100%;
        background: $background;
        layout: vertical;
        padding: 1;
    }

    #screenplay-toolbar {
        height: 3;
        width: 100%;
        background: $surface;
        border-bottom: solid $accent;
        padding: 0 1;
        align: center middle;
    }

    #screenplay-toolbar Button {
        margin: 0 1;
    }

    #page_indicator {
        color: $text;
        text-style: bold;
        padding: 0 2;
        content-align: center middle;
    }

    #screenplay-empty-container {
        width: 100%;
        height: 1fr;
        align: center middle;
        padding: 4;
        background: $surface-darken-1;
        border: heavy $accent;
    }

    #screenplay-empty-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        content-align: center middle;
    }

    #screenplay-empty-desc {
        color: $text-muted;
        margin-bottom: 2;
        content-align: center middle;
        text-align: center;
    }

    #btn_empty_generate_screenplay {
        min-width: 44;
    }

    #page-scroll {
        width: 100%;
        height: 1fr;
        align: center top;
        padding-top: 1;
    }

    #page-paper {
        width: 76;
        max-width: 80;
        min-height: 52;
        background: $surface-darken-1;
        color: $text;
        border: heavy $accent;
        padding: 2 4;
        margin: 0;
    }

    #screenplay-loading {
        height: 3;
        margin-top: 4;
        content-align: center middle;
    }

    #script-content {
        width: 100%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="screenplay-toolbar"):
            yield Button("← Back to Treatment [1]", id="btn_back_to_treatment", variant="default")
            yield Button("◀ Page Up", id="btn_page_up", variant="primary")
            yield Label("Page 1 of 1", id="page_indicator")
            yield Button("Page Down ▶", id="btn_page_down", variant="primary")
            yield Button("🎥 Generate Shot List [3]", id="btn_generate_shotlist", variant="success")

        with Vertical(id="screenplay-empty-container"):
            yield Label("📜 [bold cyan]No Screenplay Generated Yet[/bold cyan]", id="screenplay-empty-title")
            yield Label(
                "Transform your active film treatment into a complete Fountain-formatted screenplay.",
                id="screenplay-empty-desc",
            )
            yield Button(
                "🎬 Generate Screenplay from Active Treatment",
                id="btn_empty_generate_screenplay",
                variant="success",
            )

        with VerticalScroll(id="page-scroll"):
            yield LoadingIndicator(id="screenplay-loading")
            with Container(id="page-paper"):
                yield Static(id="script-content")

    def on_mount(self) -> None:
        self.apply_view_state()
        self.update_page()

    def watch_fountain_text(self, new_text: str) -> None:
        self.current_page = 1
        self.apply_view_state()
        self.update_page()

    def watch_current_page(self, new_page: int) -> None:
        self.update_page()

    def watch_is_generating(self, is_gen: bool) -> None:
        self.apply_view_state()

    def watch_is_generating_shotlist(self, is_gen: bool) -> None:
        try:
            btn = self.query_one("#btn_generate_shotlist", Button)
            if is_gen:
                btn.label = "⏳ Generating..."
                btn.disabled = True
            else:
                btn.label = "🎥 Generate Shot List [3]"
                btn.disabled = False
        except Exception:
            pass

    def apply_view_state(self) -> None:
        try:
            loader = self.query_one("#screenplay-loading", LoadingIndicator)
            paper = self.query_one("#page-paper", Container)
            empty_box = self.query_one("#screenplay-empty-container", Vertical)
            toolbar = self.query_one("#screenplay-toolbar", Horizontal)
            page_scroll = self.query_one("#page-scroll", VerticalScroll)
            btn_empty = self.query_one("#btn_empty_generate_screenplay", Button)

            if self.is_generating:
                empty_box.display = False
                page_scroll.display = True
                toolbar.display = True
                loader.display = True
                paper.display = False
                btn_empty.disabled = True
                btn_empty.label = "⏳ Generating Screenplay..."
            else:
                loader.display = False
                btn_empty.disabled = False
                btn_empty.label = "🎬 Generate Screenplay from Active Treatment"
                toolbar.display = True

                if not self.fountain_text or not self.fountain_text.strip():
                    empty_box.display = True
                    page_scroll.display = False
                else:
                    empty_box.display = False
                    page_scroll.display = True
                    paper.display = True
        except Exception:
            pass

    def _paginate_fountain(self) -> List[List[str]]:
        """Split screenplay text into visual-wrapped, page-budgeted chunks."""
        if not self.fountain_text or not self.fountain_text.strip():
            return [["(Empty Screenplay)"]]

        pages: List[List[str]] = []
        current_page_lines: List[str] = []
        raw_lines = self.fountain_text.splitlines()

        for line in raw_lines:
            stripped = line.strip()

            # Handle explicit Fountain page break
            if re.match(r"^={3,}\s*$", stripped):
                if current_page_lines:
                    pages.append(current_page_lines)
                    current_page_lines = []
                continue

            # Compute visual wrapped lines
            if not stripped:
                wrapped = [""]
            elif len(line) <= self.PAGE_WIDTH:
                wrapped = [line]
            else:
                wrapped = textwrap.wrap(line, width=self.PAGE_WIDTH, replace_whitespace=False)
                if not wrapped:
                    wrapped = [line]

            # If adding these wrapped lines exceeds the page budget, push to next page
            if len(current_page_lines) + len(wrapped) > self.LINES_PER_PAGE and current_page_lines:
                pages.append(current_page_lines)
                current_page_lines = []

            current_page_lines.extend(wrapped)

        if current_page_lines:
            pages.append(current_page_lines)

        return pages if pages else [["(Empty Screenplay)"]]

    @property
    def total_pages(self) -> int:
        pages = self._paginate_fountain()
        return max(1, len(pages))

    def update_page(self) -> None:
        try:
            content_widget = self.query_one("#script-content", Static)
            indicator = self.query_one("#page_indicator", Label)
            btn_up = self.query_one("#btn_page_up", Button)
            btn_down = self.query_one("#btn_page_down", Button)
        except Exception:
            return

        pages = self._paginate_fountain()
        tot_pages = max(1, len(pages))
        page = max(1, min(self.current_page, tot_pages))

        page_lines = pages[page - 1]
        styled_text = highlight_fountain_lines(page_lines)
        content_widget.update(styled_text)

        indicator.update(f"Page {page} of {tot_pages}")
        btn_up.disabled = (page == 1)
        btn_down.disabled = (page == tot_pages)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_page_up":
            if self.current_page > 1:
                self.current_page -= 1
        elif event.button.id == "btn_page_down":
            if self.current_page < self.total_pages:
                self.current_page += 1
        elif event.button.id == "btn_back_to_treatment":
            if hasattr(self.app, "action_switch_to_treatment_view"):
                self.app.action_switch_to_treatment_view()
        elif event.button.id == "btn_generate_shotlist":
            if hasattr(self.app, "action_generate_shotlist"):
                self.app.action_generate_shotlist()
        elif event.button.id == "btn_empty_generate_screenplay":
            if hasattr(self.app, "action_generate_screenplay"):
                self.app.action_generate_screenplay()
