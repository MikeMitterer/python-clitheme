"""ArgumentParser: Hilfe und Fehlermeldung enden mit einer Leerzeile, auch in Unterparsern."""

import io

import pytest

from cli_theme import ArgumentParser


def build() -> ArgumentParser:
    """Parser mit einem Unterbefehl run, wie ihn eine App anlegt."""
    parser = ArgumentParser(prog="app", description="Sample app.")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("run", help="run it")
    return parser


def ends_with_one_blank_line(text: str) -> bool:
    return text.endswith("\n\n") and not text.endswith("\n\n\n")


def test_print_help_ends_with_blank_line():
    """print_help, wie ihn eine App ohne Argumente aufruft, endet mit einer Leerzeile."""
    stream = io.StringIO()
    build().print_help(stream)
    assert ends_with_one_blank_line(stream.getvalue()), repr(stream.getvalue())


@pytest.mark.parametrize("args", [["-h"], ["--help"], ["run", "-h"]])
def test_help_option_ends_with_blank_line(args, capsys):
    """-h und --help enden mit Exit 0 und einer Leerzeile, auch im Unterparser."""
    with pytest.raises(SystemExit) as stop:
        build().parse_args(args)
    assert stop.value.code == 0
    output = capsys.readouterr().out
    assert ends_with_one_blank_line(output), repr(output)


@pytest.mark.parametrize("args", [["--unknown"], ["nope"], ["run", "--unknown"]])
def test_error_ends_with_blank_line(args, capsys):
    """Eine Fehlermeldung endet mit Exit 2 und einer Leerzeile auf stderr."""
    with pytest.raises(SystemExit) as stop:
        build().parse_args(args)
    assert stop.value.code == 2
    errors = capsys.readouterr().err
    assert "error:" in errors and ends_with_one_blank_line(errors), repr(errors)


def test_subparsers_inherit_class():
    """add_subparsers legt Unterparser derselben Klasse an."""
    parser = ArgumentParser(prog="app")
    child = parser.add_subparsers().add_parser("run")
    assert isinstance(child, ArgumentParser)
