# Event deduplication policy

The master calendar is normalized by `scripts/dedupe_master.py` before feeds are built.

## Identity

Two rows are treated as the same event when:

- their canonical country is the same;
- their normalized event name is the same (Unicode/punctuation/case differences and a trailing 2026/2027 edition year are ignored); and
- their date spans overlap. A one-day listing inside a multi-day listing is therefore merged into the broader event span.

## Country cleanup

Country values are Unicode/control-character cleaned, date fragments and surrounding separator debris are removed, and common European aliases/country codes are mapped to one canonical English spelling. Unknown country values are cleaned but are not guessed.

## Sources and organisers

Duplicate rows retain distinct source links in `Primary source` and `Secondary source`; further links are preserved in `Notes`. When independent domains list the same event, the notes explicitly show all listing links.

A source listing is not automatically called an organiser: federation and discovery calendars often list events they do not organise. If research confirms two actual organisers/co-organisers, imports should name both organisers in `Notes` and include their official links in the source fields. The deduper preserves and merges that text rather than discarding it.
