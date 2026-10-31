"""Theme-Datei finden, lesen, prüfen und aus den Vorlagen anlegen.

Die Datei liegt unter ${XDG_CONFIG_HOME:-~/.config}/cli-theme/<name>.theme, CLI_THEME wählt
den Namen (Standard classic). Sie enthält Farbrollen (C_*) und Abstände als NAME=wert; Bash
und Make binden dieselbe Datei direkt ein. Ohne Datei gibt es keine Farben, die Abstände
kommen aus der classic-Vorlage.
"""

import os
import re
import tempfile
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

from cli_theme.i18n import N_, _

THEME_DIR = "cli-theme"
DEFAULT_THEME = "classic"
SUFFIX = ".theme"
# Farbrollen; in Python ohne Präfix und klein (C_HEAD → head).
ROLES = ("head", "key", "text", "val", "hint", "acc", "ok", "warn", "err", "mark")
# Abstände; in Python klein (I_ROW → i_row).
SPACING = ("i_head", "i_row", "i_hint", "w_key", "gap", "width", "space")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
LINE = re.compile(r"([A-Z][A-Z_]*)=(.*)")
COLOR = re.compile(r"(?:(bold|dim)\+)?(\d{1,3})|bold|dim|")


class ThemeError(ValueError):
    """Fehler mit stabiler Kennung (code) und Werten (params); der Text ist übersetzt.

    Eine Anwendung mit eigenem Katalog übersetzt über code und params selbst.
    """

    def __init__(self, code: str, message: str, **params: object) -> None:
        self.code = code
        self.message = message
        self.params = params
        super().__init__(_(message).format(**params))


@dataclass(frozen=True)
class Theme:
    """Gelesenes Theme: Farbangabe je Rolle (bold+11 …), Abstände als Zahl, Herkunft.

    found ist False, wenn die Datei fehlt; dann sind alle Farben leer.
    """

    colors: dict[str, str] = field(default_factory=dict)
    spacing: dict[str, int] = field(default_factory=dict)
    path: Path | None = None
    found: bool = False


def theme_name() -> str:
    """Name aus CLI_THEME, sonst classic; nur Buchstaben, Ziffern, - und _ (kein Pfad)."""
    name = os.environ.get("CLI_THEME") or DEFAULT_THEME
    if not NAME.fullmatch(name):
        raise ThemeError("theme_name_invalid", N_("Invalid CLI_THEME {name}"), name=repr(name))
    return name


def config_dir() -> Path:
    """Ordner der Theme-Dateien: $XDG_CONFIG_HOME/cli-theme, sonst ~/.config/cli-theme.

    Ein relativer XDG_CONFIG_HOME gilt nach der XDG-Spezifikation nicht.
    """
    base = os.environ.get("XDG_CONFIG_HOME", "")
    root = Path(base) if os.path.isabs(base) else Path.home() / ".config"
    return root / THEME_DIR


def theme_path(name: str | None = None) -> Path:
    """Ort der Theme-Datei name, ohne Angabe des gewählten Themes."""
    return config_dir() / f"{name or theme_name()}{SUFFIX}"


def template_names() -> tuple[str, ...]:
    """Namen der mitgelieferten Vorlagen, classic zuerst."""
    names = sorted(
        entry.name.removesuffix(SUFFIX)
        for entry in resources.files("cli_theme").joinpath("templates").iterdir()
        if entry.name.endswith(SUFFIX)
    )
    return (DEFAULT_THEME, *(name for name in names if name != DEFAULT_THEME))


def template_text(name: str = DEFAULT_THEME) -> str:
    """Inhalt der mitgelieferten Vorlage name."""
    template = resources.files("cli_theme").joinpath("templates", f"{name}{SUFFIX}")
    return template.read_text(encoding="utf-8")


