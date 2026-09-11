# Quellen und Pflegehinweise

Die Primär- und Sekundärquellen zu einzelnen Veranstaltungen stehen direkt in der Master-CSV unter `data/`.

## Statuskonventionen

- **confirmed / date confirmed / registration open**: Termin bzw. Veranstaltung aktuell bestätigt.
- **announced**: angekündigt, aber einzelne Details können noch fehlen.
- **month/period published**: nur Monat oder Zeitraum bekannt; im Kalender als vorläufig behandeln.
- **TENTATIVE** in der ICS: kein verlässliches exaktes Veranstaltungsdatum.

## Pflege

Bei Änderungen möglichst zuerst die Masterdaten aktualisieren und anschließend die ICS neu erzeugen. Bereits vergebene Event-UIDs sollten bei reinen Termin- oder Detailänderungen stabil bleiben, damit Kalender-Abonnements keine Duplikate erzeugen.
