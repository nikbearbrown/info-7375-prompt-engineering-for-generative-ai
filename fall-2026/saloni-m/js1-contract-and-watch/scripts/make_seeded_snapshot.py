"""SEEDED: build an 'earlier' board response from a real saved one.

Keeps only postings whose first_published is before CUTOFF. This approximates the board as it
was on CUTOFF: it cannot bring back postings that closed since, so it is a constructed input,
labelled as such, not a second real fetch.

    python3 scripts/make_seeded_snapshot.py evidence/raw/<real>.json 2026-10-29 evidence/seeded/<out>.json
"""
import json
import os
import sys

src, cutoff, dst = sys.argv[1:4]
with open(src, encoding="utf-8") as f:
    data = json.load(f)
kept = [j for j in data["jobs"] if j["first_published"][:10] < cutoff]
data["jobs"] = kept
data["_SEEDED"] = {"from": src, "rule": f"first_published < {cutoff}", "kept": len(kept),
                   "note": "constructed from a real response; not a real fetch"}
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst, "w", encoding="utf-8") as f:
    json.dump(data, f)
print(f"SEEDED snapshot: kept {len(kept)} postings published before {cutoff} -> {dst}")
