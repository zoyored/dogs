from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "Canitrail_Masterkalender_2026_2027.csv"
JSON_PATH = ROOT / "data" / "events.json"
CALENDAR_ROOT = ROOT / "calendar"

EXPECTED_COLUMNS = [
    "Date",
    "Country",
    "Event",
    "Dog distance (km)",
    "Elevation (m+)",
    "Dog access",
    "Status",
    "Notes",
    "Primary source",
    "Secondary source",
    "Origin",
]

DATE_RANGE_RE = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\s*$")
DATE_SINGLE_RE = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})\s*$")


def parse_date_field(value: str) -> tuple[date, date]:
    value = (value or "").strip()
    m = DATE_RANGE_RE.match(value)
    if m:
        start = date.fromisoformat(m.group(1))
        end = date.fromisoformat(m.group(2))
        if end < start:
            raise ValueError(f"Date range ends before it starts: {value}")
        return start, end

    m = DATE_SINGLE_RE.match(value)
    if m:
        d = date.fromisoformat(m.group(1))
        return d, d

    raise ValueError(f"Unsupported Date value: {value!r}")


def split_numeric_or_text(value: str) -> tuple[list[float], str | None]:
    """
    Converts simple pipe-separated numeric values such as '10|15|20'
    into [10, 15, 20]. Mixed/free-text values are preserved in text.
    """
    value = (value or "").strip()
    if not value:
        return [], None

    parts = [p.strip() for p in value.split("|")]
    numbers: list[float] = []

    for part in parts:
        try:
            numbers.append(float(part))
        except ValueError:
            return [], value

    return numbers, None


def clean_number(n: float):
    return int(n) if n.is_integer() else n


def slugify(text: str) -> str:
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
        "ß": "ss", "’": "", "'": "",
        "–": "-", "—": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def make_event_id(start: date, event_name: str, country: str) -> str:
    base = f"{start.isoformat()}-{slugify(event_name)}"
    digest = hashlib.sha1(f"{event_name}|{country}".encode("utf-8")).hexdigest()[:6]
    return f"{base}-{digest}"


def ics_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\r\n", r"\n")
        .replace("\n", r"\n")
    )


def fold_ics_line(line: str, limit: int = 73) -> list[str]:
    """
    Fold ICS lines conservatively. RFC 5545 specifies octets; for this
    small UTF-8 feed this implementation stays safely below the usual limit.
    """
    if len(line) <= limit:
        return [line]
    out = [line[:limit]]
    rest = line[limit:]
    while rest:
        out.append(" " + rest[:limit - 1])
        rest = rest[limit - 1:]
    return out


def event_description(event: dict) -> str:
    parts = []
    if event["distancesKm"]:
        ds = " / ".join(f"{d:g} km" for d in event["distancesKm"])
        parts.append(f"Distanzen: {ds}")
    elif event.get("distanceText"):
        parts.append(f"Distanz: {event['distanceText']}")

    if event["elevationM"]:
        hs = " / ".join(f"{h:g} hm" for h in event["elevationM"])
        parts.append(f"Höhenmeter: {hs}")
    elif event.get("elevationText"):
        parts.append(f"Höhenmeter: {event['elevationText']}")

    if event.get("dogAccess"):
        parts.append(f"Hund: {event['dogAccess']}")
    if event.get("status"):
        parts.append(f"Status: {event['status']}")
    if event.get("notes"):
        parts.append(event["notes"])
    if event.get("secondarySource"):
        parts.append(f"Weitere Quelle: {event['secondarySource']}")
    return "\n".join(parts)


def write_ics(events: list[dict], year: int) -> Path:
    out_dir = CALENDAR_ROOT / str(year)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"canicross-canitrail-{year}.ics"

    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Sandsturm//Canicross Canitrail Events//DE",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Canicross & Canitrail Events",
        "X-WR-CALDESC:Canicross- und Canitrail-Veranstaltungen",
    ]

    for e in events:
        start = date.fromisoformat(e["date"])
        end = date.fromisoformat(e["dateEnd"]) if e.get("dateEnd") else start

        # All-day DTEND is exclusive.
        end_exclusive = end + timedelta(days=1)

        uid = f"{e['id']}@sandsturm.com"
        location = e.get("country") or ""
        url = e.get("primarySource") or ""
        description = event_description(e)

        event_lines = [
            "BEGIN:VEVENT",
            f"UID:{ics_escape(uid)}",
            f"DTSTAMP:{now}",
            f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{end_exclusive.strftime('%Y%m%d')}",
            f"SUMMARY:{ics_escape(e['event'])}",
            f"LOCATION:{ics_escape(location)}",
        ]
        if description:
            event_lines.append(f"DESCRIPTION:{ics_escape(description)}")
        if url:
            event_lines.append(f"URL:{url}")
        event_lines.append("END:VEVENT")

        for line in event_lines:
            lines.extend(fold_ics_line(line))

    lines.append("END:VCALENDAR")
    out_path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    return out_path


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing CSV: {CSV_PATH}")

    events: list[dict] = []

    # utf-8-sig removes the BOM in the current source CSV.
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise SystemExit(
                "Unexpected CSV schema.\n"
                f"Expected: {EXPECTED_COLUMNS}\n"
                f"Found:    {reader.fieldnames}"
            )

        for line_no, row in enumerate(reader, start=2):
            try:
                start, end = parse_date_field(row["Date"])
            except Exception as exc:
                raise SystemExit(f"CSV line {line_no}: {exc}") from exc

            distance_values, distance_text = split_numeric_or_text(row["Dog distance (km)"])
            elevation_values, elevation_text = split_numeric_or_text(row["Elevation (m+)"])

            event = {
                "id": make_event_id(start, row["Event"].strip(), row["Country"].strip()),
                "date": start.isoformat(),
                "dateEnd": end.isoformat() if end != start else None,
                "country": row["Country"].strip(),
                "event": row["Event"].strip(),
                "distancesKm": [clean_number(x) for x in distance_values],
                "elevationM": [clean_number(x) for x in elevation_values],
                "dogAccess": row["Dog access"].strip(),
                "status": row["Status"].strip(),
                "notes": row["Notes"].strip(),
                "primarySource": row["Primary source"].strip() or None,
                "secondarySource": row["Secondary source"].strip() or None,
                "origin": row["Origin"].strip(),
            }
            if distance_text:
                event["distanceText"] = distance_text
            if elevation_text:
                event["elevationText"] = elevation_text

            events.append(event)

    events.sort(key=lambda e: (e["date"], e["event"].casefold()))

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "title": "Canicross & Canitrail Events",
            "description": "Canicross- und Canitrail-Veranstaltungen mit Schwerpunkt Europa.",
            "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "source": str(CSV_PATH.relative_to(ROOT)),
            "count": len(events),
        },
        "events": events,
    }
    JSON_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    by_year: dict[int, list[dict]] = defaultdict(list)
    for event in events:
        start = date.fromisoformat(event["date"])
        end = date.fromisoformat(event["dateEnd"]) if event.get("dateEnd") else start
        for year in range(start.year, end.year + 1):
            by_year[year].append(event)

    written = [JSON_PATH]
    for year, year_events in sorted(by_year.items()):
        written.append(write_ics(year_events, year))

    print(f"Generated {len(events)} events.")
    for path in written:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
