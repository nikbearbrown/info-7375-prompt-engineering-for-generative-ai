"""Review packet step 3: read the diff as a change in behaviour. Runs R3 from review/rule_before_r3.py (the rule before the
R3 change) and agent/rule.py (after) on every real posting saved by run 1, and lists every location whose
R3 result changed, plus every posting whose final rule verdict changed."""
import collections
import glob
import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import ats  # noqa: E402
from agent import rule as after  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rule_before_r3", os.path.join(here, "rule_before_r3.py"))
before = importlib.util.module_from_spec(spec)
spec.loader.exec_module(before)

resume = json.load(open("persona/resume.json", encoding="utf-8"))
changed, verdicts, n = collections.Counter(), [], 0
for f in sorted(glob.glob("runs/live/evidence/20261109T211138Z-*.json")):  # run 1 only
    system = os.path.basename(f).split("Z-")[1].split("-")[0]
    for p in ats.parse(system, open(f, "rb").read()):
        n += 1
        b, a = before.judge(p, resume), after.judge(p, resume)
        r3b = {r["check"]: r for r in b["reasons"]}["R3"]["result"]
        r3a = {r["check"]: r for r in a["reasons"]}["R3"]["result"]
        if r3b != r3a:
            changed[(r3b, r3a, p["location"].get("name", ""))] += 1
        if b["verdict"] != a["verdict"]:
            verdicts.append((system, p["id"], p["title"], p["location"].get("name", ""), b["verdict"], a["verdict"]))
print(f"{n} real postings; R3 changed on {sum(changed.values())}; final verdict changed on {len(verdicts)}")
print("R3 changes by location (before -> after, count):")
for (b, a, loc), c in sorted(changed.items(), key=lambda x: -x[1]):
    print(f"  {b} -> {a}  x{c}  {loc}")
print("final verdict changes:")
for v in verdicts:
    print("  ", *v)
