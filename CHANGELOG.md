# Changelog

Aus Release-Tags und Conventional Commits erzeugt.

## v0.4.0+261102.1800.5c1a8 — 2026-11-02

Output.write mit wrap=False: Zeilen zum Kopieren nie umbrechen

### Neue Funktionen

- Output.write mit wrap=False – Zeilen zum Kopieren nie umbrechen (T-18) (`390d974`)

## v0.3.0+261102.1724.ca51d — 2026-11-02

Leerzeile am Ende jeder Ausgabe: Output.finish und ArgumentParser

### Fehlerkorrekturen

- hints zeigt Werkzeug-Arbeitskopie nur, wenn das Paket an der Git-Wurzel liegt (T-7) (`4871f72`)

### Weitere Änderungen

- Sprachkataloge wie bei agent-lessons – .mo nicht im Git, Paketbau übersetzt (T-8) (`b42aeb2`)
- .dev-tools.conf.sh im devtools-Format, BashLib-Tag aktualisiert (T-10) (`f2941dc`)
- Version an einer Stelle lesen – READ\_VERSION für help und version (T-12) (`179bb43`)
- make hints liest Paketnamen und Labels aus .dev-tools.conf.sh (T-13) (`eeeba17`)

### Neue Funktionen

- help zeigt bei tag-major/-minor/-patch die Version danach (T-9) (`0948f0b`)
- Leerzeile am Ende jeder Ausgabe – Output.finish und ArgumentParser (T-11) (`c50be1e`)
- --version endet wie Hilfe und Fehler mit einer Leerzeile (T-14) (`27b4ab6`)

### Dokumentation

- --version nicht in der Regel für alle Apps erwähnen (T-17) (`947467f`)

## v0.2.0+261031.1844.14a24 — 2026-10-31

Initial release

### Neue Funktionen

- Theme-Datei in Python lesen, Vorlagen und cli-theme (T-2) (`d8f3fa5`)

### Fehlerkorrekturen

- Kaputte Theme-Datei melden statt abstürzen (T-2 R1) (`af909d0`)

### Dokumentation

- Installation mit pipx aus python-clitheme (T-4) (`7ce85f0`)
