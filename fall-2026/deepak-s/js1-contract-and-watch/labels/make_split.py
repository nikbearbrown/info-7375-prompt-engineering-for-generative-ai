"""Split the 20 hand-labelled postings into development and held-out: CONTRACT.md Interfaces.

    python labels/make_split.py --seed S

Reads labels/labels.csv (never modifies it) and writes labels/split.json
{seed, development: [10 ids], held_out: [10 ids]}. Run from the project folder.
Refuses unless there are exactly 20 unique ids, each labelled relevant or not_relevant, and
refuses to replace an existing split.json with a different one.
"""
import argparse
import csv
import json
import random
import sys
from pathlib import Path

LABELS_CSV = Path("labels") / "labels.csv"
SPLIT_JSON = Path("labels") / "split.json"
HAND_LABELS = ("relevant", "not_relevant")
N_IDS = 20
N_DEVELOPMENT = 10


class Refused(Exception):
    """The input is not 20 unique labelled ids, or split.json would change."""


def read_ids():
    try:
        with open(LABELS_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except OSError:
        raise Refused(f"cannot read {LABELS_CSV.as_posix()}") from None
    ids = [row.get("posting_id") for row in rows]
    if len(ids) != N_IDS or len(set(ids)) != N_IDS or not all(ids):
        raise Refused(f"{LABELS_CSV.as_posix()} must hold exactly {N_IDS} unique posting ids; it has "
                      f"{len(rows)} rows and {len(set(i for i in ids if i))} unique ids")
    unlabelled = [row["posting_id"] for row in rows if row.get("hand_label") not in HAND_LABELS]
    if unlabelled:
        raise Refused(f"not labelled relevant or not_relevant: {', '.join(unlabelled)}")
    return ids


def make_split(seed, ids):
    ordered = sorted(ids, key=int)
    development = sorted(random.Random(seed).sample(ordered, N_DEVELOPMENT), key=int)
    held_out = [i for i in ordered if i not in development]
    return {"seed": seed, "development": development, "held_out": held_out}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="labels/make_split.py", description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        split = make_split(args.seed, read_ids())
        data = (json.dumps(split, indent=2) + "\n").encode("utf-8")
        if SPLIT_JSON.exists():
            if SPLIT_JSON.read_bytes() != data:
                raise Refused(f"{SPLIT_JSON.as_posix()} exists with a different split; it is not replaced")
            done = "unchanged"
        else:
            SPLIT_JSON.write_bytes(data)
            done = "wrote"
    except Refused as e:
        print(f"make_split: refused: {e}", file=sys.stderr)
        return 2
    print(f"make_split: seed {args.seed}; {done} {SPLIT_JSON.as_posix()}")
    print("development: " + ", ".join(split["development"]))
    print("held_out:    " + ", ".join(split["held_out"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
