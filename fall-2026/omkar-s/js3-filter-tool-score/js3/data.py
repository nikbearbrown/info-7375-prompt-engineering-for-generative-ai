"""Loading the collected corpus, the persona and the held-out labels (read-only helpers)."""
import csv
import glob
import gzip
import json
import os

from .js2 import ats, persona

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA = os.path.join(BASE, "persona", "aarav-patel.example.json")
HELDOUT_DIR = os.path.join(BASE, "labels", "heldout-js1")


def latest_run():
    runs = sorted(os.path.basename(p)[:-len(".jsonl.gz")] for p in glob.glob(os.path.join(BASE, "data", "corpus", "*.jsonl.gz")))
    if not runs:
        raise SystemExit("no corpus yet: run `python3 -m js3.collect` first")
    return runs[-1]


def load_corpus(run=None):
    run = run or latest_run()
    with gzip.open(os.path.join(BASE, "data", "corpus", run + ".jsonl.gz"), "rt", encoding="utf-8") as f:
        return run, [json.loads(line) for line in f]


def load_sources(run):
    with open(os.path.join(BASE, "data", "runs", run, "sources.json"), encoding="utf-8") as f:
        return json.load(f)


def load_persona():
    return persona.load(PERSONA)


def load_heldout():
    """Omkar's 20 JS1 hand labels (2026-10-27) with their saved Greenhouse postings.

    Returns [(posting, label, note)]. None of these labels was used to set any JS3 number."""
    with open(os.path.join(HELDOUT_DIR, "postings-20.json"), encoding="utf-8") as f:
        raw = json.load(f)
    postings = {p["id"]: p for p in ats.parse("greenhouse", json.dumps({"jobs": raw["jobs"]}).encode())}
    out = []
    with open(os.path.join(HELDOUT_DIR, "labels.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = dict(postings[row["posting_id"]], source="greenhouse:klaviyo", company="Klaviyo")
            p["html"] = p["content"]
            out.append((p, row["omkar_label"], row["omkar_note"]))
    return out
