"""Befehl cli-theme: Vorlagen anlegen, Ort nennen, Rollen und Abstände zeigen."""

import argparse
import sys
from importlib.metadata import version

from rich.text import Text

from cli_theme.i18n import N_, _
from cli_theme.output import Output, styles
from cli_theme.theme import (
    ROLES,
    SPACING,
    ThemeError,
    install_themes,
    load_theme,
    theme_name,
    theme_path,
)

PACKAGE = "mmit-cli-theme"
SAMPLE = N_("Sample")


def install(out: Output) -> int:
    """Legt fehlende Vorlagen an; vorhandene Dateien bleiben unverändert."""
    out.head(_("Theme files"))
    for path, created in install_themes():
        state = _("created") if created else _("unchanged")
        style = out.styles["ok"] if created else out.styles["hint"]
        out.row(Text(f"{state:<10}", style=style), Text(str(path), style=out.styles["val"]))
    return 0


def show(out: Output) -> int:
    """Zeigt Ort, Farbrollen mit Muster und Abstände des gewählten Themes."""
    theme = load_theme()
    out.head(_("Theme"))
    out.row("CLI_THEME", theme_name())
    out.row(_("File"), str(theme.path))
    if not theme.found:
        out.hint(_("File missing: no colors, spacing from the classic template."))
        out.hint(_("Create it with: cli-theme install"))
    rich = styles(theme)
    out.head(_("Colors"))
    for role in ROLES:
        value = theme.colors[role]
        sample = Text(f"{value or '-':<10}", style=out.styles["val"]) + Text(
            _(SAMPLE), style=rich[role]
        )
        out.row(f"C_{role.upper()}", sample)
    out.head(_("Spacing"))
    for name in SPACING:
        out.row(name.upper(), theme.spacing[name])
    return 0


def parser() -> argparse.ArgumentParser:
    """Argumente: install, path, show und --version."""
    result = argparse.ArgumentParser(
        prog="cli-theme",
        description=_("Shared CLI theme for Python, Bash and Make: colors and spacing."),
    )
    result.add_argument("--version", action="version", version=f"%(prog)s {version(PACKAGE)}")
    commands = result.add_subparsers(dest="command", metavar="COMMAND")
    commands.add_parser("install", help=_("create missing theme files, keep existing ones"))
    commands.add_parser("path", help=_("print the path of the chosen theme file"))
    commands.add_parser("show", help=_("show roles and spacing of the chosen theme"))
    return result


def main(argv: list[str] | None = None) -> int:
    """Einstieg des Befehls cli-theme; Fehler im Theme enden mit Exit 1."""
    arguments = parser().parse_args(argv)
    if arguments.command is None:
        parser().print_help()
        return 0
    out = Output()
    try:
        if arguments.command == "path":
            print(theme_path())
            return 0
        code = install(out) if arguments.command == "install" else show(out)
    except (ThemeError, OSError) as error:
        out.error(f"✗ {error}")
        return 1
    print()
    return code


if __name__ == "__main__":
    sys.exit(main())
