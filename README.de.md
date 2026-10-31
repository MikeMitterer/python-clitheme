<div align="center">

# CLITheme

**Eine Theme-Datei für Farben und Abstände der Ausgabe von Python, Bash und Make**

[Beispiel](#beispiel) · [Schnellstart](#schnellstart) · [Theme-Datei](#theme-datei) · [Einbinden](#einbinden) · [Entwicklung](docs/development.md)

[English](README.md) · Deutsch

</div>

CLITheme hält Farben und Abstände der Kommandozeilen-Ausgabe in einer
kleinen Datei je Theme. Python-Werkzeuge lesen sie über das Paket
`mmit-cli-theme`; Bash-Skripte und Makefiles binden dieselbe Datei direkt
ein. Der Befehl `cli-theme` legt die mitgelieferten Themes an, nennt den Ort
des gewählten und zeigt dessen Rollen und Abstände.

## Inhalt

- [Beispiel](#beispiel)
- [Funktionen](#funktionen)
- [Schnellstart](#schnellstart)
- [Theme-Datei](#theme-datei)
- [Einbinden](#einbinden)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)

## Beispiel

```python
from cli_theme import Output

out = Output()
out.head("Repository")
out.row("Branch", "master")
out.row("Status", "clean")
out.hint("Nothing to commit.")
```

Im Terminal erscheinen Überschrift, Bezeichnungen und Werte in den Farben
des gewählten Themes, in zwei Spalten ausgerichtet. In Pipes, mit `NO_COLOR`
oder mit `TERM=dumb` erscheint derselbe Text ohne Farben und mit denselben
Abständen.

[↑ Inhalt](#inhalt)

## Funktionen

- **Theme-Datei:** Farben für zehn Rollen und sieben Abstände als
  `NAME=value`-Zeilen, lesbar für Python, Bash und Make.
- **Neun Themes:** classic, ocean, earth, night, mono, sunset, forest, neon
  und shell; `CLI_THEME` wählt eines.
- **Geprüftes Lesen:** ungültige oder fehlende Einträge werden mit Datei und
  Zeile gemeldet; ohne Datei gibt es keine Farben und die Abstände von
  classic.
- **rich-Stile:** die Farbe jeder Rolle als [rich](https://github.com/Textualize/rich)-Stil,
  fertig für die eigene Ausgabe.
- **Ausgabehelfer:** `head()`, `row()` und `hint()` brechen lange Zeilen bei
  `WIDTH` oder der Terminalbreite um.
- **Befehl `cli-theme`:** `install`, `path` und `show`, je nach Locale auf
  Englisch oder Deutsch.

[↑ Inhalt](#inhalt)

## Schnellstart

Voraussetzungen: Python 3.11 oder neuer und [pipx](https://pipx.pypa.io/).

**Installieren** mit einem festen Release-Tag. Tags folgen dem Schema
`vX.Y.Z+YYMMDD.HHMM.hash`, und pipx braucht den vollen Tag. Dieser Befehl
zeigt den neuesten:

```bash
git ls-remote --tags --refs --sort=-v:refname https://github.com/MikeMitterer/python-clitheme.git | head -1
```

Damit installieren, `<release-tag>` durch den Tag ersetzen, dann die
Theme-Dateien anlegen:

```bash
pipx install 'git+https://github.com/MikeMitterer/python-clitheme.git@<release-tag>'
cli-theme install
cli-theme show
```

`install` legt jede fehlende Theme-Datei an und lässt vorhandene unverändert;
eigene Änderungen bleiben also erhalten. **Aktualisieren:**
`pipx install --force` mit dem neuen vollen Tag. Wer an CLITheme selbst
arbeitet, installiert die Arbeitskopie mit `pipx install -e <checkout>`;
Änderungen wirken dann ohne Neuinstallation.

Ein Python-Projekt nimmt das Paket in seine Abhängigkeiten auf, ebenfalls mit
dem vollen Tag:

```toml
dependencies = [
    "mmit-cli-theme @ git+https://github.com/MikeMitterer/python-clitheme.git@<release-tag>",
]
```

[↑ Inhalt](#inhalt)

## Theme-Datei

**Ort:** `${XDG_CONFIG_HOME:-~/.config}/cli-theme/<name>.theme`. Die
Umgebungsvariable `CLI_THEME` wählt den Namen, Standard ist `classic`; er
darf Buchstaben, Ziffern, `-` und `_` enthalten. `cli-theme path` gibt den
Ort aus.

**Format:** ein `NAME=value` je Zeile, ohne Anführungszeichen und ohne
Leerzeichen um das `=`, damit Make und Bash die Datei direkt einbinden.
Zeilen mit `#` sind Kommentare. Eine Farbe ist eine Nummer von 0 bis 255,
davor optional `bold+` oder `dim+`; `bold` oder `dim` allein sind erlaubt,
leer heißt Terminalfarbe. Die Datei muss alle 17 Einträge enthalten.

| Rolle | Wofür | classic |
|---|---|---|
| `C_HEAD` | Überschriften und Gruppen | `bold+11` |
| `C_KEY` | Bezeichnungen in der linken Spalte: Targets, Optionen, Schlüssel | `33` |
| `C_TEXT` | Beschreibungen in der Hilfe | `10` |
| `C_VAL` | Werte, Befehle, Pfade | `10` |
| `C_HINT` | Hinweise und Nebensächliches | `dim` |
| `C_ACC` | Hervorhebung im Text: Platzhalter, zulässige Werte, Antworten | `14` |
| `C_OK` | Erfolg (✓), angenommen, freigegeben | `10` |
| `C_WARN` | Warnung, Stillstand, veraltet | `208` |
| `C_ERR` | Fehler (✗), abgelehnt, Konflikt | `bold+196` |
| `C_MARK` | Sonderstellung: Maintainer, Server, Herkunft eines Werts | `13` |

| Abstand | Bedeutung | classic |
|---|---|---|
| `I_HEAD` | Einrückung der Gruppenüberschrift | `2` |
| `I_ROW` | Einrückung einer Zeile oder eines Parameters | `7` |
| `I_HINT` | Einrückung von Hinweistext | `7` |
| `W_KEY` | Breite der Bezeichnung; eine längere steht in eigener Zeile | `21` |
| `GAP` | Mindestabstand zwischen Bezeichnung und Text | `2` |
| `WIDTH` | Höchste Zeilenbreite im Terminal; `0` = ganze Breite | `120` |
| `SPACE` | Leerzeilen vor einer Gruppe | `1` |

**Ohne gültige Datei:** Fehlt die Datei, hat die Ausgabe keine Farben und
die Abstände von classic. Eine ungültige Datei ist ein Fehler mit Datei,
Zeile und Eintrag; `cli-theme show` meldet ihn, die Ausgabehelfer zeigen dann
keine Farben. Theme-Ordner und Datei dürfen keine symbolischen Links sein;
CLITheme liest und schreibt nicht über sie.

[↑ Inhalt](#inhalt)

## Einbinden

**Python:** `Output` schreibt Überschriften, Zeilen und Hinweise wie im
[Beispiel](#beispiel). Für eigene Ausgaben liefert `load_theme()` das Theme
mit Farben und Abständen, `styles()` den rich-Stil je Rolle, und
`rich_style()` wandelt einen einzelnen Wert wie `bold+11` in
`bold color(11)`. Fehler sind `ThemeError` mit stabiler Kennung `code` und
deren `params`; eine Anwendung kann sie so im eigenen Katalog übersetzen.

```python
from cli_theme import load_theme, styles

theme = load_theme()
indent = " " * theme.spacing["i_row"]
style = styles(theme)["warn"]
```

**Bash:** die Datei einbinden und die Werte direkt verwenden; eine Farbe in
eine Escape-Sequenz umzusetzen, ist Sache des Skripts oder seiner Bibliothek.

```bash
theme_file="$(cli-theme path)"
[[ -r "$theme_file" ]] && source "$theme_file"
printf '%*s%s\n' "$I_ROW" '' "indented by I_ROW"
```

**Make:** die Datei optional einbinden, damit das Makefile auch ohne sie
läuft.

```makefile
-include $(shell cli-theme path 2>/dev/null)
```

[↑ Inhalt](#inhalt)

## Entwicklung

Einrichten aus dem Checkout, Tests und Übersetzungen beschreibt die
[Entwicklerdoku](docs/development.md).

[↑ Inhalt](#inhalt)

## Lizenz

Copyright © 2026 Michael Mitterer. **MangoLila GmbH** ist Anbieterin und
Lizenzgeberin.

CLITheme steht unter der **[EUPL 1.2](LICENSE)**, nur Version 1.2. Sie
erlaubt private und gewerbliche Nutzung, Änderungen, Weitergabe, Verkauf und
Hosting ohne kostenpflichtige Lizenz.

Wer CLITheme oder eine geänderte Fassung weitergibt oder als Netzwerkdienst
anbietet, muss die Urheber- und Lizenzhinweise erhalten, Änderungen
kennzeichnen und den zugehörigen Quelltext nach den Copyleft-Regeln der
Lizenz bereitstellen.

Die Gewährleistungs- und Haftungsausschlüsse der EUPL-Artikel 7 und 8 gelten
auch gegenüber Verbrauchern, soweit das Gesetz es zulässt. Zwingende Rechte
bleiben unberührt, darunter die Haftung für Vorsatz, grobe Fahrlässigkeit,
Personenschäden und nach dem Produkthaftungsgesetz. Eine zusätzliche Garantie
wird nicht übernommen.

Kontakt: **office@MangoLila.at**.

Details: [LICENSE](LICENSE) · [Deutscher Lizenztext](LICENSE.de.txt) ·
[Anbieter- und Verbrauchererklärung](LICENSING.md)

[↑ Inhalt](#inhalt)
