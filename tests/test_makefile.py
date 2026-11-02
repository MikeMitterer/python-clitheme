"""make help: die Release-Targets nennen die Version vorher und nachher."""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ANSI = re.compile(r"\x1b\[[0-9;]*m|\x1b\(B")

pytestmark = pytest.mark.skipif(shutil.which("make") is None, reason="make fehlt")


def help_lines(bash_libs: Path) -> dict[str, str]:
    """Hilfe ohne Farben, je Target die Beschreibung; BASH_LIBS zeigt auf bash_libs."""
    env = {key: value for key, value in os.environ.items() if key != "DEV_MAKE"}
    env["BASH_LIBS"] = str(bash_libs)
    result = subprocess.run(
        ["make", "--no-print-directory", "-C", str(ROOT), "help"],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    lines = {}
    for line in ANSI.sub("", result.stdout).splitlines():
        target, _, desc = line.strip().partition(" ")
        lines[target] = desc.strip()
    return lines


def test_release_targets_show_next_version(tmp_path):
    """Bei 1.4.9 zeigen tag-major, tag-minor und tag-patch 2.0.0, 1.5.0 und 1.4.10."""
    (tmp_path / "version.lib.sh").write_text("readProjectVersion() { echo 1.4.9; }\n")
    lines = help_lines(tmp_path)
    assert "1.4.9 → 2.0.0" in lines["tag-major"]
    assert "1.4.9 → 1.5.0" in lines["tag-minor"]
    assert "1.4.9 → 1.4.10" in lines["tag-patch"]


def test_release_targets_without_bashlib(tmp_path):
    """Ohne BashLib steht ein Hinweis statt der Versionen, und die Hilfe läuft durch."""
    lines = help_lines(tmp_path / "missing")
    for target in ("tag-major", "tag-minor", "tag-patch"):
        assert "Version unbekannt" in lines[target], lines[target]
        assert "→" not in lines[target]
