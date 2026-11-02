<div align="center">

# CLITheme

**One theme file for the colors and spacing of Python, Bash and Make output**

[Example](#example) · [Quick start](#quick-start) · [Theme file](#theme-file) · [Use](#use) · [Development](docs/development.md)

English · [Deutsch](README.de.md)

</div>

CLITheme keeps the colors and spacing of command line output in one small
file per theme. Python tools read it through the package `mmit-cli-theme`;
Bash scripts and Makefiles include the same file directly. The command
`cli-theme` installs the bundled themes, prints the path of the chosen one
and shows its roles and spacing.

## Contents

- [Example](#example)
- [Features](#features)
- [Quick start](#quick-start)
- [Theme file](#theme-file)
- [Use](#use)
- [Development](#development)
- [License](#license)

## Example

```python
from cli_theme import Output

with Output() as out:
    out.head("Repository")
    out.row("Branch", "master")
    out.row("Status", "clean")
    out.hint("Nothing to commit.")
```

In a terminal the heading, labels and values appear in the colors of the
chosen theme, aligned in two columns. In pipes, with `NO_COLOR` or with
`TERM=dumb` the same text appears without colors and with the same spacing.
At the end of the `with` block a blank line closes the output, so the next
prompt does not stick to it.

[↑ Contents](#contents)

## Features

- **Theme file:** colors for ten roles and seven spacing values as
  `NAME=value` lines, readable by Python, Bash and Make.
- **Nine themes:** classic, ocean, earth, night, mono, sunset, forest, neon
  and shell; `CLI_THEME` selects one.
- **Checked reading:** invalid or missing entries are reported with file and
  line; a missing file means no colors and the spacing of classic.
- **rich styles:** the color of each role as a [rich](https://github.com/Textualize/rich)
  style, ready for your own output.
- **Output helpers:** `head()`, `row()` and `hint()` wrap long lines at
  `WIDTH` or the terminal width.
- **Closing blank line:** `Output` and `ArgumentParser` end output, help,
  `--version` and error messages with one blank line.
- **`cli-theme` command:** `install`, `path` and `show`, in English or German
  depending on the locale.

[↑ Contents](#contents)

## Quick start

Requirements: Python 3.11 or later and [pipx](https://pipx.pypa.io/).

**Install** with a fixed release tag. Tags follow the scheme
`vX.Y.Z+YYMMDD.HHMM.hash`, and pipx needs the full tag. This command shows
the latest one:

```bash
git ls-remote --tags --refs --sort=-v:refname https://github.com/MikeMitterer/python-clitheme.git | head -1
```

Install with it, replacing `<release-tag>` with the tag, then create the
theme files:

```bash
pipx install 'git+https://github.com/MikeMitterer/python-clitheme.git@<release-tag>'
cli-theme install
cli-theme show
```

`install` creates every missing theme file and leaves existing ones
unchanged, so your own changes stay. **Update:** run `pipx install --force`
with the new full tag. If you work on CLITheme itself, install the working
copy with `pipx install -e <checkout>`; changes then take effect without
reinstalling.

A Python project adds the package to its dependencies, again with the full
tag:

```toml
dependencies = [
    "mmit-cli-theme @ git+https://github.com/MikeMitterer/python-clitheme.git@<release-tag>",
]
```

[↑ Contents](#contents)

## Theme file

**Location:** `${XDG_CONFIG_HOME:-~/.config}/cli-theme/<name>.theme`. The
environment variable `CLI_THEME` selects the name, `classic` by default; it
may contain letters, digits, `-` and `_`. `cli-theme path` prints the
location.

**Format:** one `NAME=value` per line, without quotes and without spaces
around `=`, so that Make and Bash can include the file directly. Lines
starting with `#` are comments. A color is a number from 0 to 255, optionally
prefixed with `bold+` or `dim+`; `bold` or `dim` alone are allowed, and an
empty value means the terminal color. The file must contain all 17 entries.

| Role | Used for | classic |
|---|---|---|
| `C_HEAD` | Headings and groups | `bold+11` |
| `C_KEY` | Labels in the left column: targets, options, keys | `33` |
| `C_TEXT` | Descriptions in help output | `10` |
| `C_VAL` | Values, commands, paths | `10` |
| `C_HINT` | Hints and secondary text | `dim` |
| `C_ACC` | Emphasis in text: placeholders, allowed values, answers | `14` |
| `C_OK` | Success (✓), accepted, approved | `10` |
| `C_WARN` | Warning, stalled, outdated | `208` |
| `C_ERR` | Error (✗), rejected, conflict | `bold+196` |
| `C_MARK` | Special status: maintainer, server, origin of a value | `13` |

| Spacing | Meaning | classic |
|---|---|---|
| `I_HEAD` | Indent of a group heading | `2` |
| `I_ROW` | Indent of a row or parameter | `7` |
| `I_HINT` | Indent of hint text | `7` |
| `W_KEY` | Width of the label; a longer label gets its own line | `21` |
| `GAP` | Minimum space between label and text | `2` |
| `WIDTH` | Maximum line width in a terminal; `0` = full width | `120` |
| `SPACE` | Blank lines before a group | `1` |

**Without a valid file:** if the file is missing, output has no colors and
uses the spacing of classic. An invalid file is an error that names file,
line and entry; `cli-theme show` reports it, while the output helpers fall
back to no colors. The theme folder and the file must not be symbolic links;
CLITheme refuses to read or write through them.

[↑ Contents](#contents)

## Use

**Python:** `Output` writes headings, rows and hints as in the
[example](#example). For your own output, `load_theme()` returns the theme
with its colors and spacing, `styles()` the rich style of each role, and
`rich_style()` converts a single value such as `bold+11` to
`bold color(11)`. Errors are `ThemeError` with a stable `code` and its
`params`, so an application can translate them in its own catalog.

**Rule for all apps: output ends with one blank line.** `Output.finish()`,
or the end of a `with Output() as out:` block, writes exactly one blank line
to each stream that received output (stdout, stderr) and nothing if there
was none. `ArgumentParser` is a drop-in for `argparse.ArgumentParser` whose
help (`-h`, `--help`, `print_help()`), version (`action="version"`) and
error messages end the same way; subparsers inherit it. `$(app --version)`
in the shell, `head -1` and `grep` do not see the blank line. Machine output
such as a path or a command to copy goes through `print()` instead of
`Output` and stays without the blank line, like `cli-theme path`.

```python
from cli_theme import ArgumentParser, Output

parser = ArgumentParser(prog="app")
arguments = parser.parse_args()
with Output() as out:
    out.head("Result")
```

```python
from cli_theme import load_theme, styles

theme = load_theme()
indent = " " * theme.spacing["i_row"]
style = styles(theme)["warn"]
```

**Bash:** include the file and use the values directly; turning a color into
an escape sequence is up to the script or its library.

```bash
theme_file="$(cli-theme path)"
[[ -r "$theme_file" ]] && source "$theme_file"
printf '%*s%s\n' "$I_ROW" '' "indented by I_ROW"
```

**Make:** include the file optionally, so the Makefile still works without
it.

```makefile
-include $(shell cli-theme path 2>/dev/null)
```

[↑ Contents](#contents)

## Development

Setting up from the checkout, tests and translations are described in the
[developer documentation](docs/development.md) (German).

[↑ Contents](#contents)

## License

Copyright © 2026 Michael Mitterer. **MangoLila GmbH** is the provider and
licensor.

CLITheme is licensed under the **[EUPL 1.2](LICENSE)**, version 1.2 only.
It permits personal and commercial use, changes, redistribution, sale and
hosting without a paid license.

If you redistribute CLITheme or a changed version, or offer it as a network
service, keep the copyright and license notices, mark your changes and
provide the corresponding source under the license's copyleft rules.

The warranty and liability exclusions in EUPL Articles 7 and 8 also apply to
consumers, as far as the law permits. Mandatory rights remain unaffected,
including liability for intent, gross negligence, personal injury and product
liability. No additional guarantee is given.

Contact: **office@MangoLila.at**.

Details: [LICENSE](LICENSE) · [German license text](LICENSE.de.txt) ·
[Provider and consumer declaration](LICENSING.md)

[↑ Contents](#contents)
