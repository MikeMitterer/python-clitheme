"""Gemeinsames CLI-Theme für Python-Werkzeuge: Theme-Datei lesen, rich-Stile, Abstände.

Bash und Make lesen dieselbe Datei direkt; der Befehl cli-theme legt die Vorlagen an.
"""

from cli_theme.arguments import ArgumentParser
from cli_theme.output import Output, current_theme, rich_style, styles
from cli_theme.theme import (
    DEFAULT_THEME,
    ROLES,
    SPACING,
    Theme,
    ThemeError,
    config_dir,
    install_themes,
    load_theme,
    parse_theme,
    template_names,
    template_text,
    theme_name,
    theme_path,
)

__all__ = [
    "ArgumentParser",
    "DEFAULT_THEME",
    "ROLES",
    "SPACING",
    "Output",
    "Theme",
    "ThemeError",
    "config_dir",
    "current_theme",
    "install_themes",
    "load_theme",
    "parse_theme",
    "rich_style",
    "styles",
    "template_names",
    "template_text",
    "theme_name",
    "theme_path",
]
