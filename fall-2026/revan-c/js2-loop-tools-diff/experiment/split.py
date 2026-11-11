"""Stratified dev / held-out split of the hand-labeled postings, with a fixed seed.

Run once, after every label is filled in. It refuses to overwrite an existing split,
so the split cannot be re-rolled until it looks convenient.

Usage: .venv/bin/python -m experiment.split --seed 7375
"""
import argparse
import random

from .common import SPLIT, ExperimentError, load_labels, now_utc, write_json


def stratified_split(labels, seed, dev_size=10):
    """labels: {posting_id: 'relevant'|'not_relevant'} -> {'dev': [...], 'heldout': [...]}"""
    n = len(labels)
    if not 0 < dev_size < n:
        raise ExperimentError(f"dev_size {dev_size} must be between 1 and {n - 1}")
    rng = random.Random(seed)
    groups = {}
    for verdict in ("relevant", "not_relevant"):
        ids = sorted(pid for pid, lab in labels.items() if lab == verdict)
        rng.shuffle(ids)
        groups[verdict] = ids
    rel = groups["relevant"]
    dev_rel = min(len(rel), max(0, round(len(rel) * dev_size / n)))
    if len(rel) >= 2:
        dev_rel = min(max(dev_rel, 1), len(rel) - 1)  # both sets see at least one relevant posting
    dev_not = dev_size - dev_rel
    if dev_not > len(groups["not_relevant"]):
        raise ExperimentError("not enough not_relevant labels to fill the dev set")
    dev = sorted(rel[:dev_rel] + groups["not_relevant"][:dev_not])
    heldout = sorted(rel[dev_rel:] + groups["not_relevant"][dev_not:])
    return {"dev": dev, "heldout": heldout}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--dev-size", type=int, default=10)
    args = parser.parse_args(argv)
    if SPLIT.exists():
        raise SystemExit(f"{SPLIT} already exists; refusing to re-split")
    try:
        rows = load_labels()
        labels = {pid: r["label"].strip() for pid, r in rows.items()}
        split = stratified_split(labels, args.seed, args.dev_size)
    except ExperimentError as exc:
        raise SystemExit(str(exc))
    counts = {name: {v: sum(labels[i] == v for i in ids) for v in ("relevant", "not_relevant")}
              for name, ids in split.items()}
    write_json(SPLIT, {"seed": args.seed, "created_at": now_utc().isoformat(timespec="seconds"),
                       "label_counts": counts, **split})
    print(f"wrote {SPLIT}: dev {counts['dev']}, heldout {counts['heldout']}")


if __name__ == "__main__":
    main()
