"""Raw evidence, seen-id state, and new-since-last-run (CONTRACT §9)."""

import gzip
import hashlib
import json
from pathlib import Path


def parse_jobs(raw):
    data = json.loads(raw)
    jobs = data["jobs"]
    ids = [str(job["id"]) for job in jobs]
    if len(ids) != len(set(ids)):
        raise ValueError("response contains duplicate posting ids")
    return jobs


def save_raw(raw, evidence_dir, stamp, label):
    """Store the response bytes unchanged (gzip-compressed) and return its record."""
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{stamp}-{label}.json.gz"
    n = 2
    while path.exists():  # never overwrite earlier evidence
        path = evidence_dir / f"{stamp}-{label}-{n}.json.gz"
        n += 1
    path.write_bytes(gzip.compress(raw, mtime=0))
    return {"file": path.name, "sha256_of_raw": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def load_raw(path):
    path = Path(path)
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as fh:
            return fh.read()
    return path.read_bytes()


def load_state(path):
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def new_postings(state, jobs):
    """Baseline (no state) reports nothing; later runs report only unseen ids, in board order."""
    if state is None:
        return []
    seen = set(state["seen_ids"])
    return [job for job in jobs if str(job["id"]) not in seen]


def next_state(state, jobs, run_record):
    seen = set(state["seen_ids"]) if state else set()
    seen.update(str(job["id"]) for job in jobs)
    runs = (state["runs"] if state else []) + [run_record]
    return {"board": run_record["board"], "seen_ids": sorted(seen, key=int), "runs": runs}


def save_state(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=1) + "\n")
