# Contributing

Thank you for helping improve the event calendar.

## Reporting corrections and missing events

Open a GitHub Issue for a missing event, date change, cancellation or incorrect detail. Include a reliable event source whenever possible. An inaccessible source alone does not prove that an event has been cancelled.

## Submitting a Pull Request

The published source of truth is `main`. Do not edit generated files manually.

1. Fork the repository or create a branch.
2. Edit `data/Canitrail_Masterkalender_2026_2027.csv`.
3. If you add a recurring federation, organiser or discovery source, also update `data/source-master.csv`.
4. Run locally:

   ```bash
   python scripts/dedupe_master.py
   python scripts/build_events.py
   python -m json.tool data/events.json > /dev/null
   ```

5. Commit the master/source changes together with the generated changes in `data/events.json` and `calendar/`.
6. Open a Pull Request against `main` and describe the evidence and reason for the change.

GitHub Actions verifies that the master calendar is normalized, the JSON is valid, and the committed JSON/ICS files can be reproduced exactly from the submitted master data. This required check is read-only and does not modify the Pull Request or `main`.

## Review requirements

Pull Requests are reviewed before merge. A successful automated check proves technical consistency; it does not replace verification of the event and its sources.

Use official organisers, venues or sports federations as primary evidence whenever available. Discovery calendars may be used to find an event, but event dates, disciplines and dog access should be confirmed from a reliable event-specific source. Record unknown distances or classes as unpublished instead of inferring them.

The automated source validator never changes or deletes master events. Its findings enter the human review process described in [docs/automation.md](docs/automation.md).

Changes to the production website are outside the scope of this repository.
