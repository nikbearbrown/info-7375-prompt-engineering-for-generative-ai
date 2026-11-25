"""Independent check of one run (GATE.md wrong version 1: "check the saved body and
before-and-after state separately from the loop's report"), extended for JS4's count check
(PLAN.md v0.2: "Compare the independently counted raw keys with the trace and displayed summary").

This script imports only the standard library, never jobwatch. It recounts jobs and keys
from the saved raw bodies with its own minimal reading of the two board formats, rechecks
each body's sha256 against the trace, and flags every count that disagrees with its
recount: the count in trace.json, in results.json, and in the results.md and trace.md
tables. Given two state files, it also compares the state saved before the run with the
one after it, and flags every claim in results.json that they contradict. Without them
(count-only mode) it skips every state check and says so. It checks consistency with the
saved evidence; it cannot tell whether a board's real contents were complete.

Usage (from the JS4 folder):
  python3 -I checks/independent_check.py runs/RUN_ID
  python3 -I checks/independent_check.py runs/RUN_ID --state-before FILE|none --state-after FILE|none

Take the "before" copy yourself before the run (cp state/state.json somewhere outside
runs/), so the check does not rely on anything the agent wrote about its own state.
Exit 0: no contradiction found (PASS). Exit 1: at least one (FAIL). Exit 2: a usage error."""

import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

DISPLAYS = ("results.md", "trace.md")


def keys_in_body(board, body):
    """Posting keys in a saved body, or None if it is not a JSON object with a jobs list.
    Greenhouse keys are the ids as decimal strings; Ashby keys are the jobUrl strings."""
    try:
        data = json.loads(body)
    except ValueError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        return None
    system = board.split("/", 1)[0]
    keys = []
    for job in data["jobs"]:
        if not isinstance(job, dict):
            return None
        if system == "greenhouse":
            key = str(job["id"]) if type(job.get("id")) is int else None
        else:
            key = job.get("jobUrl") if isinstance(job.get("jobUrl"), str) else None
        if key is None:
            return None
        if key not in keys:
            keys.append(key)
    return keys


def displayed_counts(path):
    """(board, jobs) for each row of each Markdown table that has a Board and a Jobs column
    and a whole number in its Jobs cell. A '—' or empty Jobs cell is not a count."""
    found, header = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            header = None
            continue
        cells = [cell.strip().strip("`") for cell in line[1:-1].split("|")]
        if header is None:
            header = cells
            continue
        if all(cell and set(cell) <= set("-:") for cell in cells):
            continue
        if "Board" in header and "Jobs" in header and len(cells) == len(header):
            jobs = cells[header.index("Jobs")]
            if re.fullmatch(r"\d+", jobs):
                found.append((cells[header.index("Board")], int(jobs)))
    return found


def read_state(path):
    if path == "none":
        return None, None
    raw = Path(path).read_bytes()
    return raw, json.loads(raw)


def seen_keys(state_data, board):
    if state_data is None or board not in state_data.get("boards", {}):
        return None
    return list(state_data["boards"][board].get("seen", {}))


