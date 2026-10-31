# Entwicklung

[← README](../README.de.md)

Diese Seite beschreibt die Arbeit **an** CLITheme: Einrichten aus dem
Checkout, Tests, Übersetzungen, Aufbau und Release. Alle Befehle zeigt
`make help`, die Reihenfolge für den ersten Start `make hints`.

## Übersicht

- [Voraussetzungen](#voraussetzungen)
- [Einrichten](#einrichten)
- [Tests](#tests)
- [Übersetzungen](#übersetzungen)
- [Aufbau](#aufbau)
- [Version und Release](#version-und-release)

## Voraussetzungen

Python 3.11 oder neuer; `make setup` nimmt `python3.14`, ein anderer
Interpreter geht mit `PYTHON_BOOTSTRAP=…`. Einzige Laufzeitabhängigkeit ist
rich.

Die Prüfungen brauchen ProjectTools (`docs-check`, `repo-status`,
`changelog`), Releases zusätzlich BashLib, beide über pipx. Die verlangten
Release-Tags stehen in `.dev-tools.conf.sh`; `make hints` nennt die
Installationsbefehle, `make info` die gefundenen Versionen.

[↑ Übersicht](#übersicht)

## Einrichten

```bash
make setup
```

`setup` legt die `.venv` an, installiert das Paket editierbar samt den
Werkzeugen für Tests, Lint und Kataloge (Extra `dev` in `pyproject.toml`) und
aktiviert den pre-commit-Hook unter `.githooks/`, der vor jedem Commit die
Doku prüft. Ein zweiter Aufruf ist schnell; neu installiert wird nur, wenn
`pyproject.toml` sich geändert hat. Danach steht `.venv/bin/cli-theme` bereit. Die eigenen Theme-Dateien unter
`~/.config/cli-theme/` bleiben dabei unberührt.

[↑ Übersicht](#übersicht)

## Tests

```bash
make check
```

`check` ist der volle Prüflauf: Ruff (Lint und Format), Shellcheck, die
Doku-Prüfung und alle Tests. `make test ARGS="-k name"` lässt nur passende
Tests laufen, `make format` formatiert den Python-Code. Ohne `make setup`
brechen die Prüfungen mit einem Hinweis darauf ab.

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
make catalog
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

## Version und Release

Die Version steht nur in `pyproject.toml`; `cli-theme --version` liest sie
aus den Paketdaten, `make version` zeigt sie zusammen mit dem letzten Tag.

Ein Release erhöht die Version, committet, setzt den Tag
`v<version>+YYMMDD.HHMM.hash`, pusht und schreibt danach `CHANGELOG.md`:

```bash
make tag-patch MSG="Kurze Beschreibung des Releases"
```

`tag-minor` und `tag-major` erhöhen die jeweilige Stelle. `make changelog`
zeigt vorher eine Vorschau.

[↑ Übersicht](#übersicht)
