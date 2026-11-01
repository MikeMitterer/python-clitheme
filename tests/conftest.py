"""Gemeinsame Hilfen: temporärer XDG-Ort und Aufruf des echten Befehls cli-theme."""

import fcntl
import os
import pty
import struct
import subprocess
import sys
import termios
from dataclasses import dataclass
from pathlib import Path

import pytest
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

# Der installierte Befehl aus der venv der Tests, nicht ein Modulaufruf.
COMMAND = Path(sys.executable).parent / "cli-theme"
# Umgebungsvariablen, die Sprache, Farben oder Theme-Wahl verändern würden.
NEUTRAL = ("CLI_THEME", "NO_COLOR", "TERM", "LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG", "COLUMNS")
# Katalogordner ohne Kataloge, gesetzt vor dem ersten Import von cli_theme: Bibliothek und
# Befehl lesen nie eine .mo des Quellbaums, die make setup erzeugt hat.
os.environ["CLI_THEME_LOCALE_DIR"] = str(Path(__file__).parent / "no-locale")
PO = Path(__file__).parents[1] / "src/cli_theme/locales/de/LC_MESSAGES/cli_theme.po"


@dataclass
class Sandbox:
    """Temporäre Heimat mit eigenem XDG_CONFIG_HOME; run startet cli-theme darin."""

    root: Path
    env: dict[str, str]

    @property
    def themes(self) -> Path:
        return self.root / "config" / "cli-theme"

    def theme(self, name: str = "classic") -> Path:
        return self.themes / f"{name}.theme"

    def use_german_catalog(self) -> None:
        """Übersetzt die deutsche .po in einen Katalogordner der Sandbox und schaltet die
        Aufrufe darauf und auf Deutsch um; der Quellbaum bleibt unberührt."""
        folder = self.root / "locale"
        target = folder / "de" / "LC_MESSAGES" / "cli_theme.mo"
        target.parent.mkdir(parents=True)
        with PO.open("rb") as source, target.open("wb") as stream:
            write_mo(stream, read_po(source, locale="de"))
        self.env["CLI_THEME_LOCALE_DIR"] = str(folder)
        self.env["LANGUAGE"] = "de"

    def run(self, *args: str, code: int = 0) -> subprocess.CompletedProcess:
        """cli-theme mit args in einer Pipe; prüft den Exit-Code. Hängt der Aufruf, scheitert
        der Test nach 30 Sekunden statt die ganze Suite zu blockieren."""
        result = subprocess.run(
            [str(COMMAND), *args],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert result.returncode == code, (result.returncode, result.stdout, result.stderr)
        return result

    def run_in_terminal(self, *args: str, columns: int = 200) -> tuple[int, str]:
        """cli-theme in einem Pseudo-Terminal mit columns Spalten; Exit-Code und Ausgabe."""
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 40, columns, 0, 0))
        process = subprocess.Popen(
            [str(COMMAND), *args], env=self.env, stdin=slave, stdout=slave, stderr=slave
        )
        os.close(slave)
        chunks = []
        while True:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            chunks.append(chunk)
        process.wait()
        os.close(master)
        return process.returncode, b"".join(chunks).decode("utf-8", "replace")


@pytest.fixture
def sandbox(tmp_path, monkeypatch) -> Sandbox:
    """Leere Heimat und XDG-Ort für Prozess und Bibliothek; nie die echte Konfiguration."""
    home = tmp_path / "home"
    home.mkdir()
    for name in NEUTRAL:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("TERM", "xterm-256color")
    return Sandbox(tmp_path, dict(os.environ))
