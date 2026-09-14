from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "source-master.csv"

NEW_ROWS = [
    ["France", "Les CaniPirates", "https://www.les-canipirates.fr/", "club", "FFSLC-affiliated Canicross/Canitrail club and organiser of Canitrail des Châtaignes and L'Ile aux Tresors"],
    ["France", "Canicross Breizh", "https://www.canicrossbreizh.fr/", "club", "Independent Breton canicross club and organiser of the annual Challenge Canicrossbreizh"],
    ["France", "X-Trem34 Canisport", "https://sites.google.com/view/x-trem34canisport/accueil", "club", "Canicross and Canitrail club; organiser/source for X-Trem canisport events"],
    ["France", "Canikazes 86", "https://canikazes86.wixsite.com/canikazes-86", "club", "FFSLC club active in Canicross CaniVTT and CaniTrot; organiser selected for the 2026 French Canitrail championship"],
    ["France", "Canicross Val de Loire", "https://www.helloasso.com/associations/canicross-val-de-loire", "club", "Canicross/Canitrail club and organiser of the Canicross Val de Loire race"],
    ["UK", "TRAILDOG Events", "https://www.traildogevents.co.uk/events", "organizer", "Dedicated North East dog-running organiser with The Collective UltiMutt MultiSport and Kielder events"],
    ["UK", "Big Bear Events", "https://bigbearevents.net/", "organizer", "Trail/endurance organiser with selected dedicated Canicross starts and dog-friendly challenge events; verify each event"],
    ["UK", "Running On Point", "https://runningonpoint.co.uk/", "discovery-calendar", "UK discovery platform focused on Canicross and dog-friendly running; verify listings against the organiser"],
    ["Italy", "Be WILD", "https://www.bewildogs.com/", "organizer", "Canicross Bikejoring and Scooterjoring organiser; CSEN calendar organiser for Born to Run"],
    ["Italy", "Canpus Cinofilia", "https://www.canpuscinofilia.it/", "organizer", "Canine sport centre with Canicross and Scooterjoring; CSEN calendar organiser for FranciacorSa"],
    ["Italy", "Mad Dogs Sporting Center", "https://www.maddogssportingcenter.it/", "organizer", "Canine sport centre and Canicross organiser; listed by CSEN for Basovizza 2026"],
    ["Italy", "Scuola Cinotecnica Italiana", "https://scuolacinotecnicaitaliana.it/", "organizer", "Canine training and event organisation; listed by CSEN as organiser of Canicross Citta di Grosseto 2027"],
    ["Poland", "Warsaw Dog Run", "https://dogrun.com.pl/", "organizer", "Fundacja Maraton Warszawski dog-running event with dedicated Canicross and Dogtrekking formats"],
    ["Poland", "Puchar Polski w Dogtrekkingu", "https://dogtrekking.pl/", "organizer", "National Dogtrekking cup organised by Sportshooter and Fundacja Sportowa Polska; useful dog-endurance discovery source"],
    ["Czech Republic", "Mammoth Race / Canicross Prerov", "https://www.mammothrace.cz/", "organizer", "Independent dedicated Canicross Dog Sprint organiser in Prerov"],
    ["Denmark", "DIRTY PAWS", "https://dirtypawscanicross.dk/", "club", "National Canicross/Canihike club and DCF member club; organiser of DCF Dog Series rounds"],
    ["Denmark", "DCF Dog Series", "https://www.danskcanicross.dk/kalender", "federation-calendar", "DCF season calendar identifies individual organiser clubs such as CaniXFyn K9Runners Mariager DogRunDK Canicross Ostjylland and Dirty Paws"],
    ["Finland", "Traildog.fi event calendar", "https://traildog.fi/pages/valjakkourheilukilpailut-ja-tapahtumat", "discovery-calendar", "Continuously updated Finnish sleddog sport calendar covering Canicross Bikejoring Scooter and race organiser clubs; verify against VUL or organiser"],
]


def main() -> None:
    with PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]

    # Replace the obsolete TRAILDOG row/URL with the current TRAILDOG Events source.
    data = [r for r in data if not (len(r) >= 2 and r[0] == "UK" and r[1] == "TRAILDOG")]

    existing = {(r[0].strip().casefold(), r[1].strip().casefold()) for r in data if len(r) >= 2}
    added = 0
    for row in NEW_ROWS:
        key = (row[0].casefold(), row[1].casefold())
        if key not in existing:
            data.append(row)
            existing.add(key)
            added += 1

    with PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\r\n")
        writer.writerow(header)
        writer.writerows(data)
    print(f"Added {added} new/updated source rows; total {len(data)} sources.")


if __name__ == "__main__":
    main()
