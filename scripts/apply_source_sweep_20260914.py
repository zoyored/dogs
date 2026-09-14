from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "Canitrail_Masterkalender_2026_2027.csv"
FIELDS = ["Date", "Country", "Event", "Category", "Dog distance (km)", "Elevation (m+)", "Dog access", "Status", "Notes", "Primary source", "Secondary source", "Origin"]

NEW_ROWS = [
    ["2027-01-02", "UK", "YPB Seven Sins Challenge – Canicross", "canicross", "11.3", "", "dedicated canicross start", "registration open", "Seven Sins weekend; organiser explicitly lists Canicross on Saturday 2 Jan at 10:00. Approx. 7-mile course.", "https://www.ypbevents.co.uk/7-sins-immortal", "", "source-master sweep round 2 2026-09-14"],
    ["2027-01-03", "UK", "Lakeland Paws – Grizedale Growl East Side", "canicross", "not published", "", "dedicated canicross event", "registration open", "Official Lakeland Paws 2026/27 series lists Grizedale Growl East Side on 3 Jan 2027.", "https://lakelandpaws.com/events/", "", "source-master sweep round 2 2026-09-14"],
    ["2027-01-16", "UK", "Maverick New Forest Gravel 2027", "dog friendly trail", "12|22", "111|172", "dogs allowed with separate dog entry", "dog entries sold out", "Official event page is dog-friendly with limited dog spaces; 6 km option omitted here.", "https://www.maverick-race.com/products/2027/2027-01-16", "", "source-master sweep round 2 2026-09-14"],
    ["2027-01-30 to 2027-01-31", "UK", "YPB May Hill Massacre – Canicross", "canicross", "7-8 miles", "", "dedicated canicross start", "registration open", "Official organiser page publishes the 30–31 Jan weekend and a Canicross start at 10:00; main Massacre route is 7–8 miles.", "https://www.ypbevents.co.uk/mayhill-massacre", "", "source-master sweep round 2 2026-09-14"],
    ["2027-03-07", "UK", "Lakeland Paws – Tour de Grizedale", "canicross", "12|22", "", "dedicated canicross event", "registration open", "Official 2026/27 series date; current route page offers 12 km and half-marathon (~22 km) options.", "https://lakelandpaws.com/events/", "https://lakelandpaws.com/grizedale-growl-tour-de-grizedale/", "source-master sweep round 2 2026-09-14"],
    ["2027-03-20", "UK", "Maverick Hampshire Trail 2027", "dog friendly trail", "16|24", "298|410", "dogs allowed with separate dog entry", "registration open", "Official event page confirms dog-friendly entries; 5 km option omitted here.", "https://www.maverick-race.com/products/2027/2027-03-20", "", "source-master sweep round 2 2026-09-14"],
    ["2027-04-03", "UK", "Maverick East Sussex Trail 2027", "dog friendly trail", "13|21", "339|457", "dogs allowed with separate dog entry", "registration open", "Official event page confirms dog-friendly entries; 5 km option omitted here.", "https://www.maverick-race.com/products/the-maverick-east-sussex-trail-2027", "", "source-master sweep round 2 2026-09-14"],
    ["2027-04-24", "UK", "Lakeland Paws – Dogs @ Dodd Double Header", "canicross", "not published", "", "dedicated canicross event", "registration open", "First day of Lakeland Paws Double Header; official 2026/27 events page confirms 24 Apr 2027.", "https://lakelandpaws.com/events/", "", "source-master sweep round 2 2026-09-14"],
    ["2027-04-25", "UK", "Lakeland Paws – Whinlatter Tails Seat How Double Header", "canicross", "not published", "", "dedicated canicross event", "registration open", "Second day of Lakeland Paws Double Header; official 2026/27 events page confirms 25 Apr 2027.", "https://lakelandpaws.com/events/", "", "source-master sweep round 2 2026-09-14"],
    ["2027-05-22", "UK", "Maverick Cotswolds Trail 2027", "dog friendly trail", "11|23|42|50", "302|580|1175|1495", "dogs allowed with separate dog entry", "registration open", "Official event page confirms dog-friendly entries; 7 km option omitted here.", "https://www.maverick-race.com/products/2027/2027-05-22", "", "source-master sweep round 2 2026-09-14"],
]


def norm(s: str) -> str:
    return " ".join((s or "").casefold().replace("–", "-").replace("’", "'").split())

with PATH.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

existing = {(r["Date"].strip(), norm(r["Event"])) for r in rows}
added = 0
for values in NEW_ROWS:
    row = dict(zip(FIELDS, values))
    key = (row["Date"], norm(row["Event"]))
    if key not in existing:
        rows.append(row)
        existing.add(key)
        added += 1

rows.sort(key=lambda r: (r["Date"][:10], norm(r["Event"])))
with PATH.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {added} verified events; master now has {len(rows)} rows.")
