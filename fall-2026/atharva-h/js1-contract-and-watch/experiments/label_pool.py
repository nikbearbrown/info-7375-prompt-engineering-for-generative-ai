"""Fetch the label pool for the prompt experiment and pick 20 postings to hand-label.

    python3 experiments/label_pool.py

Boards are Greenhouse boards of employers on my H-1B list, read through the same
allow-listed fetch as the watch. Raw responses are saved byte for byte. Selection uses
titles only, never the rule's verdict, so the rule cannot pick its own test set.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import watch  # noqa: E402
from rule import normalize  # noqa: E402

# Employers on my H-1B list whose Greenhouse slug is distinctive enough to trust the match by name
# (probed 2026-10-31). Ambiguous slugs such as "mercury", "rga", "impact", and "abc" are left out.
BOARDS = ("abacusinsights", "beyondfinance", "duolingo", "redwoodmaterials", "asteralabs",
          "alphasense", "artefact", "businessolver", "cloudflare", "scopely", "point72", "woolpert",
          "joblogic", "yqn", "freedomcare", "natera", "schonfeld", "coherehealth", "thrivemarket")
TARGET_WORDS = ("data analyst", "bi analyst", "business intelligence analyst", "business analyst")
NEAR_WORDS = ("analyst", "analytics", "business intelligence", "data")
QUOTA = {0: 14, 1: 4, 2: 2}  # target-title, near-miss, and other postings
SEED = 7375


def main():
    raw_dir = os.path.join(HERE, "label_pool", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    pool = []
    for board in BOARDS:
        raw = watch.fetch(watch.BOARD_URL.format(board=board))
        with open(os.path.join(raw_dir, f"{board}.json"), "wb") as f:
            f.write(raw)
        for job in json.loads(raw)["jobs"]:
            pool.append((board, job))
    def tier(job):
        title = f" {normalize(job['title'])} "
        if any(f" {w} " in title for w in TARGET_WORDS):
            return 0
        if any(f" {w} " in title for w in NEAR_WORDS):
            return 1
        return 2
    rng = random.Random(SEED)
    picked = []
    for t in (0, 1, 2):
        group = sorted((p for p in pool if tier(p[1]) == t), key=lambda p: (p[0], p[1]["id"]))
        rng.shuffle(group)
        picked += group[:QUOTA[t]]
    rng.shuffle(picked)
    split = [{"board": b, "id": j["id"], "title": j["title"], "location": (j.get("location") or {}).get("name"),
              "url": j.get("absolute_url"), "set": "development" if i < 10 else "held_out"}
             for i, (b, j) in enumerate(picked)]
    with open(os.path.join(HERE, "label_pool", "selection.json"), "w", encoding="utf-8") as f:
        json.dump({"seed": SEED, "boards": BOARDS, "pool_size": len(pool), "quota": QUOTA,
                   "tiers": {"0": "title has a target phrase", "1": "title has analyst/analytics/data",
                             "2": "anything else"}, "postings": split}, f, indent=2, ensure_ascii=False)
        f.write("\n")
    counts = {t: sum(tier(j) == t for _, j in pool) for t in (0, 1, 2)}
    print(f"pool {len(pool)} postings; tier counts {counts}")
    for s in split:
        print(f"{s['set']:12} {s['board']:16} {s['id']:>12}  {s['title'][:60]:60} {s['location']}")


if __name__ == "__main__":
    main()
