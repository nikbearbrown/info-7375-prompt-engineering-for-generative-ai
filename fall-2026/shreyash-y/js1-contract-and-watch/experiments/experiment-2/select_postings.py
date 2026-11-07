"""Experiment 2 (added 2026-10-31 after the TA-style review): pick 20 real Klaviyo postings for
hand labeling, from the saved raw response. Committed, with its output, before Shreyash labeled
anything and before any Claude call on Klaviyo.

Procedure, fixed in advance:
1. Pool = postings whose title passes condition 1 (22 of 156). Repeated titles in other cities are
   kept, because the city changes condition 3.
2. So that both halves can test positives, the pool is split by the rule v1 record: Relevant (4)
   and the rest (18). random.Random(7376) shuffles each part.
3. Development = 2 Relevant + 8 others; held-out = the other 2 Relevant + the next 8 others.
   2 of the 18 others are left out.
The output file does not say which postings the rule marks Relevant, and neither does the label
sheet. Shreyash labels without seeing any verdict."""
import json
import pathlib
import random

from jsagent import persona, posting, rule

RAW = sorted(pathlib.Path("experiments/experiment-2/raw").glob("klaviyo-*.json"))[0]
jobs = json.loads(RAW.read_bytes())["jobs"]
view = persona.public_view(persona.load("persona/alex_morgan.json"))
recs = {j["id"]: rule.judge(posting.normalize(j, "klaviyo"), view) for j in jobs}
pool = sorted((j for j in jobs if 1 not in recs[j["id"]]["failed_conditions"]), key=lambda j: j["id"])
pos = [j for j in pool if recs[j["id"]]["verdict"] == "Relevant"]
neg = [j for j in pool if recs[j["id"]]["verdict"] != "Relevant"]
rng = random.Random(7376)
rng.shuffle(pos)
rng.shuffle(neg)
dev, held = pos[:2] + neg[:8], pos[2:4] + neg[8:16]
rng.shuffle(dev)
rng.shuffle(held)
item = lambda j: {"id": j["id"], "title": j["title"].strip(), "location": j["location"]["name"]}
out = {"raw_file": str(RAW), "procedure": __doc__.strip(), "pool_size": len(pool),
       "development": [item(j) for j in dev], "held_out": [item(j) for j in held]}
pathlib.Path("experiments/experiment-2/selected_postings.json").write_text(json.dumps(out, indent=2) + "\n")
print(f"pool {len(pool)}; wrote experiments/experiment-2/selected_postings.json (10 development, 10 held-out)")
