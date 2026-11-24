"""Compare a saved filter run with my hand labels. Reads files only; runs no rules.

    python3 -m agent.evaluate evidence/filter-v1.2/decisions.jsonl labels/heldout.csv

Prints tp/fp/fn/tn, precision, recall, and every disagreement.
"""

from __future__ import annotations

import csv
import json
import sys


def evaluate(decisions_path: str, labels_path: str) -> dict:
    ds = {json.loads(l)["uid"]: json.loads(l) for l in open(decisions_path, encoding="utf-8")}
    cells = {"tp": [], "fp": [], "fn": [], "tn": []}
    for r in csv.DictReader(open(labels_path, encoding="utf-8")):
        mine, got = r["my_label"] == "keep", ds[r["uid"]]["keep"]
        cells[("t" if mine == got else "f") + ("p" if got else "n")].append((r, ds[r["uid"]]))
    return cells


def main(argv=None) -> int:
    dec, lab = (argv or sys.argv[1:])[:2]
    c = evaluate(dec, lab)
    tp, fp, fn, tn = (len(c[k]) for k in ("tp", "fp", "fn", "tn"))
    print(f"{dec} vs {lab} ({tp + fp + fn + tn} rows)")
    print(f"  tp {tp}  fp {fp}  fn {fn}  tn {tn}   precision {tp}/{tp + fp}   recall {tp}/{tp + fn}")
    for k in ("fp", "fn"):
        for r, d in c[k]:
            print(f"  {k} {r['uid']}  score {d['score']}  years {d['years']}  {d['gates'] or ''}  {d['title']}  | my reason: {r['my_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
