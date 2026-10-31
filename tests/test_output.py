"""Ausgabehelfer: rich-Stile, Abstände, Umbruch auf WIDTH bzw. Terminalbreite, ohne Farben."""

import io
import re
from pathlib import Path

from cli_theme import Output, current_theme, parse_theme, rich_style, styles, template_text

ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


class Terminal(io.StringIO):
    """Ausgabe, die sich als Terminal ausgibt."""

    def isatty(self) -> bool:
        return True


def theme(**values: str):
    """classic-Theme mit ersetzten Einträgen, etwa WIDTH="40"."""
    text = template_text()
    for name, value in values.items():
        text = re.sub(rf"(?m)^{name}=.*$", f"{name}={value}", text)
    return parse_theme(text, Path("test.theme"))


def test_rich_style_translates_theme_values():
    """bold+11 → bold color(11), 33 → color(33); dim und leer bleiben."""
    assert rich_style("bold+11") == "bold color(11)"
    assert rich_style("dim+245") == "dim color(245)"
    assert rich_style("33") == "color(33)"
    assert rich_style("dim") == "dim"
    assert rich_style("") == ""
    assert styles(theme())["err"] == "bold color(196)"


def test_layout_in_pipe_follows_spacing_without_colors():
    """head, row und hint setzen I_HEAD, I_ROW, W_KEY, GAP, I_HINT und SPACE; keine Farben."""
    stream = io.StringIO()
    out = Output(stream, theme=theme(I_HEAD="1", I_ROW="3", I_HINT="5", W_KEY="6", GAP="2"))
    out.head("Group")
    out.row("key", "value")
    out.row("long-label", "value")
    out.hint("note")
    out.head("Next")
    assert stream.getvalue() == (
        " Group\n   key     value\n   long-label\n           value\n     note\n\n Next\n"
    )


def test_pipe_never_wraps():
    """In Pipes bleibt jede Zeile ganz, egal wie lang."""
    stream = io.StringIO()
    Output(stream, theme=theme(WIDTH="20")).hint("word " * 30)
    assert len(stream.getvalue().splitlines()) == 1


def test_terminal_wraps_at_width_below_terminal(monkeypatch):
    """Im Terminal bricht der Wert bei WIDTH um und beginnt in jeder Zeile in seiner Spalte."""
    monkeypatch.setenv("COLUMNS", "200")
    monkeypatch.setenv("NO_COLOR", "")
    stream = Terminal()
    Output(stream, theme=theme(WIDTH="60")).row("key", "word " * 30)
    lines = stream.getvalue().splitlines()
    assert len(lines) > 1
    assert all(len(line) <= 60 for line in lines), lines
    assert all(line.startswith(" " * 30) and line[30] != " " for line in lines[1:]), lines


def test_terminal_wraps_at_terminal_width_below_width(monkeypatch):
    """Ist das Terminal schmaler als WIDTH, gilt seine Breite; WIDTH=0 heißt ganze Breite."""
    monkeypatch.setenv("COLUMNS", "50")
    monkeypatch.setenv("NO_COLOR", "")
    for width in ("120", "0"):
        stream = Terminal()
        Output(stream, theme=theme(WIDTH=width)).hint("word " * 30)
        lines = stream.getvalue().splitlines()
        assert len(lines) > 1 and all(len(line) <= 50 for line in lines), lines


def test_terminal_colors_and_no_color(monkeypatch):
    """Im Terminal Farben je Rolle; mit NO_COLOR dieselbe Ausgabe ohne Escape-Codes."""
    monkeypatch.setenv("COLUMNS", "200")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "xterm-256color")
    colored = Terminal()
    Output(colored, theme=theme()).head("Group")
    # Farbe 11 gibt rich als helles Gelb (93) aus.
    assert "\x1b[1;93mGroup" in colored.getvalue(), repr(colored.getvalue())
    monkeypatch.setenv("NO_COLOR", "")
    plain = Terminal()
    Output(plain, theme=theme()).head("Group")
    assert plain.getvalue() == ESCAPE.sub("", colored.getvalue())


def test_current_theme_never_fails(sandbox):
    """Eine ungültige Datei bricht die Ausgabe nicht: keine Farben, Abstände der Vorlage."""
    sandbox.themes.mkdir(parents=True)
    sandbox.theme().write_text("C_HEAD=kein\n")
    fallback = current_theme()
    assert not fallback.found and set(fallback.colors.values()) == {""}
    stream = io.StringIO()
    Output(stream).head("Group")
    assert stream.getvalue() == "  Group\n"
