# Event calendar automation

This document describes the automated validation and review pipeline for the Canitrail/Canicross master calendar.

## Goals and safety model

The automation detects source problems and possible event changes, prepares review proposals, records an explicit human decision, and only then changes the master calendar.

The central safety rules are:

- validation findings are signals for review, not proof that an event is wrong;
- Phases 1–3 never change or delete master-calendar rows;
- HTTP 404/410 means "replace source or investigate cancellation", not "event cancelled";
- master changes require an explicit human approval and an explicit field/value patch;
- deletion is not supported by the automated apply step;
- every write to protected `main` goes through a pull request;
- generated JSON/ICS feeds must match the master before a PR can be merged;
- the final calendar change is never auto-merged.

## Important files

| Purpose | File |
|---|---|
| Master calendar | `data/Canitrail_Masterkalender_2026_2027.csv` |
| Validation state | `data/event-validation.csv` |
| Proposal queue | `data/event-update-proposals.csv` |
| Approved patches | `data/event-approved-changes.csv` |
| Generated event JSON | `data/events.json` |
| Generated calendars | `calendar/<year>/canicross-canitrail-<year>.ics` |
| Latest validation report | `reports/event-validation/latest.md` |
| Proposal report | `reports/event-validation/proposals.md` |

## End-to-end flow

```text
Phase 1: full source audit
          |
          v
Phase 2: daily validation
          |
          v
validation-state PR
          |
       human merge
          |
          v
Phase 3: build proposals
          |
          v
proposal-queue PR
          |
       human merge
          |
          v
Phase 5: human approve/reject
          |
          v
review-decision PR
          |
       human merge
          |
          +---------------- reject ----------------> finished
          |
        approve
          |
          v
Phase 4: apply approved patch
          |
          v
final calendar PR
          |
       human review + merge
          |
          v
master + JSON + ICS updated
```

The phase numbering reflects the order in which the implementation was designed. Operationally, Phase 5 is the human gate before Phase 4.

## Phase 1 — Full master source audit

Phase 1 is the broad audit mechanism for checking the master calendar and its sources. It is intentionally conservative and must not directly change event data.

Relevant files:

- `scripts/audit_master_sources.py`
- `.github/workflows/full-master-source-audit.yml`

Use Phase 1 for a broad/full source review rather than the bounded daily rotation.

Note: the Phase 1 workflow predates the current protected-main pipeline and should be reviewed separately before relying on it as a routine production workflow.

## Phase 2 — Daily event validation

Workflow:

`.github/workflows/daily-event-validation.yml`

Validator:

`scripts/validate_events.py`

The scheduled run targets 05:30 Europe/Berlin. GitHub cron uses UTC, so two UTC slots plus a timezone guard cover CET and CEST. A manual workflow dispatch is also available; the `full` input checks all master rows.

The normal daily run checks a bounded set of rows, default 25, while previously flagged rows and near-term events receive priority.

The validator records, among other things:

- HTTP status and final URL;
- event-name token match;
- year/date marker;
- dog-discipline/access marker;
- source fingerprint;
- review flag and reason;
- last checked date.

New/unseen rows remain in the review queue until they have been checked.

A source fingerprint change is a review signal only.

### Phase 2 output

Phase 2 writes:

- `data/event-validation.csv`
- `reports/event-validation/latest.md`

If those files change, the workflow creates a branch named approximately:

`automation/event-validation-<run-id>`

and opens the PR:

`Update daily event validation`

The validation state reaches `main` only after the required check passes and the PR is merged.

## Phase 3 — Build event update proposals

Workflow:

`.github/workflows/event-update-proposals.yml`

Script:

`scripts/build_update_proposals.py`

Phase 3 starts automatically when `data/event-validation.csv` is merged/pushed to `main`. It can also be dispatched manually.

It converts rows with `Review required == true` into stable proposals. Proposal IDs are deterministic hashes of:

