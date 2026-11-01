"""Pick the 20 experiment postings from the real run-1 response, before any labels or Claude calls.

Stratified so the set is not all easy negatives: 10 the rule calls relevant, 10 the rule calls
not_relevant whose title still contains 'engineer' (the hard cases). Fixed seed; the split into
development and held-out is a second seeded shuffle. Sampling uses the first 5 development postings.

    python3 scripts/pick_postings.py evidence/raw/anthropic-20261101T185817Z.json
"""
import json
import random
import sys

sys.path.insert(0, ".")
from agent.resume import load_resume  # noqa: E402
from agent.rule import judge_rule, words  # noqa: E402

SEED = 7375
raw = sys.argv[1]
resume = load_resume("personas/priya-nair.resume.json")
jobs = json.load(open(raw, encoding="utf-8"))["jobs"]

rel = [j for j in jobs if judge_rule(j, resume)["verdict"] == "relevant"]
hard = [j for j in jobs if judge_rule(j, resume)["verdict"] == "not_relevant" and "engineer" in words(j["title"])]
rng = random.Random(SEED)
picked = rng.sample(rel, 10) + rng.sample(hard, 10)
rng.shuffle(picked)

out = []
for i, j in enumerate(picked):
    out.append({"id": j["id"], "split": "dev" if i < 10 else "heldout", "title": j["title"].strip(),
                "location": (j.get("location") or {}).get("name"), "url": j["absolute_url"]})
json.dump({"source": raw, "seed": SEED, "postings": out}, open("labels/experiment_set.json", "w"), indent=2)
for p in out:
    print(p["split"], p["id"], p["title"], "|", p["location"])
