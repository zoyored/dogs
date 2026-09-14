from __future__ import annotations

import csv
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "Canitrail_Masterkalender_2026_2027.csv"

EXPECTED_COLUMNS = [
    "Date", "Country", "Event", "Category", "Dog distance (km)",
    "Elevation (m+)", "Dog access", "Status", "Notes", "Primary source",
    "Secondary source", "Origin",
]

PIPE_FIELDS = {"Category", "Dog distance (km)", "Elevation (m+)"}
TEXT_MERGE_FIELDS = {"Dog access", "Notes", "Origin"}
SOURCE_FIELDS = ("Primary source", "Secondary source")

COUNTRY_ALIASES = {
    "at": "Austria", "austria": "Austria", "osterreich": "Austria", "österreich": "Austria",
    "be": "Belgium", "belgium": "Belgium", "belgie": "Belgium", "belgië": "Belgium", "belgique": "Belgium",
    "bg": "Bulgaria", "bulgaria": "Bulgaria",
    "cz": "Czech Republic", "czech republic": "Czech Republic", "czechia": "Czech Republic", "cesko": "Czech Republic", "česko": "Czech Republic",
    "de": "Germany", "germany": "Germany", "deutschland": "Germany", "allemagne": "Germany",
    "dk": "Denmark", "denmark": "Denmark", "danmark": "Denmark",
    "ee": "Estonia", "estonia": "Estonia",
    "es": "Spain", "spain": "Spain", "espana": "Spain", "españa": "Spain",
    "fi": "Finland", "finland": "Finland",
    "fr": "France", "france": "France", "frankreich": "France",
    "gr": "Greece", "greece": "Greece",
    "hu": "Hungary", "hungary": "Hungary",
    "ie": "Ireland", "ireland": "Ireland",
    "it": "Italy", "italy": "Italy", "italia": "Italy",
    "lt": "Lithuania", "lithuania": "Lithuania",
    "lu": "Luxembourg", "luxembourg": "Luxembourg",
    "lv": "Latvia", "latvia": "Latvia",
    "nl": "Netherlands", "netherlands": "Netherlands", "nederland": "Netherlands", "the netherlands": "Netherlands",
    "no": "Norway", "norway": "Norway", "norge": "Norway",
    "pl": "Poland", "poland": "Poland", "polska": "Poland",
    "pt": "Portugal", "portugal": "Portugal",
    "se": "Sweden", "sweden": "Sweden", "sverige": "Sweden",
    "si": "Slovenia", "slovenia": "Slovenia",
    "sk": "Slovakia", "slovakia": "Slovakia",
    "ch": "Switzerland", "switzerland": "Switzerland", "schweiz": "Switzerland", "suisse": "Switzerland",
    "uk": "UK", "gb": "UK", "united kingdom": "UK", "great britain": "UK", "england": "UK", "scotland": "UK", "wales": "UK",
    "tr": "Türkiye", "turkiye": "Türkiye", "türkiye": "Türkiye", "turkey": "Türkiye",
    "sm": "San Marino", "san marino": "San Marino",
    "rs": "Serbia", "serbia": "Serbia",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RANGE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})$", re.I)
ROUND_LABEL_RE = re.compile(
    r"\b(?:spring|summer|autumn|fall|winter)\s+(?:round|race|edition)\b|"
    r"\b(?:round|race|edition)\s+(?:spring|summer|autumn|fall|winter)\b",
    re.I,
)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def clean_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = "".join(ch for ch in value if unicodedata.category(ch)[0] != "C")
    return normalize_space(value)


