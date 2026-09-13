# Canicross & Canitrail Event Calendar

Öffentlicher Kalender für Canicross-, Canitrail- und hundefreundliche Trail-Veranstaltungen mit Schwerpunkt Europa.

## Mitmachen

Hinweise, Korrekturen und neue Veranstaltungen aus der Community sind ausdrücklich willkommen. Änderungen an den Kalenderdaten sollen über **Issues oder Pull Requests** eingebracht werden. Der Branch `main` ist die veröffentlichte Datenquelle; Änderungen werden vor der Übernahme geprüft.

Details zum Ablauf stehen in [CONTRIBUTING.md](CONTRIBUTING.md).

## Kalender abonnieren

Die erzeugten iCalendar-Dateien liegen im Verzeichnis `calendar/`.

2026:
`https://zoyored.github.io/dogs/calendar/2026/canicross-canitrail-2026.ics`

2027:
`https://zoyored.github.io/dogs/calendar/2027/canicross-canitrail-2027.ics`

Auf iPhone/iPad können diese URLs als abonnierte Kalender hinzugefügt werden. Änderungen an den erzeugten ICS-Dateien werden anschließend über dieselben URLs veröffentlicht.

> Hinweis: Der URL-Bestandteil `/dogs/` stammt vom Repository-Namen `zoyored/dogs`. Er bezeichnet kein Unterverzeichnis `dogs/` im Repository.

## Repository-Struktur

```text
.
├── .github/workflows/build-events.yml
├── calendar/
├── data/
│   ├── Canitrail_Masterkalender_2026_2027.csv
│   ├── events.json
│   └── source-master.csv
├── scripts/
│   ├── build_events.py
│   └── dedupe_master.py
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Datenfluss

`data/Canitrail_Masterkalender_2026_2027.csv` ist die zentrale Datenquelle.

Zu jeder Änderung an den Eventdaten werden die abgeleiteten Dateien bereits im selben Pull Request erzeugt und mit eingecheckt:

1. `python scripts/dedupe_master.py` prüft und bereinigt doppelte Events.
2. `python scripts/build_events.py` erzeugt `data/events.json` und die ICS-Dateien unter `calendar/<Jahr>/`.
3. Der GitHub-Actions-Workflow `Validate event feeds` führt dieselben Prüfungen erneut in einer schreibgeschützten Umgebung aus.
4. Nur wenn Masterdaten und generierte Dateien konsistent sind, ist die Validierung erfolgreich.
5. Nach dem geprüften Merge enthält `main` sofort die vollständige, veröffentlichungsfähige Version.

Der Workflow besitzt nur `contents: read` und schreibt **nicht** selbst nach `main`. Dadurch kann `main` geschützt werden, ohne dass die Automatisierung eine Ausnahme mit Schreibrechten benötigt.

Die Dateien `data/events.json` und `calendar/**/*.ics` sind generierte Dateien und sollten nicht manuell editiert werden.

## Datenpflege

Neue und korrigierte Veranstaltungen werden ausschließlich im Masterkalender gepflegt:

`data/Canitrail_Masterkalender_2026_2027.csv`

`data/source-master.csv` dient als ergänzende Quellen-/Importbasis.

## GitHub Pages

GitHub Pages kann den Branch `main` aus dem Repository-Root (`/`) veröffentlichen. Die öffentlichen URLs enthalten aufgrund des Repository-Namens weiterhin den Pfad `/dogs/`.

## Automatisierung

Der Workflow befindet sich unter `.github/workflows/build-events.yml`.

Er läuft bei passenden Pull Requests und nach Änderungen auf `main` als Konsistenzprüfung. Er kann zusätzlich manuell über **Actions → Validate event feeds → Run workflow** gestartet werden.