`Date | Country | Event | Primary source`

Example:

`EV-AD5CCC65AC`

Possible proposal actions currently include:

- `find-source`
- `replace-source-or-confirm-cancelled`
- `manual-source-check`
- `review-source-change`
- `verify-date`
- `verify-dog-eligibility`
- `verify-event-identity`
- `manual-document-review`
- `await-validation`
- `manual-review`

### Important interpretation

A proposal is not a requested automatic edit. It is a review item.

In particular:

- 404/410 does not prove cancellation;
- a missing date marker does not prove the stored date is wrong;
- a weak event-name match does not prove the event is wrong;
- missing dog-related text does not prove dogs are not allowed.

The current deterministic checks can produce false positives, especially for date and event-identity checks. Human/source verification is therefore mandatory before approval.

### Phase 3 output

Phase 3 writes:

- `data/event-update-proposals.csv`
- `reports/event-validation/proposals.md`

If changed, it creates:

`automation/event-proposals-<run-id>`

and opens:

`Update event review proposals`

Merge this PR only after the required validation check passes.

## Phase 5 — Human review

Workflow:

`.github/workflows/review-event-proposal.yml`

Script:

`scripts/review_event_proposal.py`

Run the workflow manually from GitHub Actions.

Inputs:

| Input | Meaning |
|---|---|
| `proposal_id` | Proposal such as `EV-AD5CCC65AC` |
| `decision` | `approve` or `reject` |
| `field` | Master field to change; required for approval |
| `new_value` | Exact new value; required for approval |
| `source` | Evidence/source URL |
| `note` | Reviewer explanation |

Allowed patch fields are:

`Date`, `Country`, `Event`, `Category`, `Dog distance (km)`, `Elevation (m+)`, `Dog access`, `Status`, `Notes`, `Primary source`, `Secondary source`, `Origin`.

### Approve

Approval:

1. changes the proposal's `Review status` to `approved`;
2. writes the explicit field/value patch to `data/event-approved-changes.csv`;
3. records source and reviewer note;
4. creates `automation/event-review-<run-id>`;
5. opens `Review event proposal <proposal-id>`.

No master row is changed at this point.

Multiple approved fields for one proposal are supported. Each field is stored as a separate patch.

### Reject

Rejection:

1. changes the proposal's `Review status` to `rejected`;
2. removes any approved-change rows for that proposal;
3. creates the same protected review-decision PR flow.

A reject must never change the master calendar.

## Phase 4 — Apply approved changes

Workflow:

`.github/workflows/create-approved-event-pr.yml`

Script:

`scripts/apply_approved_changes.py`

Phase 4 starts when `data/event-approved-changes.csv` changes on `main`, normally after an approved Phase 5 review PR is merged. Manual dispatch is also available.

The script:

1. loads proposals marked `approved`;
2. loads explicit patches from `data/event-approved-changes.csv`;
3. groups patches by Proposal ID;
4. finds the original master row exactly once using the proposal's Date/Country/Event identity;
5. requires exactly one matching row;
6. applies only allow-listed fields;
7. never deletes a row;
8. stamps `Origin` as `approved proposal <proposal-id> <date>` unless Origin itself is being patched;
9. runs `scripts/dedupe_master.py`;
10. rebuilds JSON and ICS with `scripts/build_events.py`.

Grouping patches by proposal is important: if an approved patch changes Date, Country, or Event, later patches for the same proposal still apply to the already-resolved row.

If the approved patches produce no master change, Phase 4 stops without creating a branch or PR.

If there is a real change, Phase 4 creates:

`automation/approved-event-changes-<run-id>`

and opens:

`Apply approved event updates`

This is the final calendar-change PR. It is deliberately not auto-merged.

## Required validation check

Workflow:

`.github/workflows/build-events.yml`

Required check:

`Validate event data and generated feeds`

The check is read-only. It:

