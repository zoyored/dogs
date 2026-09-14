#!/usr/bin/env python3
import csv
from pathlib import Path

MASTER = Path('data/Canitrail_Masterkalender_2026_2027.csv')

with MASTER.open(newline='', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
    fields = list(rows[0].keys())

by_event = {r['Event']: r for r in rows}

def update(name, **changes):
    if name not in by_event:
        raise SystemExit(f'Missing event in master: {name}')
    by_event[name].update(changes)

# Re-checked 2026-09-14 against current organiser pages.
update(
    'MOUNTAINMAN Reit im Winkl – Dogs-Trail',
    Date='2026-09-25',
    **{
        'Elevation (m+)': '304|938',
        'Status': 'sold out / waitlist',
        'Notes': 'S 11 km / 304 m+ and M 26 km / 938 m+; both dog starts sold out, waitlist available; own dog starts and separate trailrunner ranking.',
        'Primary source': 'https://mountainman.de/trailrunning-events/alps/reit-im-winkl/dogs-trail/',
        'Origin': 'web re-check 2026-09-14',
    },
)

update(
    'MOUNTAINMAN Nesselwang – Dogs-Trail',
    **{
        'Dog distance (km)': '10|21',
        'Elevation (m+)': '780|1268',
        'Status': 'registration open',
        'Notes': 'S 10 km / 780 m+ and M 21 km / 1,268 m+; registration open; around 150 dog-team places.',
        'Origin': 'web re-check 2026-09-14',
    },
)

update(
    'Canitrail des Châtaignes',
    Date='2026-11-14',
    **{
        'Dog distance (km)': '15',
        'Elevation (m+)': '440',
        'Status': 'sold out / waitlist',
        'Notes': 'Official 2026 canitrail is Saturday 14 Nov: 15 km / 440 m+, start 13:00; minimum dog age 24 months; event full, waitlist open.',
        'Primary source': 'https://trail-des-chataignes.com/les-courses/',
        'Secondary source': 'https://trail-des-chataignes.com/reglement-canitrail/',
        'Origin': 'web re-check 2026-09-14',
    },
)

# Previously identified missing UK 2027 event; official organiser page re-checked 2026-09-14.
if 'Ultra Cani-Trail 30 & 50 Mile' not in by_event:
    row = {k: '' for k in fields}
    row.update({
        'Date': '2027-03-20',
        'Country': 'UK',
        'Event': 'Ultra Cani-Trail 30 & 50 Mile',
        'Category': 'canitrail',
        'Dog distance (km)': '48.3|80.5',
        'Dog access': 'dog-only ultra trail event',
        'Status': 'registration open',
        'Notes': 'South Wales Valleys. 30 mile route has no time limit; 50 mile route has a 17-hour cut-off. GPS tracker on both routes; 30-mile relay option.',
        'Primary source': 'https://www.canitrailevents.co.uk/ultra-cani-trail-30-and-50-2027/',
        'Origin': 'web re-check 2026-09-14',
    })
    rows.append(row)

rows.sort(key=lambda r: (r['Date'][:10], r['Country'], r['Event']))
with MASTER.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
