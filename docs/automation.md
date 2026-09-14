# Event-Automation für den Dogs-Masterkalender

## Ziel

Der Masterkalender soll sich weitgehend selbst aktuell halten. Bereits bekannte Events werden täglich gegen ihre Quellen geprüft. Neue Events werden in einem separaten, weniger häufig laufenden Discovery-Prozess gesucht. Eindeutige technische Änderungen können automatisiert verarbeitet werden; komplexe oder mehrdeutige Änderungen werden durch eine KI-Auswertung klassifiziert und anschließend nachvollziehbar als Pull Request vorgeschlagen.

Wichtig: Die Quelle bleibt maßgeblich. Die KI soll keine Eventdaten erfinden, sondern Informationen aus vorhandenen Quellen strukturieren, vergleichen und Unsicherheiten kennzeichnen.

## Grundarchitektur

```text
source-master.csv
      |
      +--> Daily Event Monitor
      |       +--> bekannte Event-URLs abrufen
      |       +--> Änderungen erkennen
      |       +--> strukturierte Felder vergleichen
      |       +--> bei Bedarf KI-Auswertung
      |       +--> Masterkalender aktualisieren
      |       +--> Prüfbericht erzeugen
      |       +--> Pull Request erstellen
      |
      +--> Weekly Event Discovery
              +--> Quellen nach neuen Events durchsuchen
              +--> Kandidaten normalisieren
              +--> Dubletten erkennen
              +--> bei Bedarf KI-Auswertung
              +--> neue Events vorschlagen
              +--> Pull Request erstellen
```

## 1. Täglicher Workflow: bekannte Events überwachen

Vorgeschlagene Datei: `.github/workflows/event-monitor-daily.yml`

### Trigger

- automatisch einmal täglich per `schedule`
- zusätzlich `workflow_dispatch`, damit der Lauf jederzeit manuell gestartet werden kann
- GitHub-Cron arbeitet in UTC

### Aufgabe

Der Workflow liest alle relevanten Events aus dem Masterkalender und prüft die zugehörigen Quellen auf Änderungen, insbesondere:

- Eventname, Veranstalter, Datum/Zeitraum und Startzeit
- Ort und Land
- Kategorie, Distanzen, Höhenmeter und Disziplinen
- Anmeldestatus: noch nicht geöffnet, offen, Warteliste, geschlossen, ausverkauft/voll
- Eventstatus: angekündigt, bestätigt, verschoben, abgesagt, durchgeführt
- Änderungen an Strecke oder Reglement
- offizielle Event- und Registrierungs-URL
- sonstige teilnehmerrelevante Änderungen

### Statusmodell

Mittelfristig sollten Statusinformationen strukturiert gespeichert werden. Denkbare Felder:

```text
status = announced | confirmed | registration_open | sold_out | postponed | cancelled | completed | unknown
registration_status = not_open | open | waitlist | closed | sold_out | unknown
last_checked = ISO timestamp
last_changed = ISO timestamp
source_url = URL
source_checked = URL
verification = automatic | ai_assisted | manual
confidence = high | medium | low
```

Die endgültigen Feldnamen werden vor der Implementierung an das vorhandene CSV-Schema angepasst.

## 2. Mehrstufige Änderungserkennung

Nicht jede Seite soll täglich vollständig durch eine KI geschickt werden.

### Stufe A – Abruf

Soweit technisch und rechtlich sinnvoll werden HTTP-Metadaten und Inhalt geprüft. Zur Optimierung können `ETag`, `Last-Modified`, Content-Hash oder ein Hash des relevanten Seitenbereichs verwendet werden. Hat sich nichts geändert, ist für dieses Event kein KI-Aufruf erforderlich.

### Stufe B – deterministische Prüfung

Bei geänderten Seiten versucht ein Parser zunächst, Informationen ohne KI zu erkennen, z. B. Datumsfelder, JSON-LD/Schema.org-Eventdaten, bekannte Tabellen, Registrierungsstatus, eindeutige Schlüsselwörter, APIs oder strukturierte Feeds.

### Stufe C – KI-Auswertung

Nur relevante oder nicht eindeutig interpretierbare Änderungen werden an ein KI-Modell gegeben. Die Aufgabe ist begrenzt auf den Vergleich von bisherigem Datensatz, aktueller Quelle und gegebenenfalls vorherigem Snapshot. Die Antwort soll strikt strukturiert sein, beispielsweise:

