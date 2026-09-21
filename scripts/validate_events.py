#!/usr/bin/env python3
"""Incremental deterministic event-source validator.

Checks a bounded daily slice of master events plus all previously flagged rows.
It never changes or deletes master-calendar rows.
"""
import argparse, csv, hashlib, re, ssl, urllib.error, urllib.request
from datetime import date, datetime
from html import unescape
from pathlib import Path

MASTER=Path("data/Canitrail_Masterkalender_2026_2027.csv")
STATE=Path("data/event-validation.csv")
REPORT=Path("reports/event-validation/latest.md")
UA="Mozilla/5.0 (compatible; SandsturmEventValidator/2.0; +https://sandsturm.com/)"

FIELDS=["Date","Country","Event","Primary source","HTTP status","Final URL","Event token match",
        "Year/date marker","Dog marker","Review required","Review reason","Checked","Source fingerprint"]

def norm(s):
    return re.sub(r"[^a-z0-9]+"," ",unescape((s or "").lower())).strip()

def tokens(s):
    stop={"the","and","und","des","der","die","de","du","la","le","les","trail","canicross","canitrail","2026","2027"}
    return [x for x in norm(s).split() if len(x)>=4 and x not in stop]

def key(row):
    return (row.get("Date","").strip(),row.get("Country","").strip(),row.get("Event","").strip())

def first_date(value):
    m=re.search(r"20\d{2}-\d{2}-\d{2}",value or "")
    if not m: return date.max
    try: return datetime.strptime(m.group(0),"%Y-%m-%d").date()
    except ValueError: return date.max

def fetch(url):
    if not url: return ("missing","","")
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml,application/pdf;q=0.8,*/*;q=0.5"})
    try:
        with urllib.request.urlopen(req,timeout=25,context=ssl.create_default_context()) as r:
            raw=r.read(1200000); ctype=r.headers.get("Content-Type",""); final=r.geturl()
            if "pdf" in ctype.lower() or raw[:4]==b"%PDF":
                return (str(r.status),final,"[pdf]:"+hashlib.sha256(raw).hexdigest())
            text=raw.decode("utf-8","ignore")
            text=re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>"," ",text,flags=re.I|re.S)
            text=re.sub(r"<[^>]+>"," ",text)
            return (str(r.status),final,norm(text))
    except urllib.error.HTTPError as e: return (str(e.code),url,"")
    except Exception as e: return ("error:"+type(e).__name__,url,"")

def validate(row, previous=None):
    url=row.get("Primary source","").strip()
    status,final,text=fetch(url)
    pdf=text.startswith("[pdf]:")
    body="" if pdf else text
    ev=tokens(row.get("Event",""))
    hit=sum(1 for t in ev if t in body)
    ratio=(hit/len(ev)) if ev else 0
    years=re.findall(r"20\d{2}",row.get("Date",""))
    year_hit=any(y in body for y in years) if body else False
    dog_terms=any(x in body for x in ["canicross","canitrail","dog ","dogs ","hund","chien","cani ","mushing","bikejor","scooter","sled","sledge","skijor","pulka"]) if body else False
    reachable=status.startswith("2") or status.startswith("3")
    reasons=[]
    if not url: reasons.append("missing primary source")
    elif not reachable: reasons.append("primary source unreachable: "+status)
    if pdf: reasons.append("PDF requires semantic/manual review")
    elif reachable:
        if ratio < .34: reasons.append("event name weak/not found on source")
        if not year_hit: reasons.append("event year/date not found on source")
        if not dog_terms: reasons.append("dog discipline/access not found on source")
    fingerprint=hashlib.sha256(text.encode("utf-8","ignore")).hexdigest()[:16] if text else ""
    if previous and previous.get("Source fingerprint") and fingerprint and previous["Source fingerprint"]!=fingerprint:
        reasons.append("source content changed since previous check")
    return {"Date":row.get("Date",""),"Country":row.get("Country",""),"Event":row.get("Event",""),
      "Primary source":url,"HTTP status":status,"Final URL":final,"Event token match":f"{ratio:.2f}",
      "Year/date marker":str(year_hit).lower(),"Dog marker":str(dog_terms).lower(),
      "Review required":str(bool(reasons)).lower(),"Review reason":"; ".join(reasons),
      "Checked":str(date.today()),"Source fingerprint":fingerprint}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--batch-size",type=int,default=25)
    ap.add_argument("--full",action="store_true")
    args=ap.parse_args()
    master=list(csv.DictReader(MASTER.open(encoding="utf-8")))
    old={}
    if STATE.exists():
        for r in csv.DictReader(STATE.open(encoding="utf-8")): old[key(r)]=r

    today=date.today()
    flagged={k for k,r in old.items() if r.get("Review required")=="true"}
    # Priority: flagged rows, events within 60 days, then oldest checked rows.
    def priority(r):
        k=key(r); d=first_date(r.get("Date","")); delta=(d-today).days
        near=0 <= delta <= 60
        checked=old.get(k,{}).get("Checked","0000-00-00")
        return (0 if k in flagged else 1,0 if near else 1,checked,d,k)
    ordered=sorted(master,key=priority)
    selected=ordered if args.full else ordered[:max(args.batch_size,len([r for r in ordered if key(r) in flagged]))]
    selected_keys={key(r) for r in selected}

    current={}
    for r in master:
        k=key(r)
        if k in selected_keys: current[k]=validate(r,old.get(k))
        elif k in old:
            saved=dict(old[k]); saved.setdefault("Source fingerprint",""); current[k]=saved
        else:
            current[k]={"Date":r.get("Date",""),"Country":r.get("Country",""),"Event":r.get("Event",""),
                "Primary source":r.get("Primary source",""),"HTTP status":"not-checked","Final URL":"",
                "Event token match":"","Year/date marker":"","Dog marker":"","Review required":"true",
                "Review reason":"not yet checked by daily rotation","Checked":"","Source fingerprint":""}

    rows=[current[key(r)] for r in master]
    STATE.parent.mkdir(parents=True,exist_ok=True)
    with STATE.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,extrasaction="ignore"); w.writeheader(); w.writerows(rows)

    bad=[r for r in rows if r["Review required"]=="true"]
    changed=[r for r in rows if "source content changed" in r.get("Review reason","")]
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    with REPORT.open("w",encoding="utf-8") as f:
        f.write("# Daily event validation\n\n")
        f.write(f"Run date: **{today}**. Checked this run: **{len(selected)}** of **{len(rows)}** master rows.\n\n")
        f.write(f"- Review queue: **{len(bad)}**\n- Source-content changes detected this run: **{len(changed)}**\n")
        f.write("- Master rows automatically changed/deleted: **0**\n\n")
        f.write("Flags are a review queue, not proof that an event is wrong. Near-term and previously flagged events are prioritized.\n\n")
        f.write("## Review queue\n\n| Date | Country | Event | HTTP | Checked | Reason |\n|---|---|---|---|---|---|\n")
        for r in bad:
            vals=[r.get(x,"").replace("|","/") for x in ["Date","Country","Event","HTTP status","Checked","Review reason"]]
            f.write("| "+" | ".join(vals)+" |\n")
    print(f"checked={len(selected)} total={len(rows)} review={len(bad)} changed={len(changed)}")

if __name__=="__main__": main()
