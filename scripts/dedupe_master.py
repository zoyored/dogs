from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "Canitrail_Masterkalender_2026_2027.csv"

EXPECTED_COLUMNS = [
    "Date",
    "Country",
    "Event",
    "Category",
    "Dog distance (km)",
    "Elevation (m+)",
    "Dog access",
    "Status",
    "Notes",
    "Primary source",
    "Secondary source",
    "Origin",
]

PIPE_FIELDS = {"Category", "Dog distance (km)", "Elevation (m+)"}
TEXT_MERGE_FIELDS = {"Dog access", "Notes", "Origin"}
SOURCE_FIELDS = ("Primary source", "Secondary source")


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def normalize_event_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = value.replace("–", "-").replace("—", "-").replace("’", "'")
    value = value.casefold()
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return normalize_space(value)


def duplicate_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        normalize_space(row.get("Date", "")).casefold(),
        normalize_space(row.get("Country", "")).casefold(),
        normalize_event_name(row.get("Event", "")),
    )


def merge_pipe_values(left: str, right: str) -> str:
    values: list[str] = []
    seen: set[str] = set()
    for raw in (left, right):
        for part in (raw or "").split("|"):
            value = normalize_space(part)
            if not value:
                continue
            key = value.casefold()
            if key not in seen:
                seen.add(key)
                values.append(value)
    return "|".join(values)


def merge_text(left: str, right: str) -> str:
    left = normalize_space(left)
    right = normalize_space(right)
    if not left:
        return right
    if not right or right.casefold() == left.casefold():
        return left
    return f"{left} | {right}"


def merge_sources(target: dict[str, str], incoming: dict[str, str]) -> None:
    sources: list[str] = []
    seen: set[str] = set()
    for field in SOURCE_FIELDS:
        for row in (target, incoming):
            value = normalize_space(row.get(field, ""))
            if value and value not in seen:
                seen.add(value)
                sources.append(value)

    target["Primary source"] = sources[0] if sources else ""
    target["Secondary source"] = sources[1] if len(sources) > 1 else ""
    if len(sources) > 2:
        extras = "Additional sources: " + " ; ".join(sources[2:])
        target["Notes"] = merge_text(target.get("Notes", ""), extras)


def merge_row(target: dict[str, str], incoming: dict[str, str]) -> None:
    for field in PIPE_FIELDS:
        target[field] = merge_pipe_values(target.get(field, ""), incoming.get(field, ""))

    for field in TEXT_MERGE_FIELDS:
        target[field] = merge_text(target.get(field, ""), incoming.get(field, ""))

    merge_sources(target, incoming)

    # Prefer existing canonical values, but fill any missing scalar fields.
    for field in EXPECTED_COLUMNS:
        if field in PIPE_FIELDS or field in TEXT_MERGE_FIELDS or field in SOURCE_FIELDS:
            continue
        if not normalize_space(target.get(field, "")) and normalize_space(incoming.get(field, "")):
            target[field] = incoming[field]


def main() -> None:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise SystemExit(
                "Unexpected CSV schema.\n"
                f"Expected: {EXPECTED_COLUMNS}\n"
                f"Found:    {reader.fieldnames}"
            )
        rows = [dict(row) for row in reader]

    deduped: list[dict[str, str]] = []
    by_key: dict[tuple[str, str, str], dict[str, str]] = {}
    duplicate_count = 0

    for row in rows:
        key = duplicate_key(row)
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = row
            deduped.append(row)
            continue

        duplicate_count += 1
        merge_row(existing, row)

    if duplicate_count == 0:
        print(f"No duplicates found in {CSV_PATH.relative_to(ROOT)} ({len(rows)} rows).")
        return

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_COLUMNS, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(deduped)

    print(
        f"Removed {duplicate_count} duplicate row(s) from {CSV_PATH.relative_to(ROOT)}: "
        f"{len(rows)} -> {len(deduped)} rows."
    )


if __name__ == "__main__":
    main()