```json
{
  "changed": true,
  "changes": [
    {
      "field": "registration_status",
      "old": "open",
      "new": "sold_out",
      "evidence": "Registration is now marked sold out",
      "confidence": "high"
    }
  ],
  "needs_manual_review": false
}
```

## 3. Sicherheitsprinzip für KI-Änderungen

1. Jede vorgeschlagene Änderung benötigt eine Quelle.
2. Fehlende Informationen werden nicht geraten.
3. Unsichere Aussagen werden als `needs_manual_review` markiert.
4. Eine verschwundene Webseite allein bedeutet nicht, dass das Event abgesagt wurde.
5. Kritische Änderungen wie Absage, Datumsverschiebung oder Ortswechsel benötigen besonders belastbare Evidenz.
6. Bei widersprüchlichen Quellen wird nicht automatisch überschrieben.
7. Originalquelle und Prüfzeitpunkt bleiben nachvollziehbar.

## 4. Pull Request statt blindem Schreiben nach main

Änderungen werden auf einem automatisch erzeugten Branch gesammelt, beispielsweise `automation/event-monitor-2026-09-14`, und anschließend als Pull Request vorgeschlagen.

Beispielbericht:

```text
Daily Event Monitor

Checked: 312 events
Unchanged: 296
Changed: 9
New status information: 5
Needs manual review: 2
Fetch errors: 5

Important changes:
- Example Trail: registration open -> sold out
- Example Canicross: 12.10.2026 -> 19.10.2026
- Example Stage Race: marked cancelled
```

Damit bleibt jede Änderung über Git nachvollziehbar und wird vor dem Merge sichtbar.

## 5. Vertrauensstufen und Auto-Merge

Für die erste Version wird grundsätzlich ein PR erstellt. Später kann selektives Auto-Merge erwogen werden:

- **HIGH:** eindeutig strukturierte offizielle Quelle
- **MEDIUM:** eindeutige Änderung auf offizieller Seite, durch KI klassifiziert
- **LOW:** widersprüchliche oder unklare Angaben

LOW wird niemals automatisch gemergt. Absagen und Datumsverschiebungen sollten zumindest in der Einführungsphase ebenfalls immer geprüft werden.

## 6. Wöchentlicher Workflow: neue Events entdecken

Vorgeschlagene Datei: `.github/workflows/event-discovery-weekly.yml`

Trigger: einmal pro Woche sowie manuell über `workflow_dispatch`.

Dieser Workflow verarbeitet `source-master.csv` und sucht nach Events, die noch nicht im Masterkalender vorhanden sind. Typische Quellen sind Finishers, FFST, VDSV, nationale Verbände, Veranstalterkalender, Rennserien, Canicross-/Canitrail-Portale und weitere bereits dokumentierte Quellen.

```text
Quelle laden
 -> Eventkandidaten extrahieren
 -> normalisieren
 -> gegen Masterkalender vergleichen
 -> Dublettenprüfung
 -> neue Kandidaten validieren
 -> ggf. KI-Klassifizierung
 -> Masterkalender ergänzen
 -> PR erstellen
```

## 7. Dublettenerkennung

Eine reine Namensprüfung reicht nicht. Vergleichsmerkmale sind normalisierter Eventname, Datum, Ort, Land, Veranstalter, Event-URL und Distanzen. Die Erkennung sollte einen Ähnlichkeitswert erzeugen. Als anfängliche Orientierung:

```text
0.95–1.00 -> sehr wahrscheinlich identisch
0.80–0.95 -> prüfen
< 0.80     -> wahrscheinlich neues Event
```

Die Grenzwerte werden anhand echter Daten kalibriert.

## 8. Snapshots und Prüfhistorie

Der Monitor benötigt einen kleinen technischen Zustand, beispielsweise:

```text
data/
  events-master.csv
  source-master.csv
  monitoring/
    state.json
    snapshots/
```

`state.json` könnte je Event `last_checked`, `content_hash`, `etag`, `last_modified` und `last_status` enthalten. Komplette HTML-Snapshots sollten wahrscheinlich nicht dauerhaft im Git-Repository liegen; normalisierte Inhalte/Hashes können langfristig gespeichert und Rohdaten als kurzlebige Workflow-Artefakte behandelt werden.

## 9. Fehlerbehandlung

Ein fehlgeschlagener Abruf darf niemals als Eventänderung interpretiert werden. Zu unterscheiden sind mindestens erfolgreiche Abrufe, Weiterleitungen, 404, 403/Bot-Schutz, 429/Rate-Limit, Timeout, Netzwerkfehler, Parserfehler und KI-Fehler. Bei Fehlern bleibt der bisherige Kalendereintrag unverändert. Wiederholte Fehler werden im Monitoring-Bericht zur manuellen Prüfung markiert.

