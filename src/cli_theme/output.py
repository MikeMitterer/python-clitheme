"""Ausgabe mit rich: Stile je Rolle, Abstände und Helfer für Überschrift, Zeile und Hinweis."""

import os
import shutil
import sys
from types import TracebackType
from typing import Self, TextIO

from rich.console import Console
from rich.text import Text

from cli_theme.theme import Theme, ThemeError, fallback_theme, load_theme, theme_path

# Annahme, wenn das Terminal seine Breite nicht nennt.
FALLBACK_COLUMNS = 100
# Schmaler darf die Wertspalte nicht werden; sonst steht der Wert unter seiner Bezeichnung.
MIN_VALUE_WIDTH = 20


def current_theme() -> Theme:
    """Gewähltes Theme für die Ausgabe; scheitert nie an der Konfiguration.

    Ist die Datei ungültig, ein Link oder CLI_THEME ungültig, gibt es keine Farben und die
    Abstände der classic-Vorlage. Den Grund nennt load_theme bzw. cli-theme show.
    """
    try:
        return load_theme()
    except (ThemeError, OSError):
        try:
            path = theme_path()
        except ThemeError:
            path = None
        return fallback_theme(path)


def rich_style(value: str) -> str:
    """Farbangabe des Themes als rich-Stil: bold+11 → bold color(11), 33 → color(33)."""
    effect, _, number = value.rpartition("+") if "+" in value else ("", "", value)
    if not number.isdigit():
        return value
    return f"{effect} color({number})".strip()


def styles(theme: Theme | None = None) -> dict[str, str]:
    """rich-Stil je Rolle; leer heißt Terminalfarbe."""
    theme = theme or current_theme()
    return {role: rich_style(value) for role, value in theme.colors.items()}


def plain_requested() -> bool:
    """NO_COLOR (auch leer) oder TERM=dumb verlangen Ausgabe ganz ohne Escape-Codes."""
    return "NO_COLOR" in os.environ or os.environ.get("TERM") == "dumb"


def is_terminal(stream: TextIO) -> bool:
    """Geht stream an ein Terminal?"""
    return bool(getattr(stream, "isatty", lambda: False)())


def output_width(stream: TextIO, theme: Theme) -> int | None:
    """Zeilenbreite im Terminal: dessen Breite, höchstens WIDTH (0 = ganze Breite);
    in Pipes und Dateien None, dort bleibt jede Zeile ungebrochen."""
    if not is_terminal(stream):
        return None
    limit = theme.spacing["width"]
    columns = shutil.get_terminal_size((limit or FALLBACK_COLUMNS, 24)).columns
    return min(columns, limit) if limit else columns


def console_for(stream: TextIO) -> Console:
    """Konsole für stream; ohne Terminal, mit NO_COLOR oder TERM=dumb ohne Farben."""
    terminal = is_terminal(stream)
    return Console(
        file=stream,
        force_terminal=terminal,
        highlight=False,
        soft_wrap=True,
        emoji=False,
        markup=False,
        color_system=None if plain_requested() or not terminal else "auto",
    )