def parse_theme(text: str, source: Path) -> Theme:
    """Liest NAME=wert-Zeilen; Kommentare und Leerzeilen zählen nicht. Unbekannte Namen,
    ungültige Farben oder Zahlen und fehlende Einträge sind Fehler mit Datei und Zeile."""
    colors: dict[str, str] = {}
    spacing: dict[str, int] = {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        match = LINE.fullmatch(line)
        key = match.group(1).lower() if match else ""
        value = match.group(2).strip() if match else ""
        color = COLOR.fullmatch(value)
        if key.startswith("c_") and key[2:] in ROLES and color and int(color[2] or 0) < 256:
            colors[key[2:]] = value
        elif key in SPACING and value.isascii() and value.isdigit():
            spacing[key] = int(value)
        else:
            raise ThemeError(
                "theme_invalid",
                N_("{source}:{line}: invalid theme entry {entry}"),
                source=source,
                line=number,
                entry=repr(raw.strip()),
            )
    missing = [f"C_{role.upper()}" for role in ROLES if role not in colors] + [
        name.upper() for name in SPACING if name not in spacing
    ]
    if missing:
        raise ThemeError(
            "theme_incomplete",
            N_("{source}: missing theme entries {names}"),
            source=source,
            names=", ".join(missing),
        )
    return Theme(colors, spacing, source, True)


def fallback_theme(path: Path | None = None) -> Theme:
    """Ohne Theme-Datei: keine Farben, die Abstände der classic-Vorlage."""
    spacing = parse_theme(template_text(), Path(f"{DEFAULT_THEME}{SUFFIX}")).spacing
    return Theme({role: "" for role in ROLES}, spacing, path, False)


def _refuse_link(path: Path) -> None:
    """Bricht ab, wenn path ein Link ist; so liest und schreibt nichts außerhalb des Ordners."""
    if path.is_symlink():
        raise ThemeError("theme_link", N_("{path} is a link; refused for safety"), path=path)


def read_theme_file(path: Path) -> str | None:
    """Text der Theme-Datei ohne Link-Folge, weder beim Ordner cli-theme noch bei der Datei;
    fehlt sie, None. O_NOFOLLOW hält auch einen Tausch zwischen Prüfung und Öffnen auf."""
    _refuse_link(path.parent)
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except FileNotFoundError:
        return None
    except OSError as error:
        if path.is_symlink():
            raise ThemeError(
                "theme_link", N_("{path} is a link; refused for safety"), path=path
            ) from error
        raise
    with os.fdopen(descriptor, encoding="utf-8") as stream:
        return stream.read()


def load_theme(name: str | None = None) -> Theme:
    """Theme name (ohne Angabe das gewählte); fehlt die Datei, die Rückfallstufe ohne Farben.

    Eine ungültige Datei oder ein Link ist ein ThemeError mit Ort und Grund.
    """
    path = theme_path(name)
    text = read_theme_file(path)
    if text is None:
        return fallback_theme(path)
    return parse_theme(text, path)


def _create(path: Path, content: str) -> bool:
    """Legt path mit content an, ohne eine vorhandene Datei oder einen Link zu ersetzen.

    Geschrieben wird in eine Hilfsdatei daneben; os.link setzt sie nur ein, wenn path noch
    nicht existiert. So entsteht nie eine halbe Datei. False, wenn path schon existiert.
    """
    descriptor, temporary = tempfile.mkstemp(prefix=".cli-theme-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            return False
        return True
    finally:
        os.unlink(temporary)


def install_themes() -> list[tuple[Path, bool]]:
    """Legt jede fehlende Vorlage im Konfigurationsordner an; vorhandene Dateien bleiben.

    Nennt CLI_THEME ein eigenes Theme ohne Datei, entsteht es aus der classic-Vorlage, damit
    es sich anpassen lässt. Liefert je Datei den Ort und ob sie neu angelegt wurde.
    """
    directory = config_dir()
    _refuse_link(directory)
    directory.mkdir(parents=True, exist_ok=True)
    names = list(template_names())
    sources = {name: name for name in names}
    chosen = theme_name()
    if chosen not in sources:
        names.append(chosen)
        sources[chosen] = DEFAULT_THEME
    result = []
    for name in names:
        path = theme_path(name)
        result.append((path, _create(path, template_text(sources[name]))))
    return result
