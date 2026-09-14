import csv
from pathlib import Path

p=Path('data/Canitrail_Masterkalender_2026_2027.csv')
with p.open(encoding='utf-8-sig', newline='') as f:
    r=csv.DictReader(f); fields=r.fieldnames; rows=list(r)

new=[
{'Date':'2026-09-20','Country':'Italy','Event':'Born to Run','Category':'canicross|bike jöring|scooter','Dog distance (km)':'3','Elevation (m+)':'50','Dog access':'dedicated canisport race','Status':'source-confirmed 2026','Notes':'2nd Be WILD Canicross; Bikejoring and Scooterjoring also offered; Borno, Brescia.','Primary source':'https://www.bewildogs.com/borntorun','Secondary source':'','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2026-09-27','Country':'UK','Event':'TRAILDOG UltiMutt','Category':'canicross','Dog distance (km)':'5','Elevation (m+)':'','Dog access':'dedicated dog-running obstacle event','Status':'source-confirmed 2026','Notes':'Byerley Stud, Wallridge; timed 5 km dog/human obstacle event with canicross wave.','Primary source':'https://www.traildogevents.co.uk/ultimutt','Secondary source':'https://www.traildogevents.co.uk/events','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2026-10-03 to 2026-10-04','Country':'France','Event':'Challenge Canicross Breizh','Category':'canicross|bike jöring|scooter','Dog distance (km)':'','Elevation (m+)':'','Dog access':'dedicated canisport event','Status':'source-confirmed 2026','Notes':'14th edition at Site Horizon, Plédran; organiser states 15 races across the weekend.','Primary source':'https://www.canicrossbreizh.fr/challenge-canicrossbreizh/','Secondary source':'','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2026-10-11','Country':'UK','Event':'TRAILDOG Castle Howard','Category':'canicross','Dog distance (km)':'5','Elevation (m+)':'','Dog access':'dog-running event with canicross wave','Status':'source-confirmed 2026','Notes':'5 km trail event at Castle Howard; dedicated canicross wave available.','Primary source':'https://www.traildogevents.co.uk/castlehoward','Secondary source':'https://www.traildogevents.co.uk/events','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2026-10-17','Country':'Poland','Event':'RAW PALEO Warsaw Dog Run – Canicross','Category':'canicross','Dog distance (km)':'5','Elevation (m+)':'','Dog access':'dedicated canicross','Status':'source-confirmed 2026','Notes':'Warsaw/Żoliborz; start 08:30; approx. 5 km through park, forest and Vistula beach.','Primary source':'https://dogrun.com.pl/canicross/','Secondary source':'https://dogrun.com.pl/2026/07/01/rejestracja-wystartowala/','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2026-11-08','Country':'UK','Event':'TRAILDOG The Collective – Raby Castle','Category':'canicross','Dog distance (km)':'','Elevation (m+)':'','Dog access':'dedicated dog-running event','Status':'source-confirmed 2026','Notes':'Part of TRAILDOG The Collective series; Raby Castle.','Primary source':'https://www.traildogevents.co.uk/events','Secondary source':'','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2026-12-13','Country':'UK','Event':'TRAILDOG The Collective – Druridge Bay','Category':'canicross','Dog distance (km)':'','Elevation (m+)':'','Dog access':'dedicated dog-running event','Status':'source-confirmed 2026','Notes':'Part of TRAILDOG The Collective series; Druridge Bay.','Primary source':'https://www.traildogevents.co.uk/events','Secondary source':'','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2027-01-30','Country':'UK','Event':'TRAILDOG The Collective – Druridge Night Run','Category':'canicross','Dog distance (km)':'','Elevation (m+)':'','Dog access':'dedicated dog-running event','Status':'source-confirmed 2027','Notes':'Night-run round of TRAILDOG The Collective at Druridge Bay.','Primary source':'https://www.traildogevents.co.uk/events','Secondary source':'','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2027-02-14','Country':'UK','Event':'TRAILDOG The Collective – Wallington','Category':'canicross','Dog distance (km)':'','Elevation (m+)':'','Dog access':'dedicated dog-running event','Status':'source-confirmed 2027','Notes':'Part of TRAILDOG The Collective series; Wallington National Trust.','Primary source':'https://www.traildogevents.co.uk/events','Secondary source':'','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2027-03-20','Country':'UK','Event':'Discover Kielder Ultra','Category':'canitrail','Dog distance (km)':'','Elevation (m+)':'','Dog access':'dog endurance event','Status':'source-confirmed 2027','Notes':'TRAILDOG event calendar lists Discover Kielder Ultra on 20 March 2027.','Primary source':'https://www.traildogevents.co.uk/events','Secondary source':'','Origin':'European independent-source sweep 2026-09-14'},
{'Date':'2027-03-21','Country':'UK','Event':'TRAILDOG The Collective – Kielder Waterside','Category':'canicross','Dog distance (km)':'','Elevation (m+)':'','Dog access':'dedicated dog-running event','Status':'source-confirmed 2027','Notes':'Part of TRAILDOG The Collective series; Kielder Waterside.','Primary source':'https://www.traildogevents.co.uk/events','Secondary source':'','Origin':'European independent-source sweep 2026-09-14'},
]

def norm(s): return ' '.join((s or '').lower().replace('–','-').replace('—','-').split())
def dateset(s):
    if ' to ' in s:
        a,b=s.split(' to ',1); return {a,b}
    return {s}
added=0
for n in new:
    duplicate=False
    for x in rows:
        if norm(x['Country'])==norm(n['Country']) and norm(x['Event'])==norm(n['Event']) and dateset(x['Date']) & dateset(n['Date']):
            duplicate=True; break
    if not duplicate:
        rows.append({k:n.get(k,'') for k in fields}); added+=1
rows.sort(key=lambda x:(x['Date'][:10], norm(x['Country']), norm(x['Event'])))
with p.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
print(f'Added {added} verified events; {len(new)-added} matched existing master rows.')
