"""Übersetzung der sichtbaren Texte; Basissprache Englisch, Deutsch aus dem Katalog."""

import gettext
from pathlib import Path

LOCALES = Path(__file__).parent / "locales"
DOMAIN = "cli_theme"

# Sprache wie üblich aus LANGUAGE, LC_ALL, LC_MESSAGES oder LANG; ohne Katalog Englisch.
_ = gettext.translation(DOMAIN, localedir=LOCALES, fallback=True).gettext


def N_(text: str) -> str:
    """Markiert text für den Katalog; übersetzt wird erst bei der Ausgabe."""
    return text
