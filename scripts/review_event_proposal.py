#!/usr/bin/env python3
"""Phase 5: turn a simple reviewer decision into Phase 4 queue data."""
import argparse,csv
from pathlib import Path

PROPOSALS=Path("data/event-update-proposals.csv")
CHANGES=Path("data/event-approved-changes.csv")
FIELDS=["Proposal ID","Field","New value","Source","Reviewer note"]
ALLOWED={"Date","Country","Event","Category","Dog distance (km)","Elevation (m+)","Dog access","Status","Notes","Primary source","Secondary source","Origin"}

def read(path):
    with path.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))

def write(path,rows,fields):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--proposal",required=True)
    p.add_argument("--decision",required=True,choices=["approve","reject"])
    p.add_argument("--field")
    p.add_argument("--value")
    p.add_argument("--source",default="")
    p.add_argument("--note",default="")
    a=p.parse_args()
    if not PROPOSALS.exists(): raise SystemExit("Proposal queue does not exist yet. Run Phase 3 first.")
    rows=read(PROPOSALS); matches=[r for r in rows if r.get("Proposal ID")==a.proposal]
    if len(matches)!=1: raise SystemExit(f"Expected exactly one proposal {a.proposal}, found {len(matches)}")
    proposal=matches[0]
    if a.decision=="approve":
        if not a.field or a.value is None: raise SystemExit("Approval requires --field and --value.")
        if a.field not in ALLOWED: raise SystemExit(f"Field not allowed: {a.field}")
        proposal["Review status"]="approved"
        changes=read(CHANGES) if CHANGES.exists() else []
        key=(a.proposal,a.field)
        changes=[r for r in changes if (r.get("Proposal ID"),r.get("Field"))!=key]
        changes.append({"Proposal ID":a.proposal,"Field":a.field,"New value":a.value,"Source":a.source or proposal.get("Final URL") or proposal.get("Primary source",""),"Reviewer note":a.note})
        write(CHANGES,changes,FIELDS)
    else:
        proposal["Review status"]="rejected"
        if CHANGES.exists():
            changes=[r for r in read(CHANGES) if r.get("Proposal ID")!=a.proposal]
            write(CHANGES,changes,FIELDS)
    write(PROPOSALS,rows,list(rows[0].keys()))
    print(f"{a.proposal}: {a.decision} recorded.")

if __name__=="__main__":main()
