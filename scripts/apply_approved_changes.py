#!/usr/bin/env python3
"""Phase 4: apply explicitly approved proposal patches to a working branch.

Safety model:
- only proposals with Review status == approved are considered;
- a proposal must carry an explicit machine-readable patch in data/event-approved-changes.csv;
- the target master row must match exactly one row;
- no deletion is supported;
- changed fields are allow-listed;
- feeds are rebuilt after the patch.
"""
import csv, subprocess
from datetime import date
from pathlib import Path

MASTER=Path("data/Canitrail_Masterkalender_2026_2027.csv")
PROPOSALS=Path("data/event-update-proposals.csv")
CHANGES=Path("data/event-approved-changes.csv")
ALLOWED={"Date","Country","Event","Category","Dog distance (km)","Elevation (m+)","Dog access","Status","Notes","Primary source","Secondary source","Origin"}
CHANGE_FIELDS=["Proposal ID","Field","New value","Source","Reviewer note"]

def load(path):
    with path.open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f))

def main():
    if not CHANGES.exists():
        CHANGES.parent.mkdir(parents=True,exist_ok=True)
        with CHANGES.open("w",encoding="utf-8",newline="") as f:
            csv.DictWriter(f,fieldnames=CHANGE_FIELDS).writeheader()
        print("No approved change file existed; created template.")
        return
    proposals={r["Proposal ID"]:r for r in load(PROPOSALS)}
    approved={pid:r for pid,r in proposals.items() if r.get("Review status")=="approved"}
    changes=load(CHANGES)
    actionable=[c for c in changes if c.get("Proposal ID") in approved]
    if not actionable:
        print("No explicitly approved proposal patches to apply.")
        return

    with MASTER.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
    if not fields: raise SystemExit("Master calendar has no header.")

    grouped={}
    for change in actionable:
        grouped.setdefault(change["Proposal ID"],[]).append(change)

    applied=[]
    for pid,patches in grouped.items():
        p=approved[pid]
        matches=[i for i,r in enumerate(rows) if r.get("Date")==p.get("Date") and r.get("Country")==p.get("Country") and r.get("Event")==p.get("Event")]
        if len(matches)!=1: raise SystemExit(f"{pid}: expected exactly one master row, found {len(matches)}")
        i=matches[0]
        for change in patches:
            field=change.get("Field","")
            if field not in ALLOWED: raise SystemExit(f"{pid}: field not allowed: {field!r}")
            old=rows[i].get(field,""); new=change.get("New value","")
            if old==new: continue
            rows[i][field]=new
            if field!="Origin":
                rows[i]["Origin"]=f"approved proposal {pid} {date.today()}"
            applied.append((pid,field,old,new,change.get("Source","")))

    if not applied:
        print("Approved patches produce no master changes.")
        return
    with MASTER.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

    subprocess.run(["python","scripts/dedupe_master.py"],check=True)
    subprocess.run(["python","scripts/build_events.py"],check=True)
    print(f"Applied {len(applied)} approved field change(s).")
    for pid,field,old,new,source in applied:
        print(f"{pid}: {field}: {old!r} -> {new!r} source={source}")

if __name__=="__main__": main()
