#!/usr/bin/env python3
import csv
from pathlib import Path

P=Path('data/Canitrail_Masterkalender_2026_2027.csv')
with P.open(encoding='utf-8-sig', newline='') as f:
    rows=list(csv.DictReader(f)); fields=rows[0].keys()

def add(date,country,event,category,dist,elev,access,status,notes,primary,secondary='',origin='source-master sweep 2026-09-14'):
    # Avoid duplicates by event + date; also avoid same named event already stored for 2027.
    if any(r['Event'].strip().casefold()==event.casefold() and r['Date'].startswith(date[:10]) for r in rows): return
    r={k:'' for k in fields}; r.update({'Date':date,'Country':country,'Event':event,'Category':category,'Dog distance (km)':dist,'Elevation (m+)':elev,'Dog access':access,'Status':status,'Notes':notes,'Primary source':primary,'Secondary source':secondary,'Origin':origin}); rows.append(r)

# FFSLC official 2027 calendar additions
ff='https://courses.ffslc.fr/calendar'
for e in [
('2027-01-10','Canicross de Cergy – L’île aux trésors','canicross','not published','dedicated FFSLC canicross'),
('2027-01-24','Canicross de l’XTREM – 5e édition','canicross','not published','dedicated FFSLC event'),
('2027-01-30 to 2027-01-31','CANI TROPHY FONTAINEBLEAU 2027','canicross|canitrail','not published','FFSLC canicross/canitrail weekend'),
('2027-01-30 to 2027-01-31','Trophée Canin des Plages 2027','canicross','not published','FFSLC event'),
('2027-02-07','Doggy Deûle Run #2','canicross','not published','FFSLC event'),
('2027-02-07','La Canidé’forts – 4e édition','canicross','not published','dedicated FFSLC canicross'),
('2027-02-13 to 2027-02-14','5th Dirty Dog Race','canicross','not published','FFSLC event'),
('2027-02-13 to 2027-02-19','Trophée des Lacs','canicross','not published','FFSLC event'),
('2027-02-13 to 2027-02-14','Les courses de l’étang','canicross','not published','FFSLC event'),
('2027-02-28','Interclub Manchois','canicross','not published','FFSLC event'),
('2027-04-03 to 2027-04-04','Canicross du Lac des Sapins','canicross','not published','FFSLC event'),
('2027-04-10 to 2027-04-11','Canicross XtremTrail de Brameloup','canicross|canitrail','not published','FFSLC event'),
('2027-04-24 to 2027-04-25','4e Castel’Canicross de Blangy-le-Château','canicross','not published','FFSLC event'),
]: add(e[0],'France',e[1],e[2],e[3],'',e[4],'announced', 'New 2027 date published in the official FFSLC calendar.',ff)

# Run With K9s official source
add('2027-02-28','UK','Run With K9s – Endurance Canicross Relay','canicross','2.5 km laps up to 3h','','dedicated canicross relay / solo','registration announced','3-hour endurance relay or solo challenge on 2.5 km laps at Bulwell Hall Park, Nottingham.','https://www.runwithk9s.com/canicrossrelays')

# Wild Deer Events official 2027 canicross-friendly trail events
wild=[
('2027-01-09','Yorkshire Trail Runs – Harewood House','5|10|21.1','https://www.wilddeerevents.co.uk/e/yorkshire-trail-runs-2027-harewood-house-14484'),
('2027-01-24','Druridge Bay Beach Trail Runs','5|10|21.1','https://www.wilddeerevents.co.uk/e/druridge-bay-beach-trail-runs-2026-14486'),
('2027-02-28','Fountains Abbey Wild Trail Runs','5|10|21.1','https://www.wilddeerevents.co.uk/e/fountains-abbey-wild-trail-runs-14487'),
('2027-03-06','Tatton Park Wild Trail Runs','5|10|21.1','https://www.wilddeerevents.co.uk/e/tatton-park-wild-trail-runs-2026-14521'),
('2027-03-20','Grasmere Wild Trail Runs','5|10|21.1','https://www.wilddeerevents.co.uk/e/grasmere-wild-trail-runs-2027-14493'),
('2027-04-17','Bamburgh Castle Wild 10K Trail Run','10','https://www.wilddeerevents.co.uk/e/bamburgh-castle-wild-10km-trail-run-15391'),
('2027-05-05','Gibside National Trust Wild Trail Runs','5|10','https://www.wilddeerevents.co.uk/e/gibside-national-trust-wild-trail-runs-2027-14511'),
('2027-05-23','Margam Wild Trail Runs','5|10|21.1','https://www.wilddeerevents.co.uk/e/margam-wild-trail-runs-14954'),
('2027-06-27','Alice Holt Wild Trail Runs','10|21.1','https://www.wilddeerevents.co.uk/e/alice-holt-wild-trail-runs-2026-10km-and-1-2-marathon-14497'),
]
for d,n,dist,url in wild: add(d,'UK',n,'dog friendly trail',dist,'','canicross friendly; one controlled dog per runner','registration open','Official organiser page explicitly confirms canicross access for the 2027 event.',url)

# Limitless Trails official published 2027 dates; organiser advertises Canicross but event-level dog eligibility should remain explicit in notes.
lim='https://www.limitlesstrails.co.uk/'
for d,n,dist in [
('2027-02-06','Limitless Trails – Trails & Tarmac Winter 12h BYU','4.2 mile loops up to 12h'),
('2027-03-06','Limitless Trails – Beast of the Blacks','10|20|40 miles'),
('2027-04-17','Limitless Trails – Beast of the Beacons','10|20|40 miles'),
('2027-07-10','Limitless Trails – Tenacious Ten Endurance Challenge','not published'),
]: add(d,'UK',n,'dog friendly trail',dist,'','organiser offers Canicross; verify event-level dog rules before entry','announced','New 2027 date published by Limitless Trails; Canicross is offered by organiser, but event-specific dog rules should be checked before entry.',lim)

# Finishers discovery: add only entries where the platform exposes a distinct dog-specific distance and a 2027 edition.
add('2027-03','France','Défi Vellave – Canicross','canicross','6','100','dedicated canicross distance','date TBC','Finishers lists a 6 km / 100 m+ Canicross for the early-March 2027 edition; exact day not yet published.','https://www.finishers.com/de/e/defi-vellave')
add('2027-04','Czech Republic','Leki Ještěd SkyRace – Canicross','canicross','6|13','300|945','dedicated Canicross distances','date TBC','Finishers lists 6 km / 300 m+ and 13 km / 945 m+ Canicross formats for mid-April 2027; exact day not yet published.','https://www.finishers.com/de/e/leki-jested-skyrace')
add('2027-05','Italy','Ultra Trail Mugello – Mugello Dog Trail','dogs-trail','12','650','dedicated dog trail','date TBC','Finishers lists a dedicated 12 km / 650 m+ Mugello Dog Trail for early May 2027; exact day not yet published.','https://www.finishers.com/de/e/ultra-trail-mugello')
add('2027-02','France','Trail Les Petits Pas – Cani','canicross','6','','dedicated dog-running distance','date TBC','Finishers lists a 6 km Cani format for late February 2027; exact day not yet published.','https://www.finishers.com/de/e/trail-les-petits-pas')

rows.sort(key=lambda r:(r['Date'],r['Country'],r['Event']))
with P.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f'Wrote {len(rows)} master rows')
