"""Agreement of the automatic claim labeler with my checked labels on the 16 v1.1 shortlist claims.

DEV SET: the labeler fix (2026-11-25) was designed from these 16 claims, so this is not a held-out measurement.
python3 measure_claims.py
"""
import csv
from pathlib import Path

from jsagent3.evidence import label_claim
from jsagent3.mcp_server import load_postings

HERE = Path(__file__).resolve().parent


def claim_for(name):
    if name == "level":
        return {"type": "level", "value": "early-career"}
    if name == "us":
        return {"type": "us"}
    return {"type": "skill", "skill": name, "strength": "required"}


def main():
    posts = load_postings()
    rows = list(csv.DictReader((HERE / "labels" / "shortlist-claims-dev.csv").open()))
    agree = 0
    for r in rows:
        got = label_claim(claim_for(r["claim"]), posts[r["posting_id"]])
        ok = got["label"] == r["my_label"]
        agree += ok
        print(f"{'ok ' if ok else 'BAD'} {r['posting_id'][:22]:22s} {r['claim']:20s} mine={r['my_label']:13s} "
              f"auto={got['label']:13s} {got['why']}")
    print(f"agreement with my labels: {agree}/{len(rows)} (dev set, not held out)")


if __name__ == "__main__":
    main()
