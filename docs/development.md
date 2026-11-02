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
Release-Tags stehen in `.dev-tools.conf.sh` im Format von devtools;
`make hints` nennt die Installationsbefehle, `make info` die gefundenen
Versionen. `devtools status` zeigt den Stand, `devtools upgrade --write`
trägt die neuesten Tags ein.

[↑ Übersicht](#übersicht)

## Einrichten

```bash
make setup
```

`setup` legt die `.venv` an, installiert das Paket editierbar samt den
Werkzeugen für Tests, Lint und Kataloge (Extra `dev` in `pyproject.toml`),
übersetzt die Kataloge (`.po` nach `.mo`) und aktiviert den pre-commit-Hook
unter `.githooks/`, der vor jedem Commit die Doku prüft. Ein zweiter Aufruf
ist schnell; neu installiert wird nur, wenn `pyproject.toml` sich geändert
hat, neu übersetzt nur eine geänderte `.po`. Danach steht `.venv/bin/cli-theme` bereit. Die eigenen Theme-Dateien unter
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
Konfiguration des Rechners. `CLI_THEME_LOCALE_DIR` zeigt Bibliothek und
Befehl in den Tests auf einen eigenen Katalogordner; die deutschen Texte
prüfen sie mit einer `.mo`, die sie selbst aus der `.po` übersetzen, nie mit
der aus `make setup`.

[↑ Übersicht](#übersicht)

## Übersetzungen

Basissprache der sichtbaren Texte ist Englisch; der Code markiert sie mit
`_()` oder `N_()`. Die deutsche Übersetzung steht in
`src/cli_theme/locales/de/LC_MESSAGES/cli_theme.po` und wird von Hand
gepflegt: Ein neuer Text kommt als Eintrag ans Ende der Datei. Weil
`.gitattributes` die `.po` mit `merge=union` zusammenführt, behält ein Merge
die Einträge zweier Tickets, die beide ans Ende angehängt haben.

Die übersetzte `.mo` liegt nicht im Git. Für die Entwicklung erzeugt sie
`make setup`; nach einer Änderung an der `.po` melden die Prüfungen sie als
veraltet, bis `make setup` sie neu übersetzt. Beim Paketbau übersetzt
`setup.py` die `.po` in den Build-Ordner (Babel steht dafür in
`build-system.requires`), sodass auch ein Wheel aus
`pipx install git+…` die deutschen Texte enthält.

Welche Texte der Code markiert, sammelt zum Vergleich mit der `.po`:

```bash
make messages
```

Das schreibt `build/cli_theme.pot`; die Datei ist nur zum Ansehen da und
nicht im Git. Ein Test prüft, dass jeder markierte Text genau einen
übersetzten, nicht unscharfen Eintrag hat und kein Eintrag verwaist ist, ein
weiterer baut ein Wheel und vergleicht dessen `.mo` mit der `.po`.

[↑ Übersicht](#übersicht)

## Aufbau

| Ort | Inhalt |
|---|---|
| `src/cli_theme/theme.py` | Ort, Lesen und Prüfen der Theme-Datei, Anlegen aus den Vorlagen |
| `src/cli_theme/output.py` | rich-Stile, Ausgabebreite, Ausgabehelfer `Output` mit Abschluss |
| `src/cli_theme/arguments.py` | `ArgumentParser`: Hilfe und Fehlermeldungen enden mit einer Leerzeile |
| `src/cli_theme/cli.py` | Befehl `cli-theme` |
| `src/cli_theme/locales/` | Übersetzungen (`.po`), dazu die `.mo` aus `make setup` |
| `setup.py` | Paketbau: übersetzt die Kataloge in den Build-Ordner |
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

`tag-minor` und `tag-major` erhöhen die jeweilige Stelle. `make help` zeigt
bei jedem der drei Targets, welche Version danach gilt, etwa
`Patch-Release 0.2.0 → 0.2.1`; ohne BashLib steht dort „Version unbekannt“.
`make changelog` zeigt vorher eine Vorschau.

[↑ Übersicht](#übersicht)
