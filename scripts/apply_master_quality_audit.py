import csv
from pathlib import Path

P=Path('data/Canitrail_Masterkalender_2026_2027.csv')
with P.open(encoding='utf-8-sig', newline='') as f:
    rows=list(csv.DictReader(f)); fields=list(rows[0].keys())

def merge_text(a,b,sep=' | '):
    vals=[]
    for x in (a,b):
        if x and x.strip() and x.strip() not in vals: vals.append(x.strip())
    return sep.join(vals)

# 1) Confirmed semantic duplicate: Be WILD Born to Run == CSEN Canicross Borno.
born=[r for r in rows if r['Date']=='2026-09-20' and r['Country']=='Italy' and r['Event']=='Born to Run']
csen=[r for r in rows if r['Date']=='2026-09-20' and r['Country']=='Italy' and r['Event']=='CSEN Canicross Borno']
if born and csen:
    b=born[0]; c=csen[0]
    b['Category']='canicross|bike jöring|scooter'
    b['Dog distance (km)']='3'; b['Elevation (m+)']='50'
    b['Notes']='2nd Be WILD Born to Run; Borno (BS). Official CSEN-recognized race and ICF 2027 selection race; Canicross, Bikejoring and Scooterjoring; 3 km / ca. 50 m+.'
    b['Primary source']='https://www.bewildogs.com/borntorun'
    b['Secondary source']='https://discipline.csencinofilia.it/calendario-gare-2027/'
    b['Origin']=merge_text(b['Origin'],c['Origin'])
    rows.remove(c)

# 2) Trutnovská 10 is a single-day event on 5 June 2027; canicross route is 3 km.
for r in rows:
    if r['Country']=='Czech Republic' and r['Event']=='Trutnovská 10 – Canicross 2027':
        r['Date']='2027-06-05'; r['Dog distance (km)']='3'
        r['Notes']='Trutnov; organizer page announces 5 June 2027 and a dedicated Canicross category; official route page lists a 3 km canicross loop.'
        r['Primary source']='https://www.kst.events/trutnovska10'
        r['Secondary source']='https://www.kst.events/trutnovska10/trasa'

# 3) CROSSDOG official calendar was present as a source but its six published race events were missing.
new=[
('2026-07-31 to 2026-08-01','CROSSDOG Summer Nights','not published','Goldbach; official CROSSDOG event calendar.'),
('2026-10-24','CROSSDOG DAS EVENT am SAUERBERG','not published','Frammersbach; official CROSSDOG event calendar.'),
('2026-11-14','CROSSDOGs DONNERSBERGTRAIL','not published','Kirchheimbolanden; official CROSSDOG event calendar.'),
('2026-12-31','CROSSDOGs Silvester Trail','not published','Rothenbuch; official CROSSDOG event calendar.'),
('2027-02-06','CROSSDOGs Streetwaldcross','not published','Mainaschaff; official CROSSDOG event calendar.'),
('2027-02-27 to 2027-02-28','CROSSDOG on the beach','5.5|11|20','Grömitz; CaniX RUN S/M/L approx. 5.5/11/20 km; also OCR 5.5 km and Challenge 4.5 km.')]
existing={(r['Date'],r['Country'],r['Event']) for r in rows}
for date,name,dist,note in new:
    key=(date,'Germany',name)
    if key in existing: continue
    r={k:'' for k in fields}
    r.update({'Date':date,'Country':'Germany','Event':name,'Category':'dogs-trail','Dog distance (km)':dist,'Dog access':'dedicated CROSSDOG dog-running event','Status':'source-confirmed','Notes':note,'Primary source':'https://crossdog.de/events/','Origin':'master quality audit 2026-09-14'})
    if name=='CROSSDOG on the beach': r['Primary source']='https://crossdog.de/event/crossdog-on-the-beach/'
    rows.append(r)

# 4) Kielder: keep event, but avoid overstating category while organiser only publishes it as a dog-running event without route detail yet.
for r in rows:
    if r['Country']=='UK' and r['Event']=='Discover Kielder Ultra' and r['Date']=='2027-03-20':
        r['Category']='canitrail'; r['Dog access']='dedicated TRAILDOG dog-running event'
        r['Notes']='TRAILDOG official calendar confirms Discover Kielder Ultra for 20 March 2027; distance/elevation not yet published on the accessible event listing.'

rows.sort(key=lambda r:(r['Date'][:10],r['Country'].casefold(),r['Event'].casefold()))
with P.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
print('rows',len(rows))
