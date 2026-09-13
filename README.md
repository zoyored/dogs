# Canicross & Canitrail Event Calendar

Öffentlicher Kalender für Canicross-, Canitrail- und hundefreundliche Trail-Veranstaltungen mit Schwerpunkt Europa.

## Kalender abonnieren

Die erzeugten iCalendar-Dateien liegen im Verzeichnis `calendar/`.

2026:

`https://zoyored.github.io/dogs/calendar/2026/canicross-canitrail-2026.ics`

2027:

`https://zoyored.github.io/dogs/calendar/2027/canicross-canitrail-2027.ics`

Auf iPhone/iPad können diese URLs als abonnierte Kalender hinzugefügt werden. Änderungen an den erzeugten ICS-Dateien werden anschließend über dieselben URLs veröffentlicht.

> Hinweis: Der URL-Bestandteil `/dogs/` stammt vom Repository-Namen `zoyored/dogs`. Er bezeichnet **kein** Unterverzeichnis `dogs/` im Repository.

## Repository-Struktur

```text
.
├── .github/
│   └── workflows/
│       └── build-events.yml
├── calendar/
│   ├── 2026/
│   │   └── canicross-canitrail-2026.ics
│   └── 2027/
│       └── canicross-canitrail-2027.ics
├── data/
│   ├── Canitrail_Masterkalender_2026_2027.csv
│   ├── events.json
│   └── source-master.csv
├── scripts/
│   ├── build_events.py
│   └── dedupe_master.py
├── LICENSE
└── README.md
```

## Datenfluss

`data/Canitrail_Masterkalender_2026_2027.csv` ist die zentrale Datenquelle.

Bei Änderungen am Masterkalender startet der GitHub-Actions-Workflow `Build event feeds` automatisch und führt folgende Schritte aus:

1. `scripts/dedupe_master.py` erkennt doppelte Events anhand von Datum/Zeitraum, Land und normalisiertem Eventnamen und führt deren Daten zusammen.
2. `scripts/build_events.py` erzeugt daraus `data/events.json`.
3. Für jedes enthaltene Jahr werden die ICS-Dateien unter `calendar/<Jahr>/` neu erzeugt.
4. Geänderte Master-, JSON- und Kalenderdateien werden automatisch zurück nach `main` committed.

Die Dateien `data/events.json` und `calendar/**/*.ics` sind damit **generierte Dateien** und sollten nicht manuell gepflegt werden.

## Datenpflege

Neue und korrigierte Veranstaltungen werden ausschließlich im Masterkalender gepflegt:

`data/Canitrail_Masterkalender_2026_2027.csv`

Der Masterkalender enthält unter anderem Datum, Land, Eventname, Kategorie, Distanz, Höhenmeter, Hundezugang, Status, Hinweise und Quellen.

`data/source-master.csv` dient als ergänzende Quellen-/Importbasis.

## GitHub Pages

Wenn die Kalenderdateien über GitHub Pages ausgeliefert werden, sollte Pages den Branch `main` aus dem Repository-Root (`/`) veröffentlichen. Die öffentlichen URLs enthalten aufgrund des Repository-Namens weiterhin den Pfad `/dogs/`, zum Beispiel:

`https://zoyored.github.io/dogs/calendar/2027/canicross-canitrail-2027.ics`

Ein zusätzliches Repository-Unterverzeichnis `dogs/` wird dafür nicht benötigt.

## Automatisierung

Der Workflow befindet sich unter:

`.github/workflows/build-events.yml`

Er kann zusätzlich manuell über **Actions → Build event feeds → Run workflow** gestartet werden.
