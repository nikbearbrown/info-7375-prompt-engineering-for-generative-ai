"""Independent check of a finished run.

It does not trust the agent's summary. It re-reads the saved raw bytes, re-counts postings with its own
minimal parse (not providers.parse), re-hashes the bytes, and compares against previous runs' raw files.
"""

import gzip
import hashlib
import json
from pathlib import Path

FAILED = {"not-found", "client-error", "transient-failed", "bad-shape", "policy-refused", "budget-cut"}


def _raw_count(root, obs):
    raw = gzip.decompress((Path(root) / obs["raw_file"]).read_bytes())
    try:
        return len(json.loads(raw)["jobs"]), raw
    except (ValueError, KeyError, TypeError):
        return None, raw


def _last_responses(root, trace):
    """board -> (count from raw, raw bytes, observation) for the last saved response per board."""
    out = {}
    for o in trace["observations"]:
        if o.get("event") == "response" and o.get("raw_file"):
            n, raw = _raw_count(root, o)
            out[o["board"]] = (n, raw, o)
    return out


def check_run(root, trace_path, previous=()):
    trace = json.loads(Path(trace_path).read_text())
    findings = []

    def flag(kind, board, detail):
        findings.append({"kind": kind, "board": board, "detail": detail})

    raw = _last_responses(root, trace)
    prev_counts = {}
    for p in previous:
        pt = json.loads(Path(p).read_text())
        for board, (n, _, _) in _last_responses(root, pt).items():
            if n is not None:
                prev_counts[board] = n

    for board, b in trace["boards"].items():
        status, reported = b.get("status"), b.get("postings")
        if status in FAILED and reported is not None:
            flag("value-for-failed-board", board, f"status {status} but the report gives {reported}")
        if board not in raw:
            continue
        n, body, o = raw[board]
        if o.get("sha256") and hashlib.sha256(body).hexdigest() != o["sha256"]:
            flag("raw-hash-mismatch", board, "saved raw bytes do not match the hash in the trace")
        if status == "ok" and n is not None and reported != n:
            flag("count-mismatch", board, f"report says {reported}, raw file has {n}")
        if n == 0 and (trace["exit"] == "finished" or status == "ok"):
            flag("finished-with-empty-board", board, f"exit {trace['exit']}, status {status}, but the raw board has 0 postings")
        if n == 0 and prev_counts.get(board, 0) > 0:
            flag("drop-to-zero", board, f"previous run's raw file had {prev_counts[board]} postings, this one has 0")

    if trace["exit"] == "finished":
        not_ok = [k for k, b in trace["boards"].items() if b.get("status") not in ("ok", "repeat-skipped")]
        if not_ok or trace.get("unvisited"):
            flag("finished-but-not-all-ok", ",".join(not_ok + trace.get("unvisited", [])), "exit says finished")
    return findings
