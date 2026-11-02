"""ArgumentParser, dessen Hilfe und Fehlermeldungen wie jede Ausgabe mit einer Leerzeile enden."""

import argparse
from typing import NoReturn


class ArgumentParser(argparse.ArgumentParser):
    """argparse.ArgumentParser mit Abschluss: Hilfe (-h, --help, print_help) und Fehlermeldung
    enden mit einer Leerzeile. add_subparsers legt Unterparser derselben Klasse an."""

    def format_help(self) -> str:
        return super().format_help() + "\n"

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        """Wie argparse; eine Meldung (etwa von error) endet zusätzlich mit einer Leerzeile."""
        super().exit(status, f"{message}\n" if message else message)