class Output:
    """Schreibt Überschriften, zweispaltige Zeilen und Hinweise nach dem Theme.

    Vor jeder Überschrift außer der ersten stehen SPACE Leerzeilen. finish oder das Ende
    eines with-Blocks schließt mit einer Leerzeile auf jedem Strom ab, der Ausgabe bekam;
    was nicht über Output geht, etwa ein Befehl zum Kopieren mit print, zählt nicht.
    """

    def __init__(
        self,
        stream: TextIO | None = None,
        error_stream: TextIO | None = None,
        theme: Theme | None = None,
    ) -> None:
        self.stream = sys.stdout if stream is None else stream
        self.error_stream = sys.stderr if error_stream is None else error_stream
        self.theme = theme or current_theme()
        self.styles = styles(self.theme)
        self.started = False
        # Ströme mit Ausgabe seit dem letzten finish, in der Reihenfolge der ersten Ausgabe.
        self.written: list[TextIO] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.finish()

    def finish(self) -> None:
        """Schließt die Ausgabe ab: genau eine Leerzeile auf jedem Strom, der seit dem letzten
        finish Ausgabe bekam; ohne Ausgabe nichts."""
        for stream in self.written:
            stream.write("\n")
            stream.flush()
        self.written.clear()

    def spacing(self, name: str) -> int:
        """Abstand aus dem Theme, etwa i_row oder w_key."""
        return self.theme.spacing[name]

    def indent(self, name: str) -> str:
        """Einrückung aus dem Theme als Leerzeichen (i_head, i_row, i_hint)."""
        return " " * self.spacing(name)

    def write(
        self, text: Text, stream: TextIO | None = None, hang: int = 0, wrap: bool = True
    ) -> None:
        """Gibt eine Zeile aus; im Terminal auf die Ausgabebreite umbrochen.

        hang: Zahl der Zeichen am Anfang, die nur in der ersten Zeile stehen (Einzug und
        Bezeichnung); Folgezeilen beginnen in dieser Spalte. Bleiben daneben weniger als
        MIN_VALUE_WIDTH Zeichen, steht der Kopf allein und der Text darunter mit I_ROW.
        wrap=False: nie umbrechen, auch wenn die Zeile breiter ist als das Terminal; für
        Befehle und Pfade zum Kopieren. Farben und der Abschluss durch finish gelten weiter.
        """
        target = stream or self.stream
        if not any(target is seen for seen in self.written):
            self.written.append(target)
        console = console_for(target)
        width = output_width(target, self.theme)
        if not wrap or width is None or text.cell_len <= width:
            console.print(text, crop=False, overflow="ignore")
            return
        head, rest = text[:hang], text[hang:]
        if width - hang < MIN_VALUE_WIDTH:
            if head.plain.strip():
                head.rstrip()
                head.truncate(width, overflow="ellipsis")
                console.print(head, crop=False, overflow="ignore")
            hang = min(self.spacing("i_row"), width // 3)
            head = Text(" " * hang)
        for index, line in enumerate(rest.wrap(console, width - hang)):
            line.rstrip()
            console.print((head if index == 0 else Text(" " * hang)) + line, crop=False)

    def head(self, title: str) -> None:
        """Überschrift einer Gruppe, eingerückt um I_HEAD, in der Rolle head."""
        if self.started:
            self.stream.write("\n" * self.spacing("space"))
        self.started = True
        indent = self.indent("i_head")
        self.write(Text(indent) + Text(title, style=self.styles["head"]), hang=len(indent))

    def row(self, label: str | Text, value: object) -> None:
        """Bezeichnung (Rolle key) und Wert (Rolle val) in festen Spalten.

        Ist die Bezeichnung länger als W_KEY, steht der Wert in der nächsten Zeile.
        """
        self.started = True
        indent = self.indent("i_row")
        label_text = label if isinstance(label, Text) else Text(label, style=self.styles["key"])
        value_text = (
            value if isinstance(value, Text) else Text(str(value), style=self.styles["val"])
        )
        width = self.spacing("w_key") + self.spacing("gap")
        column = len(indent) + width
        if label_text.cell_len <= self.spacing("w_key"):
            padding = Text(" " * (width - label_text.cell_len))
            self.write(Text(indent) + label_text + padding + value_text, hang=column)
        else:
            self.write(Text(indent) + label_text, hang=len(indent))
            self.write(Text(" " * column) + value_text, hang=column)

    def hint(self, value: str) -> None:
        """Hinweistext, eingerückt um I_HINT, in der Rolle hint, Zeile für Zeile."""
        self.started = True
        indent = self.indent("i_hint")
        for line in value.splitlines():
            self.write(Text(indent) + Text(line, style=self.styles["hint"]), hang=len(indent))

    def error(self, message: str) -> None:
        """Fehlermeldung in der Rolle err auf den Fehlerstrom."""
        self.write(Text(message, style=self.styles["err"]), self.error_stream)
