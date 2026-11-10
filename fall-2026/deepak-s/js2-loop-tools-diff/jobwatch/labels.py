"""labels/labels.csv and labels/split.json, as read by sample and experiment (CONTRACT.md Interfaces)."""
import csv
import json
from pathlib import Path

from jobwatch.errors import REFUSED, Stop

LABELS_CSV = Path("labels") / "labels.csv"
SPLIT_JSON = Path("labels") / "split.json"
HAND_LABELS = ("relevant", "not_relevant")
SETS = {"development": "development", "held-out": "held_out"}


def load_split(required=True):
    """split.json as {seed, development, held_out}; None when absent and not required."""
    if not SPLIT_JSON.exists():
        if required:
            raise Stop(REFUSED, f"{SPLIT_JSON.as_posix()} is missing; make it with labels/make_split.py --seed S")
        return None
    try:
        split = json.loads(SPLIT_JSON.read_bytes())
    except (OSError, ValueError):
        raise Stop(REFUSED, f"{SPLIT_JSON.as_posix()} is not readable JSON") from None
    if not isinstance(split, dict) or not all(
        isinstance(split.get(k), list) and all(isinstance(i, str) for i in split[k]) for k in SETS.values()
    ):
        raise Stop(REFUSED, f"{SPLIT_JSON.as_posix()} must hold lists of id strings under development and held_out")
    return split


def load_hand_labels(posting_ids):
    """{posting_id: hand_label} for these ids; each must have exactly one row labelled relevant or not_relevant."""
    try:
        with open(LABELS_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except OSError:
        raise Stop(REFUSED, f"cannot read {LABELS_CSV.as_posix()}") from None
    found = {}
    for row in rows:
        pid = row.get("posting_id")
        if pid in posting_ids:
            if pid in found:
                raise Stop(REFUSED, f"{LABELS_CSV.as_posix()}: posting {pid} has more than one row")
            found[pid] = row.get("hand_label")
    bad = [p for p in posting_ids if found.get(p) not in HAND_LABELS]
    if bad:
        raise Stop(REFUSED, f"{LABELS_CSV.as_posix()}: no relevant/not_relevant hand_label for {', '.join(bad)}")
    return found
