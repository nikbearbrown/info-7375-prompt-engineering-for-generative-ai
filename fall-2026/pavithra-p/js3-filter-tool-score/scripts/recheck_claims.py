"""Re-runs the evidence checker on the saved shortlist claims (no Claude call) and compares it with my claim labels.

    python3 scripts/recheck_claims.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.chdir(HERE)

from agent import collection, config, evidence, filter as filt, resume  # noqa: E402
from agent.policy import Policy  # noqa: E402

entries = json.load(open("runs/20261125T204144Z/shortlist-v1.1/shortlist.json"))
postings, _ = collection.load_run(config.RUNS_DIR / "20261125T204144Z", Policy())
jobs = {f"{b}:{j['id']}": j for b, j in postings}
spec = filt.load_filter("filters/v1.1.json")
skills = filt.resume_skills(resume.load(config.RESUME), spec["skill_lists"])
mine = {r["claim_id"]: r["my_label"] for r in csv.DictReader(open("audit/claim-labels.csv"))}
before = after = 0
for e in entries:
    for i, c in enumerate(e["claims"], 1):
        now = evidence.label_claim(c, jobs[e["key"]], spec, skills)[0]
        mark = mine[f"{e['key']}#{i}"]
        before += c["machine_label"] == mark
        after += now == mark
        if now != c["machine_label"]:
            print(f"changed: {e['title']} ({c['about']}): {c['machine_label']} -> {now}; mine: {mark}")
print(f"checker agrees with my labels: {before} of 37 when the shortlist ran, {after} of 37 now")
