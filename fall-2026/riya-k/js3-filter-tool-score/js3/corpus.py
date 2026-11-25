"""The corpus: the postings my JS2 agent saved in its live day-2 run (2026-11-10 19:45 UTC). Read-only.

FILTER.md §4: expected 2,576 postings from the four real boards. If the count differs, `load` raises instead of
filtering a partial corpus. Hashes in CORPUS.sha256 pin the exact files.
"""

import hashlib
from pathlib import Path

from . import ats

HERE = Path(__file__).resolve().parent.parent
RAW = HERE.parent / "js2-loop-tools-diff" / "runs" / "raw"
TAG = "20261110T194501Z-live-day2"
BOARDS = [("greenhouse", "databricks", 914), ("greenhouse", "anthropic", 677),
          ("ashby", "openai", 830), ("ashby", "notion", 155)]
MISSING = {"ashby:notarealco-js2": "no data (HTTP 404 in JS2, planted)",
           "smartrecruiters:hubspot": "no data (HTTP 200 with 0 postings in JS2: suspect empty)"}
EXPECTED_TOTAL = 2576


class CorpusError(RuntimeError):
    pass


def raw_path(system, board, raw_dir=None):
    return Path(raw_dir or RAW) / f"{system}-{board}-{TAG}-a1.json"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(raw_dir=None, expected_total=EXPECTED_TOTAL):
    postings = []
    for system, board, n in BOARDS:
        p = raw_path(system, board, raw_dir)
        if not p.exists():
            raise CorpusError(f"missing raw file {p}")
        items = ats.SYSTEMS[system][1](p.read_text(), board)
        if len(items) != n:
            raise CorpusError(f"{system}:{board} has {len(items)} postings, FILTER.md §4 expects {n}")
        for it in items:
            it["board"] = f"{system}:{board}"
        postings += items
    if len(postings) != expected_total:
        raise CorpusError(f"corpus has {len(postings)} postings, expected {expected_total}")
    return postings


def by_key(postings):
    return {(p["board"], p["id"]): p for p in postings}
