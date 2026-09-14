import csv
from pathlib import Path
p=Path('data/source-master.csv')
with p.open(encoding='utf-8-sig',newline='') as f:
    r=csv.DictReader(f); fields=r.fieldnames; rows=list(r)
# Remove obsolete/less useful duplicate URLs for sources replaced by current official sites.
replace_names={'Canicross Ireland'}
# Existing Ireland federation row is retained; add current event site separately.
new=[
{'Country':'Ireland','Source':'Canicross Ireland Events','URL':'https://www.canicross-ireland.com/upcoming-events','Source type':'federation-calendar','Notes':'Current official Canicross Ireland 2026/27 event calendar; Canicross Bikejoring and Scooter classes.'},
{'Country':'Spain','Source':'Cross Madrid Canicross – Calendario Mushing','URL':'https://canicrosscrossmadrid.com/competiciones/','Source type':'discovery-calendar','Notes':'Detailed Spanish 2026/27 mushing and canicross calendar; verify individual races against federation or organiser where possible.'},
{'Country':'Spain','Source':'Euskadiko Txakurkros Liga','URL':'https://txakurkros.com/pages/etl.html','Source type':'league-calendar','Notes':'Basque/Navarre popular canicross league run by independent clubs; publishes provisional 2026/27 dates and distances.'},
{'Country':'Switzerland','Source':'Swiss Canicross Competition Calendar','URL':'https://swiss-canicross.ch/courses/','Source type':'federation-calendar','Notes':'Current Swiss Canicross federation event calendar with Canicross and Canitrail dates and organiser/event detail pages.'},
{'Country':'Austria','Source':'BSSC Austria','URL':'https://bssc-austria.at/veranstaltungen/','Source type':'club','Notes':'Austrian sleddog club and race organiser; dryland events include Canicross Bikejoring and Scooter classes.'},
]
existing={(x['Country'].strip().casefold(),x['Source'].strip().casefold()) for x in rows}
for n in new:
    key=(n['Country'].casefold(),n['Source'].casefold())
    if key not in existing:
        rows.append(n); existing.add(key)
rows.sort(key=lambda x:(x['Country'].casefold(),x['Source'].casefold()))
with p.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
print('source-master rows:',len(rows))
