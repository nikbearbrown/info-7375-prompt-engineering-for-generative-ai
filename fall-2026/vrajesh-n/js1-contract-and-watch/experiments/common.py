"""Shared helpers for the Chapter 1-2 experiments."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from earlybird.resume import load_resume  # noqa: E402

SNAPSHOT = ROOT / "data/raw/2026-10-31/ashby_commure.json"
LABELS = ROOT / "experiments/labels.csv"
RESULTS = ROOT / "experiments/results"
RESUME = load_resume(ROOT / "data/resume/rohan-desai.example.json")


def postings():
    return {p["id"]: p for p in json.loads(SNAPSHOT.read_text(encoding="utf-8"))["jobs"]}


def labels():
    with LABELS.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save(name, data):
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
