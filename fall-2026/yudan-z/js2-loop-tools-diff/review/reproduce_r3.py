"""Review packet step 1: reproduce the R3 defect on the real responses saved by run 1 (runs/live/evidence/).
Prints how many real postings fail R3 although their location names a US state in full."""
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import ats, rule  # noqa: E402

FULL = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
        "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
        "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
        "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
        "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
sys.stdout.reconfigure(encoding="utf-8")
resume = json.load(open("persona/resume.json", encoding="utf-8"))
hit, total, ex = collections.Counter(), collections.Counter(), {}
for f in sorted(glob.glob("runs/live/evidence/20261109T211138Z-*.json")):  # run 1 only
    system = os.path.basename(f).split("Z-")[1].split("-")[0]
    for p in ats.parse(system, open(f, "rb").read()):
        loc = p["location"].get("name", "")
        total[system] += 1
        r3 = {r["check"]: r for r in rule.judge(p, resume)["reasons"]}["R3"]
        if r3["result"] == "fail" and any(s in loc for s in FULL):
            hit[system] += 1
            ex.setdefault(loc, (os.path.basename(f), p["id"], p["title"]))
print(f"rule.py R3 on {sum(total.values())} real postings from {len(total)} systems")
for s in total:
    print(f"  {s}: {hit[s]} of {total[s]} fail R3 although the location names a US state in full")
print("examples (evidence file, posting id, title):")
for loc, (f, i, t) in list(ex.items())[:8]:
    print(f"  {loc!r}: {f} {i} {t}")