1. checks the master for duplicates/normalization problems;
2. rebuilds `data/events.json` and the calendar files;
3. validates the JSON;
4. verifies that the rebuilt generated files exactly match what is committed.

If generated feeds are stale or the master needs deduplication, the PR fails.

This check is required on the protected `main` branch for the automation-state PRs and final calendar PRs covered by the workflow path filters.

## Normal operating procedure

### Daily validation

1. Phase 2 runs automatically.
2. Review the `Update daily event validation` PR.
3. Wait for `Validate event data and generated feeds` to pass.
4. Merge the validation PR.
5. Phase 3 automatically builds proposals.
6. Review and merge the proposal-queue PR after its required check passes.

### Reviewing a proposal

First verify the event against reliable source evidence. Do not approve solely because the deterministic validator raised a flag.

For a correct proposed edit:

1. open Actions → `Review event proposal`;
2. enter Proposal ID;
3. choose `approve`;
4. select exactly one field and enter the exact new value;
5. enter the evidence URL and a useful reviewer note;
6. run the workflow;
7. review the generated review-decision PR;
8. merge it after the required check passes;
9. Phase 4 creates the final calendar PR;
10. inspect the actual master, JSON and ICS diff;
11. merge only after the required check passes.

For a false positive or unsupported change:

1. run `Review event proposal`;
2. choose `reject`;
3. explain the reason in the note;
4. review and merge the generated decision PR.

No final calendar PR should be produced for a reject.

## Tested end-to-end cases — 2026-09-21

### Reject path

Proposal:

`EV-D83A2F63FC — RAID Cani-Trail`

The stored primary source returned HTTP 404. No reliable evidence established that the event was cancelled or that the master data itself was wrong.

Decision: `reject`.

Result:

- review decision was recorded;
- review PR was generated;
- master calendar was not changed;
- Phase 4 found no actionable patch and produced no final calendar PR.

This confirms the rule that a dead source must not automatically cancel or delete an event.

### Approve path

Proposal:

`EV-AD5CCC65AC — Canitrail des Moines`

Verified change:

`Dog distance (km): not published -> 10|8.5`

Result:

- approval was recorded;
- review-decision PR was generated and merged;
- Phase 4 started from the merged approval state;
- the final `Apply approved event updates` PR was generated;
- master, JSON and ICS were rebuilt consistently;
- the required validation check passed;
- the final PR was manually merged.

This confirms the complete protected-main approve flow.

## Known limitations and follow-up work

### False-positive proposals

The current validator uses deterministic text matching. Some `verify-date` and `verify-event-identity` proposals are false positives even when the source is correct. Future improvements should make source parsing more event-aware before increasing automation.

### Reject can technically trigger Phase 4

A reject may rewrite `data/event-approved-changes.csv` even when its logical contents remain empty or unchanged, for example because of newline normalization. Since Phase 4 watches that file on `main`, the workflow can start unnecessarily.

This is safe because `apply_approved_changes.py` detects that there is no actionable approved patch and creates no calendar PR. It is nevertheless unnecessary work and should be cleaned up by avoiding no-op rewrites of the approved-change file.

### Source disappearance

A dead source must be handled conservatively. Prefer finding a replacement official/reliable source or recording that verification is required. Do not infer cancellation from HTTP status alone.

### Human gates are intentional

There are two meaningful approvals for an accepted change:

1. approve the proposal/evidence;
2. approve the final concrete master/generated-feed PR.

This is intentional. The first answers "is this change justified?" The second answers "was the justified change applied correctly?"

## GitHub repository setting

For automation-created pull requests, the repository must allow GitHub Actions to create/approve pull requests under:

`Settings → Actions → General → Workflow permissions`

The pipeline requires permission to create PRs; branch protection still provides the human merge gate.

## Design principle

The master calendar is the source of truth. Automated source checks may discover problems, but uncertainty must move into a review queue rather than directly into production data. The system is designed to prefer a missed automatic edit over an unsupported destructive change.