def check(run_dir, before_path=None, after_path=None):
    """(notes, flags) for one run folder. With neither state file given (count-only mode),
    the state checks are skipped and a note says so."""
    count_only = before_path is None and after_path is None
    notes, flags = [], []
    trace = json.loads((run_dir / "trace.json").read_text(encoding="utf-8"))
    results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    status = results.get("status")
    notes.append(f"report: status {status}, state_advanced {results.get('state_advanced')}")

    saved = {}
    for event in trace.get("events", []):
        if event.get("event") != "request":
            continue
        board = event.get("board")
        if not event.get("raw"):
            saved[board] = {"http": event.get("status"), "keys": None}
            notes.append(f"{board}: no response saved ({event.get('reason')})")
            continue
        path = run_dir / event["raw"]
        if not path.exists():
            flags.append(f"{board}: the raw file {event['raw']} named in the trace is missing")
            continue
        body = gzip.decompress(path.read_bytes())
        if hashlib.sha256(body).hexdigest() != event.get("sha256"):
            flags.append(f"{board}: {event['raw']} does not match the sha256 recorded in the trace")
        keys = keys_in_body(board, body) if event.get("status") == 200 else None
        saved[board] = {"http": event.get("status"), "keys": keys}
        count = "no jobs list" if keys is None else f"{len(keys)} jobs"
        notes.append(f"{board}: saved body is HTTP {event.get('status')}, {len(body)} bytes, {count}")
        recorded = event.get("jobs")
        if recorded is not None and keys is None:
            flags.append(f"{board}: trace.json records {recorded} jobs, but its saved response has no jobs list")
        elif recorded is not None and recorded != len(keys):
            flags.append(f"{board}: trace.json records {recorded} jobs; its saved response has {len(keys)}")

    before_raw, before = (None, None) if count_only else read_state(before_path)
    after_raw, after = (None, None) if count_only else read_state(after_path)
    usable = [row for row in results.get("boards", []) if row.get("outcome") == "usable"]

    for row in usable:
        board = row["board"]
        info = saved.get(board)
        if info is None:
            flags.append(f"{board}: reported usable, but the trace has no saved response for it")
            continue
        keys = info["keys"]
        if info["http"] != 200 or keys is None:
            flags.append(f"{board}: reported usable, but its saved response is HTTP {info['http']} with no jobs list")
            continue
        if not keys:
            flags.append(f"{board}: reported usable, but its saved response has 0 jobs; an empty board "
                         "cannot be told apart from a board that could not be checked")
        if row.get("jobs") != len(keys):
            flags.append(f"{board}: results.json reports {row.get('jobs')} jobs; its saved response has {len(keys)}")
        if count_only:
            continue
        earlier = seen_keys(before, board)
        if earlier is None:
            if row.get("baseline") is not True or row.get("new_keys"):
                flags.append(f"{board}: no saved history before this run, so this snapshot is a baseline with no new "
                             f"postings, but the report says baseline={row.get('baseline')}, new={row.get('new_keys')}")
        else:
            expected = [k for k in keys if k not in set(earlier)]
            if row.get("new_keys") != expected:
                flags.append(f"{board}: reported new postings {row.get('new_keys')}; recomputed from the saved body "
                             f"and the earlier state: {expected}")

    for name in DISPLAYS:
        if not (run_dir / name).exists():
            continue
        for board, shown in displayed_counts(run_dir / name):
            keys = (saved.get(board) or {}).get("keys")
            if keys is None:
                flags.append(f"{board}: {name} shows {shown} jobs, but no saved response with a jobs list backs it")
            elif shown != len(keys):
                flags.append(f"{board}: {name} shows {shown} jobs; its saved response has {len(keys)}")

    if status == "finished":
        for row in results.get("boards", []):
            if row.get("role", "normal") == "normal" and row.get("outcome") != "usable":
                flags.append(f"the run reported finished, but {row['board']} is {row.get('outcome')}")

    if count_only:
        notes.append("state not checked (count-only mode: no --state-before or --state-after given)")
        return notes, flags

    changed = before_raw != after_raw
    notes.append(f"state file {'changed' if changed else 'unchanged'} between the two copies")
    if changed and status != "finished":
        flags.append(f"the state changed, but the run did not finish (status {status})")
    if status == "finished" and results.get("state_advanced") and not changed:
        flags.append("the report says finished and state advanced, but the state file is unchanged")
    if after is not None:
        for name, entry in after.get("boards", {}).items():
            if not entry.get("seen"):
                flags.append(f"{name}: saved in the state with an empty history (a baseline of 0 jobs)")
        if changed and status == "finished":
            for row in usable:
                keys = (saved.get(row["board"]) or {}).get("keys") or []
                expected = set(seen_keys(before, row["board"]) or []) | set(keys)
                got = set(seen_keys(after, row["board"]) or [])
                if got != expected:
                    flags.append(f"{row['board']}: the state after the run holds {len(got)} keys; the earlier state "
                                 f"plus the saved body give {len(expected)}")
    return notes, flags


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir")
    parser.add_argument("--state-before", help="a copy of state/state.json taken before the run, or none")
    parser.add_argument("--state-after", help="state/state.json after the run, or none")
    args = parser.parse_args(argv)
    if (args.state_before is None) != (args.state_after is None):
        parser.error("give both --state-before and --state-after, or neither (count-only mode)")
    notes, flags = check(Path(args.run_dir), args.state_before, args.state_after)
    compared = ("the trace, the report, its displays and the saved bodies (state not checked)"
                if args.state_before is None else "the report, the saved bodies and the state files")
    for note in notes:
        print(f"  {note}")
    for flag in flags:
        print(f"FLAG {flag}")
    if flags:
        print(f"FAIL: {len(flags)} contradiction(s) between {compared}")
        return 1
    print(f"PASS: no contradiction found between {compared}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
