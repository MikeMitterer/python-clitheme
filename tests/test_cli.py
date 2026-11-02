"""Befehl cli-theme über den echten Aufruf: --version, path, install, show."""

import os
import re
from importlib.metadata import version

from cli_theme import template_names, template_text

ESCAPE = "\x1b["


def test_version_names_package_version(sandbox):
    """--version nennt die Version des installierten Pakets und endet wie die Hilfe mit einer
    Leerzeile; $(cli-theme --version) in der Shell schneidet sie ab."""
    assert sandbox.run("--version").stdout == f"cli-theme {version('mmit-cli-theme')}\n\n"


def test_path_follows_cli_theme_and_xdg(sandbox):
    """path nennt den Ort des gewählten Themes; ein relativer XDG_CONFIG_HOME gilt nicht."""
    assert sandbox.run("path").stdout.strip() == str(sandbox.theme())
    sandbox.env["CLI_THEME"] = "ocean"
    assert sandbox.run("path").stdout.strip() == str(sandbox.theme("ocean"))
    sandbox.env["XDG_CONFIG_HOME"] = "relative/config"
    expected = sandbox.root / "home" / ".config" / "cli-theme" / "ocean.theme"
    assert sandbox.run("path").stdout.strip() == str(expected)


def test_invalid_cli_theme_is_refused(sandbox):
    """Ein CLI_THEME mit Pfadteilen ist ein Fehler, kein Ort außerhalb des Ordners."""
    sandbox.env["CLI_THEME"] = "../evil"
    result = sandbox.run("path", code=1)
    assert "Invalid CLI_THEME '../evil'" in result.stderr, result.stderr


def test_install_creates_missing_and_keeps_existing(sandbox):
    """install legt alle Vorlagen an; ein zweiter Lauf lässt eigene Änderungen stehen."""
    first = sandbox.run("install").stdout
    names = template_names()
    assert len(names) == 9 and names[0] == "classic"
    for name in names:
        assert sandbox.theme(name).read_text() == template_text(name)
        assert re.search(rf"created +{re.escape(str(sandbox.theme(name)))}", first), first

    sandbox.theme().write_text(template_text().replace("C_HEAD=bold+11", "C_HEAD=1"))
    sandbox.theme("ocean").unlink()
    second = sandbox.run("install").stdout
    assert "C_HEAD=1" in sandbox.theme().read_text()
    assert re.search(rf"unchanged +{re.escape(str(sandbox.theme()))}", second), second
    assert re.search(rf"created +{re.escape(str(sandbox.theme('ocean')))}", second), second
    assert not list(sandbox.themes.glob(".cli-theme-*")), "Hilfsdatei übrig"


def test_install_creates_own_theme_from_classic(sandbox):
    """Nennt CLI_THEME ein eigenes Theme, entsteht es aus der classic-Vorlage."""
    sandbox.env["CLI_THEME"] = "mine"
    sandbox.run("install")
    assert sandbox.theme("mine").read_text() == template_text()


def test_install_refuses_linked_directory(sandbox):
    """Ist der Ordner cli-theme ein Link, schreibt install nichts und endet mit Exit 1."""
    elsewhere = sandbox.root / "elsewhere"
    elsewhere.mkdir()
    sandbox.themes.parent.mkdir(parents=True)
    sandbox.themes.symlink_to(elsewhere)
    result = sandbox.run("install", code=1)
    assert "is a link" in result.stderr, result.stderr
    assert not list(elsewhere.iterdir())


def test_show_without_file_has_no_colors_and_names_next_step(sandbox):
    """Ohne Datei: keine Farben auch im Terminal, Abstände der Vorlage, Hinweis auf install."""
    code, output = sandbox.run_in_terminal("show")
    assert code == 0, output
    assert ESCAPE not in output, output
    assert "cli-theme install" in output
    assert re.search(r"(?m)^       WIDTH {18}120\r?$", output), output


def test_show_colors_in_terminal_only(sandbox):
    """Im Terminal Farben aus der Datei; in Pipes und mit NO_COLOR keine, Abstände gleich."""
    sandbox.run("install")
    code, output = sandbox.run_in_terminal("show")
    assert code == 0, output
    # C_HEAD=bold+11 färbt die Überschriften (Farbe 11 ist das helle Gelb 93), Einzug I_HEAD=2.
    assert re.search(r"(?m)^  \x1b\[1;93mColors", output), output
    plain = sandbox.run("show").stdout
    assert ESCAPE not in plain
    assert re.search(r"(?m)^  Colors$", plain), plain
    assert re.search(r"(?m)^       C_HEAD {17}bold\+11 +Sample$", plain), plain
    sandbox.env["NO_COLOR"] = ""
    code, output = sandbox.run_in_terminal("show")
    assert code == 0 and ESCAPE not in output, output


