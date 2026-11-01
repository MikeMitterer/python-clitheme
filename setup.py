"""Paketbau: die Sprachkataloge (.po) werden beim Bauen zu .mo übersetzt.

Die .mo liegen nicht im Git. Damit ein Wheel, auch eines aus dem sdist oder aus
pipx install git+…, deutsche Texte zeigt, ohne dass jemand make setup aufruft, übersetzt
build_py die .po in den Build-Ordner, nie in den Quellbaum. Alle übrigen Angaben stehen in
pyproject.toml.
"""

from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

SOURCE = Path("src")


class BuildWithCatalogs(build_py):
    """build_py, das zusätzlich jede .po des Pakets als .mo in den Build-Ordner schreibt."""

    def run(self) -> None:
        super().run()
        from babel.messages.mofile import write_mo
        from babel.messages.pofile import read_po

        for po in sorted(SOURCE.glob("cli_theme/locales/*/LC_MESSAGES/*.po")):
            target = Path(self.build_lib) / po.relative_to(SOURCE).with_suffix(".mo")
            target.parent.mkdir(parents=True, exist_ok=True)
            with po.open("rb") as source:
                catalog = read_po(source, locale=po.parents[1].name)
            with target.open("wb") as stream:
                write_mo(stream, catalog)


setup(cmdclass={"build_py": BuildWithCatalogs})
