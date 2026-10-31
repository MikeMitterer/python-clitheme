"""Deutscher Katalog: vollständig, nicht unscharf, kompiliert auf dem Stand der .po-Datei."""

import io
from pathlib import Path

from babel.messages.extract import extract_from_dir
from babel.messages.mofile import read_mo
from babel.messages.pofile import read_po

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "cli_theme"
CATALOG = PACKAGE / "locales" / "de" / "LC_MESSAGES" / "cli_theme"


def used_messages() -> set[str]:
    """Alle Texte, die der Code mit _() oder N_() markiert."""
    found = extract_from_dir(str(PACKAGE), keywords={"_": None, "N_": None})
    return {message for _, _, message, _, _ in found}


def test_catalog_complete_and_not_fuzzy():
    """Jeder markierte Text hat eine Übersetzung; keine ist unscharf, keine ist verwaist."""
    with CATALOG.with_suffix(".po").open("rb") as stream:
        catalog = read_po(stream)
    entries = {message.id: message for message in catalog if message.id}
    assert set(entries) == used_messages()
    for message in entries.values():
        assert message.string and not message.fuzzy, message.id


def test_compiled_catalog_matches_po():
    """Die .mo-Datei im Paket enthält genau die Übersetzungen der .po-Datei."""
    with CATALOG.with_suffix(".po").open("rb") as stream:
        source = {message.id: message.string for message in read_po(stream) if message.id}
    compiled = read_mo(io.BytesIO(CATALOG.with_suffix(".mo").read_bytes()))
    assert {message.id: message.string for message in compiled if message.id} == source
