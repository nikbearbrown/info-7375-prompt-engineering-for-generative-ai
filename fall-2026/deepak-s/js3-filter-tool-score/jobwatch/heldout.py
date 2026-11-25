"""Phase 2e: the held-out draw (FILTER.md section 7). Drawn once; refuses to overwrite.

    python -m jobwatch heldout --dataset data/postings-<run-id>.jsonl --seed-a N --seed-b M

Pool: stratum A = titles with ml, machine, learning, ai, scientist or data; stratum B = titles
with a word of the broad 14-word list but none of A. Whole JS1 tokens of the normalized title.
Each stratum's candidates are sorted by board key then posting id (both compared as strings) and
drawn with random.Random(seed).sample, with its own recorded seed: 30 from A, 10 from B.

Writes labels/heldout.csv (comment lines with the run, the seeds and the stratum sizes, then the
columns below) and one text file per drawn posting under data/texts/<run-id>/. This module does
not import the filter and the sheet has no score, decision or matched-rule column.
"""
import random

from jobwatch import dataset, sheets
from jobwatch.textmatch import tokens

STRATUM_A = ("ml", "machine", "learning", "ai", "scientist", "data")
BROAD = ("engineer", "engineering", "scientist", "science", "data", "machine", "learning", "ml", "ai",
         "software", "research", "researcher", "developer", "analyst")
DRAWS = {"A": 30, "B": 10}
SHEET = "labels/heldout.csv"
COLUMNS = ("posting_key", "stratum", "board", "title", "location", "url", "text_path", "label", "override_reason")


class SealedError(Exception):
    pass


def stratum(title):
    t = set(tokens(title or ""))
    if t & set(STRATUM_A):
        return "A"
    if t & set(BROAD):
        return "B"
    return None


def draw(lines, seeds):
    pools = {"A": [], "B": []}
    for ln in lines:
        s = stratum(ln["title"])
        if s:
            pools[s].append(ln)
    chosen = {}
    for s, pool in pools.items():
        pool.sort(key=lambda ln: (ln["board"], str(ln["posting_id"])))
        chosen[s] = random.Random(seeds[s]).sample(pool, DRAWS[s])
    return pools, chosen


def run(tools, dataset_path, seeds, run_id):
    if sheets.exists(tools, SHEET):
        raise SealedError(f"{SHEET} exists; the held-out set is drawn once and never redrawn")
    lines = dataset.load(tools, dataset_path)
    pools, chosen = draw(lines, seeds)
    picked = [ln for s in ("A", "B") for ln in chosen[s]]
    paths = sheets.write_texts(tools, picked, run_id)
    rows = [{"posting_key": ln["key"], "stratum": s, "board": ln["board"], "title": ln["title"],
             "location": ln["location"] if ln["location"] is not None else "", "url": ln["url"] or "",
             "text_path": paths[ln["key"]], "label": "", "override_reason": ""}
            for s in ("A", "B") for ln in chosen[s]]
    comments = [
        f"Held-out set (FILTER.md section 7), drawn once from {dataset_path} (run {run_id}). Sealed: used only for Phase 6.",
        f"Stratum A (title has {', '.join(STRATUM_A)}): pool {len(pools['A'])}, drawn {DRAWS['A']}, seed {seeds['A']}.",
        f"Stratum B (title has a broad word but none of A): pool {len(pools['B'])}, drawn {DRAWS['B']}, seed {seeds['B']}.",
        "Method: candidates sorted by board key then posting id (strings); random.Random(seed).sample per stratum.",
        "label: relevant or not_relevant (FILTER.md section 0). override_reason: filled only for an OVERRIDE.",
    ]
    sheets.write_sheet(tools, SHEET, comments, COLUMNS, rows)
    return {"A": len(pools["A"]), "B": len(pools["B"])}, rows
