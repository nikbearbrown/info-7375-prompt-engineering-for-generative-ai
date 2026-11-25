"""Measure a filter version against my reviewed labels.

    python3 measure.py               v1.0 on tuning and held-out labels, by corpus part and together

Labels come from state/labels/labels.csv (v1.0 sample) and labels_v1_1.csv (v1.1 supplement); the split
from split.json and split_v1_1.json. A label counts only if its `reviewed` column is filled in.

The metric (FILTER.md "How the filter will be measured") is precision and recall of "keep", always with the
counts behind them. A ratio with a zero denominator is reported as "undefined", never as 0 or 1.
"""
import csv
import json
import sys

import corpus
import filter as F
from policy import Policy
from tools import Tools

LABELS = (("state/labels/labels.csv", "state/labels/split.json"),
          ("state/labels/labels_v1_1.csv", "state/labels/split_v1_1.json"))


def load_labels(tools):
    out = {}
    for labels, split in LABELS:
        sides = json.loads(tools.read_text(split))["split"]
        for row in csv.DictReader(tools.read_text(labels).splitlines()):
            if not row.get("reviewed"):
                raise SystemExit(f"{labels} row {row['n']} is not reviewed")
            out[row["key"]] = {"label": row["label"], "side": sides[row["key"]], "title": row["title"]}
    return out


def counts(pairs):
    """pairs: (kept?, label is yes?). Returns tp, fp, fn, tn."""
    tp = sum(k and y for k, y in pairs)
    fp = sum(k and not y for k, y in pairs)
    fn = sum(not k and y for k, y in pairs)
    return tp, fp, fn, len(pairs) - tp - fp - fn


def ratio(a, b):
    return f"{a}/{b} = {a / b:.2f}" if b else f"{a}/{b} (undefined)"


def report(name, pairs):
    tp, fp, fn, tn = counts(pairs)
    return {"set": name, "n": len(pairs), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": ratio(tp, tp + fp), "recall": ratio(tp, tp + fn)}


def measure(evaluate, postings, labels):
    by_key = {p["key"]: p for p in postings}
    rows = []
    for key, lab in labels.items():
        p = by_key[key]
        rows.append((lab["side"], p["corpus"], evaluate(p)["verdict"] == "keep", lab["label"] == "yes", key))
    out = []
    for side in ("tuning", "held-out"):
        for part in ("v1.0", "v1.1 supplement", None):
            pairs = [(k, y) for s, c, k, y, _ in rows if s == side and (part is None or c == part)]
            out.append(report(f"{side} / {part or 'both'}", pairs))
    errors = [(s, key, labels[key]["title"], "false keep" if k else "missed")
              for s, c, k, y, key in rows if k != y]
    return out, errors


def main(argv):
    tools = Tools(Policy())
    _, postings = corpus.load(tools)
    labels = load_labels(tools)
    results, errors = measure(F.evaluate, postings, labels)
    print(f"filter v{F.VERSION}, threshold {F.THRESHOLD}, {len(labels)} reviewed labels")
    print(f"{'set':32} {'n':>3} {'tp':>3} {'fp':>3} {'fn':>3} {'tn':>3}  precision        recall")
    for r in results:
        print(f"{r['set']:32} {r['n']:>3} {r['tp']:>3} {r['fp']:>3} {r['fn']:>3} {r['tn']:>3}  "
              f"{r['precision']:16} {r['recall']}")
    print("\nerrors:")
    for side, key, title, kind in sorted(errors):
        print(f"  {side:8} {kind:10} {key}  {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
