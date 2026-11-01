"""Dry run of the RULE (record) over every posting in one saved raw response, ignoring the
state file, to show what the rule flags and what it drops. No network, no Claude.

    python3 -m experiments.whole_board runs/raw-klaviyo-<ts>.json > experiments/whole-board-<date>.md"""
import json
import sys
from collections import Counter

from experiments.common import RESUME
from jsagent import persona, rule

raw = sys.argv[1]
with open(raw, encoding="utf-8") as f:
    jobs = json.load(f)["jobs"]
resume = persona.load(RESUME)
res = [(j, rule.judge(j, resume)) for j in sorted(jobs, key=lambda j: j["title"])]
fails = Counter("".join(k for k in "ABC" if not r["clauses"][k]["pass"]) or "-" for _, r in res)
rel = [(j, r) for j, r in res if r["verdict"] == "relevant"]
print(f"# Whole-board view of the rule — `{raw.split('/')[-1]}`\n")
print(f"Dry run of the written rule over all {len(jobs)} postings (state ignored). No Claude involved.\n")
print(f"- relevant: **{len(rel)}**, not_relevant: {len(jobs) - len(rel)}")
print(f"- clauses failed (A=role, B=location, C=skills): " + ", ".join(f"{k}: {v}" for k, v in sorted(fails.items())))
print("\n## Relevant by the rule\n")
print("| id | title | location | skills found |\n|---|---|---|---|")
for j, r in rel:
    print(f"| {j['id']} | {j['title']} | {j['location']['name']} | {', '.join(r['clauses']['C']['found'])} |")
print("\n## Pass A (\"Software Engineer\" in title) but dropped by B or C\n")
print("| id | title | location | B | skills found (C) |\n|---|---|---|---|---|")
for j, r in res:
    c = r["clauses"]
    if c["A"]["pass"] and r["verdict"] != "relevant":
        print(f"| {j['id']} | {j['title']} | {j['location']['name']} | {'PASS' if c['B']['pass'] else 'FAIL'} | {', '.join(c['C']['found']) or 'none'} |")
print("\n## Engineering-department postings that fail A (title lacks \"Software Engineer\")\n")
for j, r in res:
    if not r["clauses"]["A"]["pass"] and any(d["name"] == "Engineering" for d in j["departments"]):
        print(f"- {j['title']} ({j['location']['name']}) — skills found: {', '.join(r['clauses']['C']['found']) or 'none'}")
