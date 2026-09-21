#!/usr/bin/env python3
"""Build a deterministic human-review queue from Phase 2 validation results.

Phase 3 deliberately does not edit the master calendar. It converts validator
findings into stable proposed actions that can be reviewed before any data
change is made.
"""
import csv, hashlib
from datetime import date
from pathlib import Path

VALIDATION=Path("data/event-validation.csv")
OUT=Path("data/event-update-proposals.csv")
REPORT=Path("reports/event-validation/proposals.md")

FIELDS=["Proposal ID","Date","Country","Event","Primary source","Final URL","Proposed action",
        "Confidence","Evidence","Review status","Created","Last checked"]

def proposal_id(r):
    raw="|".join([r.get("Date",""),r.get("Country",""),r.get("Event",""),r.get("Primary source","")])
    return "EV-"+hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10].upper()

def classify(r):
    reason=r.get("Review reason","")
    status=r.get("HTTP status","")
    if "missing primary source" in reason:
        return "find-source","high","No primary source is stored."
    if status in {"404","410"}:
        return "replace-source-or-confirm-cancelled","high",f"Primary source returns HTTP {status}."
    if status.startswith("error:") or status in {"401","403","429"}:
        return "manual-source-check","medium",f"Automated access failed ({status}); do not infer an event change."
    if "source content changed since previous check" in reason:
        return "review-source-change","medium","Source fingerprint changed since the previous validation."
    if "event year/date not found on source" in reason:
        return "verify-date","medium","Stored event year/date was not found in fetched source text."
    if "dog discipline/access not found on source" in reason:
        return "verify-dog-eligibility","medium","Dog discipline/access marker was not found in fetched source text."
    if "event name weak/not found on source" in reason:
        return "verify-event-identity","medium","Event-name match against fetched source text is weak."
    if "PDF requires semantic/manual review" in reason:
        return "manual-document-review","medium","Primary evidence is a PDF and needs semantic/manual review."
    if "not yet checked by daily rotation" in reason:
        return "await-validation","low","Entry has not yet reached the daily validation rotation."
    return "manual-review","low",reason or "Validator requested review."

def main():
    rows=list(csv.DictReader(VALIDATION.open(encoding="utf-8")))
    old={}
    if OUT.exists():
        for r in csv.DictReader(OUT.open(encoding="utf-8")):
            old[r["Proposal ID"]]=r
    proposals=[]
    today=str(date.today())
    for r in rows:
        if r.get("Review required")!="true":
            continue
        pid=proposal_id(r)
        action,confidence,evidence=classify(r)
        prev=old.get(pid,{})
        proposals.append({
            "Proposal ID":pid,"Date":r.get("Date",""),"Country":r.get("Country",""),"Event":r.get("Event",""),
            "Primary source":r.get("Primary source",""),"Final URL":r.get("Final URL",""),
            "Proposed action":action,"Confidence":confidence,"Evidence":evidence,
            "Review status":prev.get("Review status","pending") or "pending",
            "Created":prev.get("Created","") or today,"Last checked":r.get("Checked","")
        })
    proposals.sort(key=lambda r:(r["Review status"]!="pending",r["Date"],r["Country"],r["Event"]))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(proposals)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    pending=[r for r in proposals if r["Review status"]=="pending"]
    with REPORT.open("w",encoding="utf-8") as f:
        f.write("# Phase 3 event update proposals\n\n")
        f.write(f"Generated: **{today}**. Pending proposals: **{len(pending)}**.\n\n")
        f.write("These are review proposals only. This process makes **no automatic master-calendar changes or deletions**.\n\n")
        f.write("| ID | Date | Country | Event | Action | Confidence | Evidence |\n|---|---|---|---|---|---|---|\n")
        for r in pending:
            vals=[r[x].replace("|","/") for x in ["Proposal ID","Date","Country","Event","Proposed action","Confidence","Evidence"]]
            f.write("| "+" | ".join(vals)+" |\n")
    print(f"proposals={len(proposals)} pending={len(pending)}")

if __name__=="__main__":
    main()
