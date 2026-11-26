"""Blind sheet for the claims whose label changed with the labeler fix (v1 shortlist, excluding the 16-claim dev set).

python3 make_label_check.py evidence/old/evidence_before_fix_401cacdb.py   (pre-fix labeler, copied from commit 401cacdb)
Writes labels/changed-claims-to-check.md (no labels shown) and labels/changed-claims.csv (old/new hidden from the sheet).
"""
import csv
import importlib.util
import sys
from pathlib import Path

import jsagent3.evidence as new_ev
from jsagent3.filter import decide, load_rules
from jsagent3.mcp_server import load_postings

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("jsagent3.old_evidence", sys.argv[1], submodule_search_locations=None)
old_ev = importlib.util.module_from_spec(spec)
old_ev.__package__ = "jsagent3"
spec.loader.exec_module(old_ev)

dev = {(r["posting_id"], r["claim"]) for r in csv.DictReader((HERE / "labels" / "shortlist-claims-dev.csv").open())}
rules = load_rules("v1")
rows = []
for p in load_postings().values():
    d = decide(p, rules)
    if not d["keep"]:
        continue
    for o, n in zip(old_ev.justify(p, d, rules), new_ev.justify(p, d, rules)):
        name = n["claim"].get("skill", n["claim"]["type"])
        if o["label"] != n["label"] and (p["id"], name) not in dev:
            rows.append({"id": p["id"], "title": p["title"], "claim": name, "old": o["label"], "new": n["label"],
                         "quote": n["quote"] or o["quote"]})
with (HERE / "labels" / "changed-claims.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["n", "id", "title", "claim", "old", "new", "my_label", "quote"])
    w.writeheader()
    for i, r in enumerate(rows, 1):
        w.writerow({"n": i, **r, "my_label": ""})
with (HERE / "labels" / "changed-claims-to-check.md").open("w") as f:
    f.write("# Claims whose label the fix changed: judge blind (old and new labels hidden)\n\n"
            "For each claim, read the quoted line (open the link if needed) and answer S, C or I:\n"
            "S = the posting requires it / supports it, C = the posting says the opposite or lists it only as optional,\n"
            "I = the posting does not establish it.\n\n")
    for i, r in enumerate(rows, 1):
        what = {"level": "early-career level", "us": "US-based"}.get(r["claim"], f"requires {r['claim']}")
        f.write(f"**{i}.** {r['title']} ({r['id']}): claim: *{what}*  \n> {r['quote'][:300]}\n\n")
print(len(rows), "changed claims outside the dev set")
