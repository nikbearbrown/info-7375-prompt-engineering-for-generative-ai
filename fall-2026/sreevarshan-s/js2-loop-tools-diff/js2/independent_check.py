"""Independent check of a saved run (GATE.md section 8).

check_trace re-reads the saved trace and the raw evidence files and compares
them with what the trace claims. It deliberately does not import js2.loop, so
a parsing bug in the loop cannot hide itself here.

Discrepancy types:
  finished_with_empty_or_missing_raw  trace status is finished but a board's
                                      raw file is missing, empty, or has no postings
  finished_with_failed_board          trace status is finished but a board did not succeed
  zero_postings_recorded_success      raw file has zero postings, board recorded ok
  raw_absent_claimed_success          no raw file found, board recorded ok
  invalid_raw_recorded_success        raw file is not JSON or not a postings list, board recorded ok
  posting_ids_mismatch                raw posting IDs differ from the IDs in the trace
"""

import json
import os


def _raw_postings(ats, body):
    """Return the postings list from raw bytes, or None if the structure is wrong."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    if ats == "greenhouse":
        jobs = data.get("jobs") if isinstance(data, dict) else None
        return jobs if isinstance(jobs, list) else None
    if ats == "lever":
        return data if isinstance(data, list) else None
    return None


def check_trace(trace_path, raw_dir):
    """Return a list of {"board", "type", "detail"} discrepancies; empty means the trace holds up.

    Raw files are looked up by file name inside raw_dir, not at the path the
    trace recorded, so the check depends only on what is actually on disk.
    """
    with open(trace_path, encoding="utf-8") as f:
        trace = json.load(f)
    finished = trace.get("status") == "finished"
    problems = []

    def flag(board, kind, detail):
        problems.append({"board": board, "type": kind, "detail": detail})

    for b in trace.get("boards", []):
        name = b.get("board")
        if b.get("outcome") != "ok":
            if finished:
                flag(name, "finished_with_failed_board", "outcome %r in a finished run" % b.get("outcome"))
            continue

        raw_name = os.path.basename(b["raw_path"]) if b.get("raw_path") else None
        raw_file = os.path.join(raw_dir, raw_name) if raw_name else None
        if raw_file is None or not os.path.isfile(raw_file):
            flag(name, "raw_absent_claimed_success", "no raw file %s in %s" % (raw_name, raw_dir))
            if finished:
                flag(name, "finished_with_empty_or_missing_raw", "raw file missing")
            continue

        with open(raw_file, "rb") as f:
            body = f.read()
        postings = _raw_postings(b.get("ats"), body) if body.strip() else None
        if postings is None:
            what = "raw file is empty" if not body.strip() else "raw file is not a valid %s response" % b.get("ats")
            flag(name, "invalid_raw_recorded_success", what)
            if finished:
                flag(name, "finished_with_empty_or_missing_raw", what)
            continue
        if not postings:
            flag(name, "zero_postings_recorded_success", "raw file has 0 postings")
            if finished:
                flag(name, "finished_with_empty_or_missing_raw", "raw file has 0 postings")
            continue

        raw_ids = [str(p.get("id")) for p in postings if isinstance(p, dict)]
        if raw_ids != [str(i) for i in b.get("posting_ids", [])]:
            flag(name, "posting_ids_mismatch", "raw has %d id(s), trace has %d"
                 % (len(raw_ids), len(b.get("posting_ids", []))))
    return problems
