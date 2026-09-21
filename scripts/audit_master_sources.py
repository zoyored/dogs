#!/usr/bin/env python3
import csv, re, ssl, time, urllib.request, urllib.error
from pathlib import Path
from html import unescape
from datetime import date

MASTER=Path("data/Canitrail_Masterkalender_2026_2027.csv")
OUT=Path("data/event-validation.csv")
REPORT=Path("reports/event-validation/latest.md")
UA="Mozilla/5.0 (compatible; SandsturmEventAudit/1.0; +https://sandsturm.com/)"

def norm(s):
    return re.sub(r"[^a-z0-9]+"," ",unescape((s or "").lower())).strip()
def tokens(s):
    stop={"the","and","und","des","der","die","de","du","la","le","les","trail","canicross","canitrail","2026","2027"}
    return [x for x in norm(s).split() if len(x)>=4 and x not in stop]
def fetch(url):
    if not url: return ("missing","","")
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml,application/pdf;q=0.8,*/*;q=0.5"})
    ctx=ssl.create_default_context()
    try:
        with urllib.request.urlopen(req,timeout=25,context=ctx) as r:
            raw=r.read(1200000)
            ctype=r.headers.get("Content-Type","")
            final=r.geturl()
            if "pdf" in ctype.lower() or raw[:4]==b"%PDF": return (str(r.status),final,"[pdf]")
            text=raw.decode("utf-8","ignore")
            text=re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>"," ",text,flags=re.I|re.S)
            text=re.sub(r"<[^>]+>"," ",text)
            return (str(r.status),final,norm(text))
    except urllib.error.HTTPError as e: return (str(e.code),url,"")
    except Exception as e: return ("error:"+type(e).__name__,url,"")

rows=list(csv.DictReader(MASTER.open(encoding="utf-8")))
out=[]
for i,row in enumerate(rows,1):
    url=row.get("Primary source","").strip()
    status,final,text=fetch(url)
    ev_tokens=tokens(row["Event"])
    hit=sum(1 for t in ev_tokens if t in text)
    ratio=(hit/len(ev_tokens)) if ev_tokens else 0
    years=re.findall(r"20\d{2}",row["Date"])
    year_hit=any(y in text for y in years) if text and text!="[pdf]" else False
    dog_terms=any(x in text for x in ["canicross","canitrail","dog ","dogs ","hund","chien","cani ","mushing","bikejor","scooter","sled","sledge","skijor","pulka"]) if text and text!="[pdf]" else False
    reachable=status.startswith("2") or status.startswith("3")
    reasons=[]
    if not url: reasons.append("missing primary source")
    elif not reachable: reasons.append("primary source unreachable: "+status)
    if text=="[pdf]": reasons.append("PDF requires semantic/manual review")
    elif reachable:
        if ratio < 0.34: reasons.append("event name weak/not found on source")
        if not year_hit: reasons.append("event year/date not found on source")
        if not dog_terms: reasons.append("dog discipline/access not found on source")
    review=bool(reasons)
    out.append({
      "Date":row["Date"],"Country":row["Country"],"Event":row["Event"],"Primary source":url,
      "HTTP status":status,"Final URL":final,"Event token match":f"{ratio:.2f}",
      "Year/date marker":str(year_hit).lower(),"Dog marker":str(dog_terms).lower(),
      "Review required":str(review).lower(),"Review reason":"; ".join(reasons),
      "Checked":str(date.today())
    })
    time.sleep(.08)

OUT.parent.mkdir(parents=True,exist_ok=True)
with OUT.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
REPORT.parent.mkdir(parents=True,exist_ok=True)
bad=[r for r in out if r["Review required"]=="true"]
unreach=[r for r in out if r["HTTP status"].startswith("4") or r["HTTP status"].startswith("5") or r["HTTP status"].startswith("error")]
with REPORT.open("w",encoding="utf-8") as f:
    f.write("# Full master source audit\n\n")
    f.write(f"Checked **{len(out)}** master rows against their primary sources on {date.today()}.\n\n")
    f.write(f"- Reachability/content review required: **{len(bad)}**\n- Unreachable/error primary sources: **{len(unreach)}**\n- No automated flag: **{len(out)-len(bad)}**\n\n")
    f.write("Automated checks are conservative. A flag is a review queue, not proof that an event is wrong. No master row is changed automatically.\n\n")
    f.write("## Review queue\n\n| Date | Country | Event | HTTP | Reason |\n|---|---|---|---|---|\n")
    for r in bad:
        reason=r["Review reason"].replace("|","/")
        f.write(f"| {r['Date']} | {r['Country']} | {r['Event']} | {r['HTTP status']} | {reason} |\n")
print(f"checked={len(out)} review={len(bad)} unreachable={len(unreach)}")
