"""Draw the audit sample (dev) and the held-out sample from filter v1.0's results. SEEDED.

    python3 scripts/make_samples.py --seed 7375

labels/audit_sheet.csv   dev:  35 random rejects + 12 closest calls (|margin| <= 1) + 10 random keeps
labels/heldout_sheet.csv held-out: 15 random keeps + 15 random rejects, disjoint from dev

Rows are shuffled and the sheet the labeler sees has no filter decision or score, so the
hand label is blind to the filter. The stratum and filter decision are kept in a separate key
file (labels/*_key.csv) that label.py never reads.
Refuses to overwrite an existing sheet: the sample is drawn once.
"""
import argparse
import csv
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET_COLS = ["row", "uid", "title", "hand_label", "note", "labelled_at"]
KEY_COLS = ["row", "uid", "stratum", "filter_decision", "score", "margin"]


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7375)
    ap.add_argument("--results", default=os.path.join(HERE, "out", "filter", "v1.0", "results.jsonl"))
    a = ap.parse_args(argv)
    labels = os.path.join(HERE, "labels")
    for name in ("audit_sheet.csv", "heldout_sheet.csv"):
        if os.path.exists(os.path.join(labels, name)):
            sys.exit(f"labels/{name} exists; the sample is drawn once. Delete it by hand only if you mean to redraw.")
    with open(a.results, encoding="utf-8") as f:
        R = [json.loads(line) for line in f]
    rng = random.Random(a.seed)
    rejects = [r for r in R if r["decision"] == "reject"]
    keeps = [r for r in R if r["decision"] == "keep"]

    rand_rej = rng.sample(rejects, 35)
    used = {r["uid"] for r in rand_rej}
    below = [r for r in rejects if r["margin"] == -1 and r["uid"] not in used]
    at0 = [r for r in keeps if r["margin"] == 0]          # exactly at the threshold: all of them
    at1 = [r for r in keeps if r["margin"] == 1]
    at = at0 + rng.sample(at1, max(0, 6 - len(at0)))
    near = rng.sample(below, 6) + at
    used |= {r["uid"] for r in near}
    rand_keep = rng.sample([r for r in keeps if r["uid"] not in used], 10)
    used |= {r["uid"] for r in rand_keep}

    dev = ([dict(r, stratum="random_reject") for r in rand_rej] + [dict(r, stratum="near_threshold") for r in near]
           + [dict(r, stratum="random_keep") for r in rand_keep])
    held = ([dict(r, stratum="heldout_keep") for r in rng.sample([r for r in keeps if r["uid"] not in used], 15)]
            + [dict(r, stratum="heldout_reject") for r in rng.sample([r for r in rejects if r["uid"] not in used], 15)])

    for name, rows in (("audit", dev), ("heldout", held)):
        rng.shuffle(rows)
        for i, r in enumerate(rows, 1):
            r["row"] = i
            r["filter_decision"] = r["decision"]
        write(os.path.join(labels, f"{name}_sheet.csv"), SHEET_COLS, rows)
        write(os.path.join(labels, f"{name}_key.csv"), KEY_COLS, rows)
        print(f"labels/{name}_sheet.csv: {len(rows)} rows")
    with open(os.path.join(labels, "SAMPLE.json"), "w", encoding="utf-8") as f:
        json.dump({"seed": a.seed, "results": os.path.relpath(a.results, HERE), "population_rejects": len(rejects),
                   "population_keeps": len(keeps), "dev": len(dev), "heldout": len(held),
                   "near_threshold_pool": {"margin_-1_rejects": len(below), "margin_0_keeps": len(at0), "margin_1_keeps": len(at1)}}, f, indent=2)


if __name__ == "__main__":
    main()
