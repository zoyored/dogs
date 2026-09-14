import csv
from pathlib import Path

P=Path('data/Canitrail_Masterkalender_2026_2027.csv')
rows=list(csv.DictReader(P.open(encoding='utf-8-sig')))
fields=list(rows[0])

candidates=[]
def add(date,country,event,category,access,notes,primary,origin='Europe gap large sweep 2026-09-14'):
    candidates.append({'Date':date,'Country':country,'Event':event,'Category':category,'Dog distance (km)':'not published','Elevation (m+)':'','Dog access':access,'Status':'source-confirmed 2026/27','Notes':notes,'Primary source':primary,'Secondary source':'','Origin':origin})

# Ireland official 2026/27 calendar
for d,n,loc in [
('2026-10-17','Canicross Ireland 2026/27 – Event 1','Lough Boora Parklands – Turraun'),
('2026-10-18','Canicross Ireland 2026/27 – Event 2','Lough Boora Parklands – Turraun'),
('2026-12-12','Canicross Ireland 2026/27 – Event 3','Finnamore Lakes, Co. Offaly'),
('2026-12-13','Canicross Ireland 2026/27 – Event 4','Finnamore Lakes, Co. Offaly'),
('2027-02-07','Canicross Ireland 2026/27 – Event 5','Rathwood'),
('2027-03-20','Canicross Ireland 2026/27 – Event 6','Drewstown House'),
('2027-03-21','Canicross Ireland 2026/27 – Event 7','Drewstown House')]:
 add(d,'Ireland',n,'canicross|bike jöring|scooter','dedicated Canicross Ireland race',f'Official 2026/27 season calendar; {loc}; championship, recreational and kids classes.','https://www.canicross-ireland.com/upcoming-events')

# Denmark DCF Dog Series
for d,n,loc in [
('2026-10-25','DCF Dog Series 1 – CaniXFyn','Morud'),('2026-12-06','DCF Dog Series 2 – K9Runners Mariager','Mariager'),('2027-01-23','DCF Dog Series 3 – Danish Championship by DogRunDK','Hedeland'),('2027-02-28','DCF Dog Series 4 – Canicross Østjylland','Århus'),('2027-03-14','DCF Dog Series 5 – Dirty Paws','Frederiksværk'),('2027-04-03','DCF Dog Series 6 – K9Runners Mariager','Mariager')]:
 add(d,'Denmark',n,'canicross|bike jöring|scooter','DCF Dog Series',f'Official DCF 2026/27 calendar; {loc}.','https://www.danskcanicross.dk/kalender')

# Switzerland current federation calendar; use actual multi-day ranges
for d,n,cat,loc in [
('2026-09-12 to 2026-09-13','Canicross Saint-Cierges','canicross','Saint-Cierges, Vaud'),('2026-09-26 to 2026-09-27','Canicross Yens','canicross','Yens, Vaud'),('2026-10-03 to 2026-10-04','Canitrail des Bisses','canitrail','Anzère, Valais'),('2026-10-10 to 2026-10-11','Canicross Koppigen','canicross','Koppigen, Bern'),('2026-10-17 to 2026-10-18','Canicross La Givrine','canicross','La Givrine'),('2026-10-24 to 2026-10-25','Canicross Ardon','canicross','Ardon')]:
 add(d,'Switzerland',n,cat,'official Swiss Canicross event',f'Official Swiss Canicross calendar; {loc}.','https://swiss-canicross.ch/courses/')

# Netherlands: skip training weekend; provisional races retained with provisional note
for d,n,cat,loc,prov in [
('2026-10-04','CCNL Harderwijk','canicross|bike jöring|scooter','Harderwijk',False),('2026-12-12','CCNL IJmuiden','canicross','IJmuiden',True),('2027-01-17','CCNL Bosschenhoofd','canicross|bike jöring|scooter','Bosschenhoofd',True),('2027-01-24','Dutch Championship CC/BJ/Step','canicross|bike jöring|scooter','location TBA',False),('2027-02-14','CCNL Gasselte','canicross|bike jöring|scooter','Gasselte',True),('2027-03-06 to 2027-03-07','CCNL Helden – DutchRacingDog','canicross|bike jöring|scooter','Helden',True),('2027-03-21','CCNL Bruinisse','canicross|bike jöring|scooter','Bruinisse',True),('2027-04-11','Canicross Zundert','canicross|bike jöring|scooter','Zundert',False)]:
 add(d,'Netherlands',n,cat,'CCNL race',f'Official CCNL 2026/27 calendar; {loc}.'+(' Date marked provisional pending permits.' if prov else ''),'https://www.canicrossnederland.nl/kalender20262027.html')

# Slovakia official current 2026/27 page
for d,n,loc,status in [
('2026-09-12 to 2026-09-13','Pezinská Baba','Pezinská Baba',''),('2026-09-20','Haniska','Haniska',''),('2026-09-26 to 2026-09-27','Bosorkin Canicross','Košice',''),('2026-10-31 to 2026-11-01','Mošovce','Mošovce',''),('2026-12-05 to 2026-12-06','Láb Dog Race','Láb','')]:
 add(d,'Slovakia',n,'canicross','SZPZ dryland race',f'Official SZPZ 2026/27 race calendar; {loc}.','https://mushing.sk/preteky/')

# France: future 2027 events from official FFSLC calendar; many older 2026 entries already covered by prior FFSLC sweep
for d,n,cat in [
('2027-01-10',"Canicross de Cergy – L'île aux trésors",'canicross'),('2027-01-24',"Canicross de l'XTREM – 5e édition",'canicross'),('2027-01-30 to 2027-01-31','CANI TROPHY FONTAINEBLEAU 2027','canicross|canitrail'),('2027-01-30 to 2027-01-31','Trophée Canin des Plages 2027','canicross'),('2027-02-07','Doggy Deûle Run #2','canicross'),('2027-02-07',"La Canidé'forts – 4e édition",'canicross|bike jöring|scooter'),('2027-02-13 to 2027-02-14','5th Dirty Dog Race','canicross'),('2027-02-13 to 2027-02-19','Trophée des Lacs','canicross'),('2027-02-13 to 2027-02-14',"Les courses de l'étang",'canicross'),('2027-02-28','Interclub Manchois','canicross'),('2027-04-03 to 2027-04-04','Canicross du Lac des Sapins','canicross'),('2027-04-10 to 2027-04-11','Canicross XtremTrail de Brameloup','canicross|canitrail'),('2027-04-24 to 2027-04-25',"Castel'Canicross de Blangy le Château – 4e",'canicross')]:
 add(d,'France',n,cat,'dedicated FFSLC event','Official FFSLC 2027 calendar entry.','https://courses.ffslc.fr/calendar')

# Match conservatively before dedupe: exact normalized event+overlapping year/date will be handled by repo dedupe.
def norm(s): return ''.join(c.lower() for c in s if c.isalnum())
existing={(norm(r['Country']),norm(r['Event']),r['Date']) for r in rows}
added=0
for c in candidates:
    k=(norm(c['Country']),norm(c['Event']),c['Date'])
    if k not in existing:
        rows.append(c); existing.add(k); added+=1
rows.sort(key=lambda r:(r['Date'],r['Country'],r['Event']))
with P.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f'Candidates {len(candidates)}, appended before dedupe {added}')
