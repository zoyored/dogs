# Mitmachen / Contributing

Danke, dass du den Eventkalender verbessern möchtest.

## Kleine Hinweise und Fehler

Für fehlende Events, Terminänderungen, Absagen oder fehlerhafte Angaben kann ein GitHub Issue erstellt werden. Bitte möglichst eine verlässliche Quelle zur Veranstaltung angeben.

## Änderungen per Pull Request

Die veröffentlichte Datenquelle ist `main`. Bitte keine generierten Dateien von Hand bearbeiten.

1. Repository forken oder einen eigenen Branch erstellen.
2. `data/Canitrail_Masterkalender_2026_2027.csv` bearbeiten.
3. Lokal ausführen:

   ```bash
   python scripts/dedupe_master.py
   python scripts/build_events.py
   ```

4. Die Änderung am Masterkalender sowie die daraus erzeugten Änderungen an `data/events.json` und `calendar/` gemeinsam committen.
5. Pull Request gegen `main` öffnen und Quelle(n) sowie Anlass der Änderung beschreiben.

GitHub Actions prüft automatisch, ob der Masterkalender bereits dedupliziert ist, das JSON gültig ist und JSON/ICS exakt aus den eingereichten Masterdaten erzeugt wurden. Der Prüfworkflow besitzt nur Leserechte und verändert den Pull Request oder `main` nicht.

## Review

Pull Requests werden vor dem Merge geprüft. Ein erfolgreicher automatischer Check bedeutet, dass die Daten technisch konsistent sind; er ersetzt nicht die inhaltliche Prüfung der Veranstaltung und ihrer Quelle.

Direkte Änderungen an der produktiven Website sind nicht Teil dieses Repositories.

---

# Contributing

Corrections, missing events and updates are welcome. For a simple report, open an Issue and include a reliable event source whenever possible.

For a Pull Request, edit the master CSV, run `python scripts/dedupe_master.py` and `python scripts/build_events.py`, and commit the master change together with the generated `data/events.json` and `calendar/` changes. Automated read-only checks verify consistency before review and merge into `main`.