def test_show_reports_invalid_entry_with_file_and_line(sandbox):
    """Ein ungültiger Wert endet mit Exit 1 und nennt Datei, Zeile und Eintrag."""
    sandbox.run("install")
    path = sandbox.theme()
    lines = path.read_text().splitlines()
    number = next(index for index, line in enumerate(lines, 1) if line.startswith("C_KEY="))
    lines[number - 1] = "C_KEY=256"
    path.write_text("\n".join(lines) + "\n")
    result = sandbox.run("show", code=1)
    assert f"{path}:{number}: invalid theme entry 'C_KEY=256'" in result.stderr, result.stderr


def test_show_reports_missing_entries(sandbox):
    """Fehlen Einträge, nennt show sie alle."""
    sandbox.run("install")
    path = sandbox.theme()
    kept = [line for line in path.read_text().splitlines() if not line.startswith(("C_OK", "GAP"))]
    path.write_text("\n".join(kept) + "\n")
    result = sandbox.run("show", code=1)
    assert f"{path}: missing theme entries C_OK, GAP" in result.stderr, result.stderr


def test_show_refuses_linked_theme_file(sandbox):
    """Eine Theme-Datei als Link liest show nicht, auch wenn das Ziel gültig ist."""
    sandbox.run("install")
    target = sandbox.root / "outside.theme"
    target.write_text(template_text())
    sandbox.theme().unlink()
    sandbox.theme().symlink_to(target)
    result = sandbox.run("show", code=1)
    assert "is a link; refused for safety" in result.stderr, result.stderr


def test_show_reports_invalid_utf8_with_file_and_line(sandbox):
    """Ungültiges UTF-8 ist ein Fehler mit Datei und Zeile, kein Absturz."""
    sandbox.run("install")
    sandbox.theme().write_bytes(template_text().encode() + b"C_HEAD=\xff\n")
    number = len(template_text().splitlines()) + 1
    result = sandbox.run("show", code=1)
    assert f"{sandbox.theme()}:{number}: not valid UTF-8" in result.stderr, result.stderr
    assert "Traceback" not in result.stderr


def test_show_refuses_directory_and_fifo(sandbox):
    """Ein Ordner oder eine benannte Pipe am Ort der Datei ist ein Fehler mit Pfad; nichts
    blockiert (run bricht nach 30 Sekunden ab)."""
    sandbox.themes.mkdir(parents=True)
    sandbox.theme().mkdir()
    result = sandbox.run("show", code=1)
    assert f"{sandbox.theme()} is not a regular file" in result.stderr, result.stderr
    sandbox.theme().rmdir()
    os.mkfifo(sandbox.theme())
    result = sandbox.run("show", code=1)
    assert f"{sandbox.theme()} is not a regular file" in result.stderr, result.stderr


def test_show_reports_unreadable_file(sandbox):
    """Eine Datei ohne Leserecht ist ein Fehler mit Pfad und Grund."""
    sandbox.run("install")
    sandbox.theme().chmod(0)
    try:
        result = sandbox.run("show", code=1)
    finally:
        sandbox.theme().chmod(0o644)
    assert f"{sandbox.theme()}: cannot read (Permission denied)" in result.stderr, result.stderr


def test_german_texts_from_catalog(sandbox):
    """Mit deutscher Sprache kommen die Texte aus dem Katalog, hier aus der .po übersetzt."""
    sandbox.use_german_catalog()
    output = sandbox.run("show").stdout
    assert "Farben" in output and "Abstände" in output and "Muster" in output, output


def ends_with_one_blank_line(text: str) -> bool:
    return text.endswith("\n\n") and not text.endswith("\n\n\n")


def test_output_and_help_end_with_one_blank_line(sandbox):
    """show, install, Hilfe (ohne Argumente, -h, Unterbefehl -h) und Fehler enden mit genau
    einer Leerzeile auf ihrem Strom; path bleibt ohne, zum Kopieren."""
    for args in (["show"], ["install"], [], ["-h"], ["show", "--help"]):
        result = sandbox.run(*args)
        assert ends_with_one_blank_line(result.stdout), (args, result.stdout)
        assert result.stderr == "", (args, result.stderr)
    result = sandbox.run("--bogus", code=2)
    assert ends_with_one_blank_line(result.stderr), result.stderr
    sandbox.theme().write_text("C_HEAD=kein\n")
    result = sandbox.run("show", code=1)
    assert result.stdout == "" and ends_with_one_blank_line(result.stderr), result
    assert sandbox.run("path").stdout == f"{sandbox.theme()}\n"
