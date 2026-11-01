# Sicherheitsprofil

Was in diesem Projekt schutzwürdig ist und welche Grundsatzentscheidungen
gelten. Ein Konzeptticket, das den Aufbau der App berührt, prüft und ergänzt
es. Bei jedem Code-Ticket prüfen Implementer und Reviewer den Diff dagegen
(Guard `security`, Bericht ist Pflicht).
Leere Abschnitte heißen „noch nicht entschieden“; „keine“ ist eine Entscheidung.

## Sensible Daten

Keine. Die Theme-Dateien enthalten nur Farbangaben und Abstände.

## Speicherorte

CLITheme liest und schreibt nur unter
`${XDG_CONFIG_HOME:-~/.config}/cli-theme/`. Ein relativer `XDG_CONFIG_HOME`
gilt nicht. Der Ordner `cli-theme` und die Theme-Dateien dürfen keine Links
sein: Lesen öffnet mit `O_NOFOLLOW`, Anlegen setzt eine fertige Hilfsdatei
per `os.link` ein und ersetzt nie eine vorhandene Datei oder einen Link.
Vorhandene Dateien des Nutzers werden nie überschrieben. Gelesen werden nur
reguläre Dateien; ein Ordner oder eine benannte Pipe am Ort der Datei ist ein
Fehler, und `O_NONBLOCK` verhindert, dass das Öffnen einer Pipe hängt.
Jeder Lesefehler, auch ungültiges UTF-8, ist ein `ThemeError` mit Pfad; die
Ausgabehelfer fallen dann auf „keine Farben“ zurück.

## Geheimnisse

Keine.

## Anmeldung

Keine; CLITheme ist eine lokale Bibliothek mit Befehl, ohne Benutzer oder
Sitzungen.

## Zugriffe von außen

Eingaben sind die Umgebungsvariablen `CLI_THEME`, `XDG_CONFIG_HOME` und
`CLI_THEME_LOCALE_DIR` und der Inhalt der Theme-Datei. `CLI_THEME` darf nur Buchstaben, Ziffern, `-` und
`_` enthalten und kann so keinen Pfad bilden. Jede Zeile der Theme-Datei wird
gegen das Format geprüft; Unbekanntes ist ein Fehler. Kein Netzzugriff.

`CLI_THEME_LOCALE_DIR` nennt einen anderen Katalogordner und ist für die
Tests gedacht. Gelesen wird daraus nur die `.mo` der Sprache über gettext;
fehlt sie oder der Ordner, bleiben die Texte englisch. Wer die Variable
setzen kann, steuert ohnehin die Umgebung des Prozesses; mehr als die
angezeigten Texte ändert ein fremder Katalog nicht.

Bash und Make binden die Theme-Datei mit `source` bzw. `include` ein und
führen damit ihren Inhalt aus. Sie liegt im Konfigurationsordner des Nutzers
und gilt wie dessen übrige Shell-Konfiguration als vertrauenswürdig.

## Ausführung

Keine; CLITheme startet keine fremden Befehle.
