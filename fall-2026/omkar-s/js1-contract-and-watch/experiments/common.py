"""Shared helpers for the two experiments. Postings come from a SAVED raw response
(experiments/prompt/postings-20.json), never a live fetch, so every run sees the same text."""
import csv
import hashlib
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXP = os.path.join(ROOT, "experiments", "prompt")
POSTINGS = os.path.join(EXP, "postings-20.json")
LABELS = os.path.join(EXP, "labels.csv")
RESUME = os.path.join(ROOT, "persona", "aarav-patel.example.json")
SAMPLING_OUT = os.path.join(ROOT, "experiments", "sampling", "verdicts.jsonl")


def load_postings():
    with open(POSTINGS, encoding="utf-8") as f:
        return {str(j["id"]): j for j in json.load(f)["jobs"]}


def load_labels():
    with open(LABELS, encoding="utf-8") as f:
        return {r["posting_id"]: r for r in csv.DictReader(f)}


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def append_jsonl(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]
