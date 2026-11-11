"""Run 2 check: judge run 2's NEW postings with the JS1 rule (review/rule_before_r3.py, before the accepted R3 change)
and with the current rule, and list every posting where R3 or the final verdict differs."""
import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import ats  # noqa: E402
from agent import rule as now  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rule_before_r3", os.path.join(here, "rule_before_r3.py"))
js1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(js1)

resume = json.load(open("persona/resume.json", encoding="utf-8"))
run = json.load(open(sys.argv[1], encoding="utf-8"))
n, r3_diff, verdict_diff = 0, [], 0
for b in run["boards"]:
    for p in b.get("new_postings", []):
        n += 1
        posting = {"id": p["id"], "title": p["title"], "location": {"name": p["location"]}, "content": ""}
        # content is needed for R4-R9; take it from the saved raw response
        raw = open(os.path.join(os.path.dirname(sys.argv[1]), b["evidence"]), "rb").read()
        for q in ats.parse(b["system"], raw):
            if q["id"] == p["id"]:
                posting = q
        old, new = js1.judge(posting, resume), now.judge(posting, resume)
        o3 = {r["check"]: r["result"] for r in old["reasons"]}["R3"]
        n3 = {r["check"]: r["result"] for r in new["reasons"]}["R3"]
        if o3 != n3:
            r3_diff.append(f"  {b['board']} {p['id']} {p['title']!r} ({p['location']}): R3 {o3} -> {n3}; verdict {old['verdict']} -> {new['verdict']}")
        verdict_diff += old["verdict"] != new["verdict"]
print(f"run {run['run']}: {n} new postings; R3 differs on {len(r3_diff)}; final verdict differs on {verdict_diff}")
print("\n".join(r3_diff))