def normalize_country(value: str) -> str:
    """Return a canonical country name and remove common import debris.

    Dates and surrounding punctuation occasionally leak into Country during imports;
    strip those before alias matching. Unknown values are cleaned but not guessed.
    """
    value = clean_text(value)
    value = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", value)
    value = re.sub(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b", " ", value)
    value = re.sub(r"^[\s,;|:/_-]+|[\s,;|:/_-]+$", "", value)
    value = normalize_space(value)
    folded = value.casefold()
    if folded in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[folded]
    tokens = re.findall(r"[^\W\d_]+", folded, flags=re.UNICODE)
    for alias, canonical in COUNTRY_ALIASES.items():
        alias_tokens = re.findall(r"[^\W\d_]+", alias, flags=re.UNICODE)
        if tokens == alias_tokens:
            return canonical
    return value


def normalize_event_name(value: str) -> str:
    value = clean_text(value)
    value = value.replace("–", "-").replace("—", "-").replace("’", "'")
    # Date/country already constrain identity. Ignore edition years and generic
    # seasonal round labels so e.g. "Bosorkin Canicross – autumn round 2026"
    # can match "Bosorkin Canicross" on the same overlapping date.
    value = re.sub(r"\b(?:2026|2027)\b", " ", value)
    value = ROUND_LABEL_RE.sub(" ", value)
    value = value.casefold()
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return normalize_space(value)


def parse_date_span(value: str) -> tuple[date, date] | None:
    value = normalize_space(value)
    if DATE_RE.fullmatch(value):
        day = date.fromisoformat(value)
        return day, day
    match = RANGE_RE.fullmatch(value)
    if match:
        return date.fromisoformat(match.group(1)), date.fromisoformat(match.group(2))
    return None


def spans_overlap(left: tuple[date, date] | None, right: tuple[date, date] | None) -> bool:
    if left is None or right is None:
        return False
    return left[0] <= right[1] and right[0] <= left[1]


def canonical_span(left: str, right: str) -> str:
    a, b = parse_date_span(left), parse_date_span(right)
    if not a or not b or not spans_overlap(a, b):
        return normalize_space(left) or normalize_space(right)
    start, end = min(a[0], b[0]), max(a[1], b[1])
    return start.isoformat() if start == end else f"{start.isoformat()} to {end.isoformat()}"


def event_country_key(row: dict[str, str]) -> tuple[str, str]:
    return (normalize_country(row.get("Country", "")).casefold(), normalize_event_name(row.get("Event", "")))


def merge_pipe_values(left: str, right: str) -> str:
    values, seen = [], set()
    for raw in (left, right):
        for part in (raw or "").split("|"):
            value = normalize_space(part)
            if value and value.casefold() not in seen:
                seen.add(value.casefold()); values.append(value)
    return "|".join(values)


def merge_text(left: str, right: str) -> str:
    left, right = normalize_space(left), normalize_space(right)
    if not left: return right
    if not right or right.casefold() == left.casefold(): return left
    return f"{left} | {right}"


def source_domain(value: str) -> str:
    try:
        return urlsplit(value).netloc.casefold().removeprefix("www.")
    except ValueError:
        return ""


def merge_sources(target: dict[str, str], incoming: dict[str, str]) -> None:
    sources, seen = [], set()
    for field in SOURCE_FIELDS:
        for row in (target, incoming):
            value = normalize_space(row.get(field, ""))
            if value and value not in seen:
                seen.add(value); sources.append(value)
    target["Primary source"] = sources[0] if sources else ""
    target["Secondary source"] = sources[1] if len(sources) > 1 else ""
    if len(sources) > 2:
        target["Notes"] = merge_text(target.get("Notes", ""), "Additional sources: " + " ; ".join(sources[2:]))
    domains = {source_domain(s) for s in sources if source_domain(s)}
    if len(domains) > 1:
        target["Notes"] = merge_text(target.get("Notes", ""), "Multiple independent event listings: " + " ; ".join(sources))


def merge_row(target: dict[str, str], incoming: dict[str, str]) -> None:
    target["Date"] = canonical_span(target.get("Date", ""), incoming.get("Date", ""))
    target["Country"] = normalize_country(target.get("Country", "") or incoming.get("Country", ""))
    for field in PIPE_FIELDS:
        target[field] = merge_pipe_values(target.get(field, ""), incoming.get(field, ""))
    for field in TEXT_MERGE_FIELDS:
        target[field] = merge_text(target.get(field, ""), incoming.get(field, ""))
    merge_sources(target, incoming)
    for field in EXPECTED_COLUMNS:
        if field in PIPE_FIELDS or field in TEXT_MERGE_FIELDS or field in SOURCE_FIELDS or field in {"Date", "Country"}:
            continue
        if not normalize_space(target.get(field, "")) and normalize_space(incoming.get(field, "")):
            target[field] = incoming[field]


def main() -> None:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise SystemExit(f"Unexpected CSV schema.\nExpected: {EXPECTED_COLUMNS}\nFound:    {reader.fieldnames}")
        rows = [dict(row) for row in reader]

    changed = False
    for row in rows:
        for field in EXPECTED_COLUMNS:
            cleaned = clean_text(row.get(field, ""))
            if cleaned != row.get(field, ""):
                row[field] = cleaned; changed = True
        country = normalize_country(row.get("Country", ""))
        if country != row.get("Country", ""):
            row["Country"] = country; changed = True

    deduped: list[dict[str, str]] = []
    groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    duplicate_count = 0
    for row in rows:
        key = event_country_key(row)
        candidates = groups.setdefault(key, [])
        existing = next((candidate for candidate in candidates if spans_overlap(parse_date_span(candidate.get("Date", "")), parse_date_span(row.get("Date", "")))), None)
        if existing is None:
            candidates.append(row); deduped.append(row); continue
        duplicate_count += 1; changed = True
        merge_row(existing, row)

    if not changed:
        print(f"No duplicates or normalization changes found in {CSV_PATH.relative_to(ROOT)} ({len(rows)} rows).")
        return

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_COLUMNS, lineterminator="\r\n")
        writer.writeheader(); writer.writerows(deduped)
    print(f"Normalized {CSV_PATH.relative_to(ROOT)}; merged {duplicate_count} duplicate row(s): {len(rows)} -> {len(deduped)} rows.")


if __name__ == "__main__":
    main()
