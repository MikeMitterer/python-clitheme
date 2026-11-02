"""ArgumentParser, dessen Hilfe, Version und Fehlermeldungen wie jede Ausgabe mit einer Leerzeile
enden."""

import argparse
import sys
from typing import Any, NoReturn


class VersionAction(argparse._VersionAction):
    """action="version" wie in argparse; die Ausgabe endet zusätzlich mit einer Leerzeile.

    $(app --version) in der Shell, head -1 und grep sehen die Leerzeile nicht."""

    def __call__(self, parser: argparse.ArgumentParser, *args: Any, **kwargs: Any) -> None:
        try:
            super().__call__(parser, *args, **kwargs)
        finally:
            sys.stdout.write("\n")


class ArgumentParser(argparse.ArgumentParser):
    """argparse.ArgumentParser mit Abschluss: Hilfe (-h, --help, print_help), Version
    (action="version") und Fehlermeldung enden mit einer Leerzeile. add_subparsers legt
    Unterparser derselben Klasse an."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.register("action", "version", VersionAction)

    def format_help(self) -> str:
        return super().format_help() + "\n"

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        """Wie argparse; eine Meldung (etwa von error) endet zusätzlich mit einer Leerzeile."""
        super().exit(status, f"{message}\n" if message else message)
