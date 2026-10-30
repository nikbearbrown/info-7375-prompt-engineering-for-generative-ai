"""Scoring for the sampling report and the prompt experiment.

A call passes only when its reply passed the validator AND its verdict equals the hand
label. A rejected reply is counted as rejected; it is never read as not_relevant."""

import csv

from jobwatch.errors import InputError

LABELS = ("relevant", "not_relevant")


def load_hand_labels(path, ids):
    """Hand labels for exactly these ids. A missing or unknown label stops the run, so no
    Claude call is ever scored against a label written after seeing Claude's answer."""
    with open(path, newline="", encoding="utf-8") as handle:
        rows = {int(row["posting_id"]): row["label"].strip() for row in csv.DictReader(handle)}
    labels = {}
    for posting_id in ids:
        label = rows.get(posting_id, "")
        if label not in LABELS:
            raise InputError(f"posting {posting_id} has no usable hand label in {path} (found {label!r}); label it first")
        labels[posting_id] = label
    return labels


def score(calls, hand_labels, rule_verdicts):
    per_posting = {}
    for c in calls:
        entry = per_posting.setdefault(c["posting_id"], {
            "hand_label": hand_labels.get(c["posting_id"]),
            "rule_verdict": rule_verdicts.get(c["posting_id"]),
            "verdicts": {"relevant": 0, "not_relevant": 0, "rejected": 0},
            "calls": 0,
            "passed": 0,
        })
        entry["calls"] += 1
        entry["verdicts"][c["verdict"] if c["valid"] else "rejected"] += 1
        if c["valid"] and c["verdict"] == entry["hand_label"]:
            entry["passed"] += 1
    for entry in per_posting.values():
        entry["unanimous"] = sum(1 for n in entry["verdicts"].values() if n) == 1
    return {
        "calls": len(calls),
        "valid": sum(1 for c in calls if c["valid"]),
        "passed": sum(e["passed"] for e in per_posting.values()),
        "agrees_with_rule": sum(1 for c in calls if c["valid"] and c["verdict"] == rule_verdicts.get(c["posting_id"])),
        "postings": len(per_posting),
        "postings_all_calls_passed": sum(1 for e in per_posting.values() if e["passed"] == e["calls"]),
        "per_posting": per_posting,
    }
