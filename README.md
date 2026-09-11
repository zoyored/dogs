# dogs

Öffentlicher Kalender für Canicross- und Canitrail-Veranstaltungen mit Schwerpunkt Europa.

## Kalender abonnieren

Nach Aktivierung von GitHub Pages ist der 2027-Kalender unter dieser Adresse erreichbar:

`https://zoyored.github.io/dogs/calendar/2027/canicross-canitrail-2027.ics`

Auf iPhone/iPad kann diese URL als abonnierter Kalender hinzugefügt werden. Änderungen an der ICS-Datei werden anschließend über dieselbe URL veröffentlicht.

## Repository-Struktur

```text
.
├── README.md
├── LICENSE
├── data/
│   └── Canitrail_Masterkalender_2026_2027.csv
├── docs/
│   ├── .nojekyll
│   ├── index.html
│   └── calendar/
│       └── 2027/
│           └── canicross-canitrail-2027.ics
└── sources/
    └── README.md
```

## Datenpflege

- `data/` enthält die recherchierten Masterdaten.
- `docs/calendar/` enthält die veröffentlichten Kalenderdateien.
- `sources/` dokumentiert Quellen und Pflegekonventionen.
- Vorläufige Termine werden in der ICS als `TENTATIVE` gekennzeichnet.

## GitHub Pages

GitHub Pages sollte auf **Deploy from a branch** gestellt werden:

- Branch: `main`
- Folder: `/docs`

Danach ist die Kalenderdatei unter der oben genannten URL öffentlich erreichbar.
