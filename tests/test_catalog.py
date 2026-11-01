"""Deutscher Katalog: vollständig, nicht unscharf, beim Paketbau übersetzt und im Wheel."""

import io
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from babel.messages.extract import extract_from_dir
from babel.messages.mofile import read_mo
from babel.messages.pofile import read_po

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "cli_theme"
CATALOG = PACKAGE / "locales" / "de" / "LC_MESSAGES" / "cli_theme"


def used_messages() -> set[str]:
    """Alle Texte, die der Code mit _() oder N_() markiert."""
    found = extract_from_dir(str(PACKAGE), keywords={"_": None, "N_": None})
    return {message for _, _, message, _, _ in found}


def translations(messages) -> dict[str, str]:
    """Kennung und Übersetzung je Eintrag, ohne den Kopfeintrag."""
    return {message.id: message.string for message in messages if message.id}


def test_catalog_complete_and_not_fuzzy():
    """Jeder markierte Text hat eine Übersetzung; keine ist unscharf, keine ist verwaist."""
    with CATALOG.with_suffix(".po").open("rb") as stream:
        catalog = read_po(stream)
    entries = {message.id: message for message in catalog if message.id}
    assert set(entries) == used_messages()
    for message in entries.values():
        assert message.string and not message.fuzzy, message.id


def test_po_merges_by_union():
    """Zwei Tickets hängen neue Einträge oft an dieselbe Stelle; der Merge behält beide."""
    result = subprocess.run(
        ["git", "-C", str(ROOT), "check-attr", "merge", "--", str(CATALOG.with_suffix(".po"))],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip().endswith(": merge: union"), result.stdout


def test_wheel_brings_compiled_catalog(tmp_path):
    """Ein Wheel aus den Dateien, die git kennt, enthält die .mo genau zur .po.

    Die Kopie lässt von git ignorierte Dateien weg, also auch eine .mo aus make setup; die
    Übersetzung muss deshalb aus dem Bauschritt kommen, nicht aus dem Quellbaum."""
    listed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        check=True,
    ).stdout.decode()
    source = tmp_path / "source"
    for name in filter(None, listed.split("\0")):
        if (ROOT / name).is_file():
            (source / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, source / name)
    assert not list(source.rglob("*.mo"))
    subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "-q", "--no-deps", "--no-build-isolation"]
        + ["--no-index", "-w", str(tmp_path / "dist"), str(source)],
        check=True,
        timeout=120,
    )
    (wheel,) = (tmp_path / "dist").glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        packed = archive.read(CATALOG.with_suffix(".mo").relative_to(PACKAGE.parent).as_posix())
    compiled = read_mo(io.BytesIO(packed))
    with CATALOG.with_suffix(".po").open("rb") as stream:
        assert translations(compiled) == translations(read_po(stream))
