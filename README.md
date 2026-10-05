# Canicross & Canitrail Event Calendar

Public calendar of Canicross, Canitrail, dog-trail and other dog-sport events, with a focus on Europe.

## Contributing

Community reports, corrections and new events are welcome. Submit calendar changes through **Issues or Pull Requests** and include a reliable source whenever possible. The `main` branch is the published source of truth; changes are reviewed before they are merged.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete workflow.

## Subscribe to the calendars

The generated iCalendar feeds are stored in `calendar/` and published through GitHub Pages:

- 2026: `https://zoyored.github.io/dogs/calendar/2026/canicross-canitrail-2026.ics`
- 2027: `https://zoyored.github.io/dogs/calendar/2027/canicross-canitrail-2027.ics`

On iPhone and iPad, add these URLs as subscribed calendars. Future feed updates are published at the same URLs.

> The `/dogs/` URL segment comes from the repository name `zoyored/dogs`; it is not an additional repository directory.

## Repository layout

```text
.
├── .github/workflows/
│   ├── build-events.yml
│   ├── create-approved-event-pr.yml
│   ├── daily-event-validation.yml
│   ├── event-update-proposals.yml
│   └── review-event-proposal.yml
├── calendar/
├── data/
│   ├── Canitrail_Masterkalender_2026_2027.csv
│   ├── event-approved-changes.csv
│   ├── event-update-proposals.csv
│   ├── event-validation.csv
│   ├── events.json
│   └── source-master.csv
├── docs/
│   ├── automation.md
│   └── dedupe-policy.md
├── reports/event-validation/
├── scripts/
│   ├── apply_approved_changes.py
│   ├── build_events.py
│   ├── build_update_proposals.py
│   ├── dedupe_master.py
│   ├── review_event_proposal.py
│   └── validate_events.py
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Data flow

`data/Canitrail_Masterkalender_2026_2027.csv` is the authoritative event source.

Every event-data change must include the derived files in the same Pull Request:

1. `python scripts/dedupe_master.py` checks and normalizes duplicate events.
2. `python scripts/build_events.py` generates `data/events.json` and the ICS files below `calendar/<year>/`.
3. The read-only GitHub Actions workflow `Validate event feeds` repeats those checks.
4. Validation succeeds only when the master data and committed generated files are consistent.
5. After review and merge, `main` immediately contains a complete publishable version.

The generated files `data/events.json` and `calendar/**/*.ics` must not be edited manually.

## Source and event maintenance

- Add or correct events in `data/Canitrail_Masterkalender_2026_2027.csv`.
- Maintain federation, organiser and discovery sources in `data/source-master.csv`.
- Treat automated validation findings as review signals, not proof that an event is incorrect or cancelled.

The daily GitHub workflow checks event sources automatically, and successful validation-state updates are merged automatically. Unresolved findings enter the proposal queue for human research. Automated checks never directly change or delete master-calendar events.

See [docs/automation.md](docs/automation.md) for the full validation and review process and [docs/dedupe-policy.md](docs/dedupe-policy.md) for event identity rules.

## GitHub Pages

GitHub Pages publishes the repository from the `main` branch and repository root (`/`). Public URLs retain `/dogs/` because it is the repository name.

## Manual validation

The feed consistency workflow can be started from **Actions → Validate event feeds → Run workflow**. A full source audit can be started from **Actions → Daily event validation → Run workflow** with `full=true`.