## 10. KI-Anbindung aus GitHub Actions

Ein GitHub Actions Runner kann eine externe KI-API aufrufen. Die ChatGPT-Webanwendung selbst wird dabei nicht aus dem Runner heraus gesteuert.

```text
GitHub Action
   +--> Python/Node Script
           +--> API Request an KI-Modell
           +--> strukturierte JSON-Antwort
           +--> Validierung
           +--> Änderungsvorschlag
```

API-Schlüssel gehören ausschließlich in GitHub Secrets und niemals ins Repository, z. B. `OPENAI_API_KEY`.

## 11. Kostenkontrolle

Bei mehreren hundert Events darf nicht jeder tägliche Check automatisch einen KI-Aufruf auslösen:

```text
alle Events
   +-- keine Seitenänderung --> fertig
   +-- Änderung
          +-- Parser eindeutig --> ohne KI
          +-- Parser unklar --> KI
```

Zusätzlich sollten maximale KI-Aufrufe bzw. ein Kosten-/Tokenlimit pro Lauf konfigurierbar sein. Überzählige Fälle werden zur späteren oder manuellen Prüfung vorgemerkt.

## 12. Vorgeschlagene Projektstruktur

Die Struktur wird vor der Implementierung gegen das aktuelle Repository geprüft. Zielbild:

```text
.github/
  workflows/
    event-monitor-daily.yml
    event-discovery-weekly.yml
scripts/
  events/
    monitor.py
    discover.py
    fetch.py
    parse.py
    compare.py
    deduplicate.py
    ai_review.py
    report.py
config/
  monitoring.yml
data/
  events-master.csv
  source-master.csv
  monitoring/
    state.json
docs/
  automation.md
```

Bestehende Generatoren und Datenpfade werden wiederverwendet; es soll keine parallele zweite Kalenderstruktur entstehen.

## 13. Konfiguration

Beispiel für `config/monitoring.yml`:

```yaml
monitor:
  include_past_events: false
  days_after_event: 7
  request_timeout: 20
  max_retries: 2
  concurrency: 5
ai:
  enabled: true
  max_reviews_per_run: 30
pull_request:
  enabled: true
  auto_merge: false
```

## 14. Umgang mit vergangenen Events

Vorschlag: Events bis sieben Tage nach Veranstaltungsende täglich prüfen und danach aus dem Daily Monitor nehmen. Der historische Datensatz bleibt im Masterkalender erhalten.

## 15. Reihenfolge der Implementierung

1. **Read-only Monitor:** prüfen und Report erzeugen, noch keine CSV-Änderungen.
2. **PR-basierte Änderungen:** Änderungen auf Branch erzeugen und als PR vorschlagen, kein Auto-Merge.
3. **KI-Eskalation:** nur unklare geänderte Quellen gezielt durch KI bewerten.
4. **Weekly Discovery:** neue Events automatisiert aus `source-master.csv` suchen und als PR vorschlagen.
5. **Selektive Automatisierung:** nach ausreichender Erfahrung sehr sichere, nicht kritische Änderungen optional automatisch mergen.

## 16. Vor der Implementierung zu klären

- exakter Pfad und aktuelles Schema des Masterkalenders
- exakter Pfad und Schema von `source-master.csv`
- stabile Event-ID definieren bzw. vorhandene ID prüfen
- direkt automatisiert abrufbare Quellen
- Quellen mit JavaScript/Browser-Anforderung
- Rate-Limits und Nutzungsbedingungen der Quellen
- Statusfelder für öffentlichen Kalender
- Darstellung von Statusinformationen in ICS und Website
- Uhrzeit des Daily Runs
- Wochentag des Discovery Runs
- Wahl des KI-Modells und Kostenlimit
- Regeln für späteres Auto-Merge

## 17. Zielzustand

Der Dogs-Masterkalender besitzt langfristig drei Ebenen:

1. **Discovery** – neue relevante Hunde-Laufevents finden.
2. **Monitoring** – bekannte Events kontinuierlich auf Änderungen überwachen.
3. **Review** – unklare oder kritische Änderungen nachvollziehbar prüfen.

Damit wird der Masterkalender zu einer kontinuierlich gepflegten Eventdatenbank, aus der Website, JSON und ICS automatisiert erzeugt werden können.
