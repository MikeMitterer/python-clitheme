# Entwicklung

[← README](../README.de.md)

Diese Seite beschreibt die Arbeit **an** CLITheme: Einrichten aus dem
Checkout, Tests, Übersetzungen und Aufbau.

## Übersicht

- [Voraussetzungen](#voraussetzungen)
- [Einrichten](#einrichten)
- [Tests](#tests)
- [Übersetzungen](#übersetzungen)
- [Aufbau](#aufbau)
- [Version](#version)

## Voraussetzungen

Python 3.11 oder neuer; entwickelt wird mit der neuesten stabilen Version.
Einzige Laufzeitabhängigkeit ist rich.

[↑ Übersicht](#übersicht)

## Einrichten

Die Entwicklungsumgebung ist eine `.venv` im Checkout. Das Paket kommt
editierbar hinein, zusammen mit den Werkzeugen für Tests, Lint und Kataloge
(Extra `dev` in `pyproject.toml`):

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

Danach steht `.venv/bin/cli-theme` bereit. Die eigenen Theme-Dateien unter
`~/.config/cli-theme/` bleiben dabei unberührt.

[↑ Übersicht](#übersicht)

## Tests

```bash
.venv/bin/pytest
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
```

Die Tests rufen den installierten Befehl `cli-theme` auf, auch in einem
Pseudo-Terminal für die farbige Ausgabe, und arbeiten mit echten Dateien in
einem temporären `XDG_CONFIG_HOME`. Sie lesen und schreiben nie die
Konfiguration des Rechners.

[↑ Übersicht](#übersicht)

## Übersetzungen

Basissprache der sichtbaren Texte ist Englisch; der Code markiert sie mit
`_()` oder `N_()`. Die deutsche Übersetzung steht in
`src/cli_theme/locales/de/LC_MESSAGES/cli_theme.po`, die kompilierte `.mo`
daneben wird mitcommittet und kommt ins Paket.

Nach einer Änderung an Texten oder an der `.po`-Datei neu kompilieren:

```bash
.venv/bin/pybabel compile -D cli_theme -d src/cli_theme/locales -l de
```

Ein Test prüft, dass jeder markierte Text übersetzt und nicht unscharf ist
und dass die `.mo`-Datei zur `.po`-Datei passt.

[↑ Übersicht](#übersicht)

## Aufbau

| Ort | Inhalt |
|---|---|
| `src/cli_theme/theme.py` | Ort, Lesen und Prüfen der Theme-Datei, Anlegen aus den Vorlagen |
| `src/cli_theme/output.py` | rich-Stile, Ausgabebreite, Ausgabehelfer `Output` |
| `src/cli_theme/cli.py` | Befehl `cli-theme` |
| `src/cli_theme/templates/` | Vorlagen der neun Themes |
| `tests/` | Tests über die echte CLI und die Bibliothek |

Alle Vorlagen haben denselben Aufbau wie `classic.theme` und unterscheiden
sich nur in den Farben und der Titelzeile; ein Test hält das fest. Eine
Änderung an Kommentaren oder Abständen gilt deshalb für alle neun Dateien.

[↑ Übersicht](#übersicht)

## Version

Die Version steht nur in `pyproject.toml`; `cli-theme --version` liest sie
aus den Paketdaten.

[↑ Übersicht](#übersicht)
