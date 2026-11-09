"""Splits the 20 hand-labeled postings into 10 development + 10 held-out (brief Step 4.2, R24-R25).

Why a script, run only after the labels were committed: the split must not be chosen by anyone who
has seen which postings are hard, and it must not have been known while labeling. Why stratified
(random within each label): with only 10 cases per set, a plain shuffle could put most relevant
postings in one set, and a pass rate on 10 cases of one kind says even less. So each set gets
half of the relevant and half of the not_relevant labels, chosen at random with a fixed seed.

Run: .venv/bin/python labels/split.py   -> labels/split.json
"""

import csv
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 7375


def main() -> None:
    rows = list(csv.DictReader(open(HERE / "labels.csv", newline="")))
    assert len(rows) == 20 and all(r["label"] in ("relevant", "not_relevant") for r in rows), "label all 20 first"
    rng = random.Random(SEED)
    dev, held = [], []
    for label in ("relevant", "not_relevant"):
        ids = sorted(int(r["posting_id"]) for r in rows if r["label"] == label)   # sorted: same input every run
        rng.shuffle(ids)
        half = len(ids) // 2
        dev += ids[:half]
        held += ids[half:]
    assert len(dev) == len(held) == 10, (len(dev), len(held))
    doc = {"seed": SEED, "method": "stratified by Isaac's label, random within each label",
           "dev": sorted(dev), "held_out": sorted(held)}
    (HERE / "split.json").write_text(json.dumps(doc, indent=1) + "\n")
    by_id = {int(r["posting_id"]): r["label"] for r in rows}
    for name, ids in (("dev", dev), ("held_out", held)):
        print(name, len(ids), "relevant:", sum(by_id[i] == "relevant" for i in ids))


if __name__ == "__main__":
    main()
