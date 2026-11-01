"""Pick the 20 real postings for the prompt experiment, deterministically, before anyone
labels or prompts anything. Rule (Claude's, 2026-10-25): from one saved raw response,
12 engineering postings (title contains "Engineer" or department is Engineering) and
8 others, drawn with random.Random(7375); within each stratum, alternate dev/held-out.

    python3 -m experiments.prompt.select_postings RAW_RESPONSE.json
Writes postings-20.json (full posting text) and labels.csv (blank label columns)."""
import csv
import json
import random
import sys

from experiments.common import EXP, LABELS, POSTINGS
import os

SEED, N_ENG, N_OTHER = 7375, 12, 8


def is_eng(j):
    return "engineer" in j["title"].lower() or any(d["name"] == "Engineering" for d in j["departments"])


def main(raw):
    if os.path.exists(LABELS):
        sys.exit(f"{LABELS} exists; refusing to reselect after labelling may have started")
    with open(raw, encoding="utf-8") as f:
        jobs = sorted(json.load(f)["jobs"], key=lambda j: j["id"])
    rng = random.Random(SEED)
    picked = []
    for pool, n in (([j for j in jobs if is_eng(j)], N_ENG), ([j for j in jobs if not is_eng(j)], N_OTHER)):
        chosen = rng.sample(pool, n)
        picked += [(j, "dev" if i % 2 == 0 else "heldout") for i, j in enumerate(chosen)]
    with open(POSTINGS, "w", encoding="utf-8") as f:
        json.dump({"_source": os.path.basename(raw), "_selection": __doc__.strip().splitlines()[1:4],
                   "jobs": [j for j, _ in picked]}, f, indent=1)
    with open(LABELS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["posting_id", "split", "title", "location", "url", "omkar_label", "omkar_note"])
        for j, split in sorted(picked, key=lambda x: (x[1], x[0]["id"])):
            w.writerow([j["id"], split, j["title"], j["location"]["name"], j["absolute_url"], "", ""])
    print(f"wrote {POSTINGS} and {LABELS}: 10 dev, 10 heldout")


if __name__ == "__main__":
    main(sys.argv[1])
