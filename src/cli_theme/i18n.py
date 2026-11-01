"""Übersetzung der sichtbaren Texte; Basissprache Englisch, Deutsch aus dem Katalog."""

import gettext
import os
from pathlib import Path

# CLI_THEME_LOCALE_DIR nennt einen anderen Katalogordner; die Tests zeigen damit auf einen
# eigenen und hängen nicht davon ab, ob im Quellbaum eine .mo liegt.
LOCALES = Path(os.environ.get("CLI_THEME_LOCALE_DIR") or Path(__file__).parent / "locales")
DOMAIN = "cli_theme"

# Sprache wie üblich aus LANGUAGE, LC_ALL, LC_MESSAGES oder LANG; ohne Katalog Englisch.
_ = gettext.translation(DOMAIN, localedir=LOCALES, fallback=True).gettext


def N_(text: str) -> str:
    """Markiert text für den Katalog; übersetzt wird erst bei der Ausgabe."""
    return text
