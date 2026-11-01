"""Shared loaders for the sampling report and the prompt experiment."""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASELINE_RAW = ROOT / "runs" / "raw" / "stripe-20261101T024132Z.json"
LABELS = ROOT / "experiments" / "prompt" / "labels.csv"


def jobs_by_id(raw=BASELINE_RAW):
    return {j["id"]: j for j in json.loads(pathlib.Path(raw).read_text())["jobs"]}


def maya():
    return json.loads((ROOT / "personas" / "maya-sehgal.resume.json").read_text())


def labels(require=True):
    rows = list(csv.DictReader(LABELS.open()))
    for r in rows:
        r["id"] = int(r["id"])
        r["hand_label"] = r["hand_label"].strip()
    if require:
        bad = [r["id"] for r in rows if r["hand_label"] not in ("relevant", "not_relevant")]
        if bad:
            raise SystemExit(f"hand labels missing or not relevant/not_relevant for ids: {bad}")
    return rows


def append_jsonl(path, obj):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path):
    path = pathlib.Path(path)
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []
