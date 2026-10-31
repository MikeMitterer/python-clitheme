"""Theme-Datei lesen und prüfen; Vorlagen vollständig und gleich aufgebaut."""

import re
from pathlib import Path

import pytest

from cli_theme import (
    ROLES,
    SPACING,
    ThemeError,
    load_theme,
    parse_theme,
    template_names,
    template_text,
)

SOURCE = Path("test.theme")
EXPECTED = ("classic", "earth", "forest", "mono", "neon", "night", "ocean", "shell", "sunset")


def entries(**values: str) -> str:
    """Vollständige Theme-Datei aus classic, einzelne Einträge ersetzt."""
    text = template_text()
    for name, value in values.items():
        text = re.sub(rf"(?m)^{name}=.*$", f"{name}={value}", text)
    return text


def test_all_templates_are_shipped_and_valid():
    """Alle neun Vorlagen liegen im Paket und lesen sich fehlerfrei."""
    assert sorted(template_names()) == sorted(EXPECTED)
    for name in template_names():
        theme = parse_theme(template_text(name), Path(f"{name}.theme"))
        assert set(theme.colors) == set(ROLES) and set(theme.spacing) == set(SPACING)


def test_templates_differ_from_classic_only_in_colors_and_title():
    """Kommentare und Abstände stehen in jeder Vorlage gleich; nur Farben und Titel weichen ab.

    So driften die Vorlagen nicht auseinander; WIDTH ist überall 120.
    """

    def skeleton(text: str) -> list[str]:
        return [
            "C_" if line.startswith("C_") else "TITLE" if line.startswith("# Theme ") else line
            for line in text.splitlines()
        ]

    classic = skeleton(template_text())
    for name in template_names():
        assert skeleton(template_text(name)) == classic, name
        assert parse_theme(template_text(name), SOURCE).spacing["width"] == 120


@pytest.mark.parametrize(
    "line",
    [
        "C_HEAD=256",
        "C_HEAD=bold+dim",
        "C_HEAD=italic",
        "I_ROW=-1",
        "I_ROW=x",
        "C_NONE=1",
        "WIDTH = 80",
        'C_KEY="33"',
    ],
)
def test_invalid_entries_name_file_and_line(line):
    """Ungültige Farben, Zahlen, Namen und Schreibweisen sind Fehler mit Ort und Zeile."""
    text = template_text() + line + "\n"
    number = len(text.splitlines())
    with pytest.raises(ThemeError) as caught:
        parse_theme(text, SOURCE)
    assert caught.value.code == "theme_invalid"
    assert str(caught.value) == f"{SOURCE}:{number}: invalid theme entry {line!r}"


def test_valid_color_forms():
    """Farben: Nummer bis 255, mit bold+ oder dim+, dim oder bold allein, leer."""
    text = entries(C_HEAD="bold+255", C_KEY="dim+0", C_TEXT="dim", C_VAL="bold", C_HINT="")
    colors = parse_theme(text, SOURCE).colors
    assert (colors["head"], colors["key"], colors["text"], colors["val"], colors["hint"]) == (
        "bold+255",
        "dim+0",
        "dim",
        "bold",
        "",
    )


def test_missing_entries_are_listed():
    """Fehlende Einträge nennt der Fehler vollständig, Farben zuerst."""
    text = "\n".join(
        line for line in template_text().splitlines() if not line.startswith(("C_MARK", "SPACE"))
    )
    with pytest.raises(ThemeError) as caught:
        parse_theme(text, SOURCE)
    assert caught.value.code == "theme_incomplete"
    assert caught.value.params["names"] == "C_MARK, SPACE"


def test_load_without_file_has_no_colors_and_classic_spacing(sandbox):
    """Fehlt die Datei: keine Farben, Abstände der classic-Vorlage, found ist False."""
    theme = load_theme()
    assert not theme.found and theme.path == sandbox.theme()
    assert set(theme.colors.values()) == {""}
    assert theme.spacing == parse_theme(template_text(), SOURCE).spacing


def test_load_reads_chosen_theme(sandbox, monkeypatch):
    """CLI_THEME wählt die Datei; gelesen wird ihr Inhalt."""
    sandbox.themes.mkdir(parents=True)
    sandbox.theme("mine").write_text(entries(C_HEAD="1", I_ROW="3"))
    monkeypatch.setenv("CLI_THEME", "mine")
    theme = load_theme()
    assert theme.found and theme.colors["head"] == "1" and theme.spacing["i_row"] == 3
