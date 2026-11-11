"""Independent check of one Job-Search Agent 2 run.

    python3 -m checks.independent_check out/runs/<run_id>

This file deliberately imports nothing from agent/ (in particular not
agent/loop.py or agent/adapters.py). It reads the run's raw response files,
its summary.json, and the state files as they were before the run
(out/runs/<run_id>/state_before/), recomputes each board's posting count
with its own JSON parsing, and prints PASS or FLAG per board.

It flags:
  - a board that previously had postings but now reports 0
    (the known limit in GATE.md section 4: the agent itself accepts this);
  - a Greenhouse response where len(jobs) != meta.total;
  - a failed board whose summary shows a number instead of unknown (null);
  - a succeeded board whose summary count or new count differs from the
    recomputed one, or whose raw file is missing or unreadable.

Exit code: 0 if every board passes, 1 if any board is flagged, 2 if the run
itself cannot be read.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _raw_files(raw_dir, run_id, board):
    """This board's raw files for the run, in (attempt, hop) order."""
    pattern = re.compile(re.escape(f"{run_id}_{board}_a") +
                         r"(\d+)(?:_r(\d+))?\.json")
    found = []
    for path in raw_dir.glob(f"{run_id}_{board}_a*.json"):
        match = pattern.fullmatch(path.name)
        if match:
            found.append((int(match.group(1)), int(match.group(2) or 0),
                          path))
    return [path for _, _, path in sorted(found)]


def _previous_ids(run_dir, board):
    path = run_dir / "state_before" / f"{board}.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(i) for i in data.get("seen_ids", [])}


def check_board(entry, run_dir, raw_dir, run_id):
    """Return a list of flag messages for one board (empty means PASS)."""
    name = entry.get("name")
    status = entry.get("status")
    flags = []
    if status != "ok":
        if _is_number(entry.get("new")):
            flags.append(f"board did not succeed ({status}, "
                         f"{entry.get('reason')}) but summary shows new = "
                         f"{entry.get('new')} instead of unknown")
        if _is_number(entry.get("postings_seen")):
            flags.append(f"board did not succeed but summary shows "
                         f"postings_seen = {entry.get('postings_seen')}")
        return flags

    files = _raw_files(raw_dir, run_id, name)
    if not files:
        return ["board succeeded but no raw file was found"]
    try:
        data = json.loads(files[-1].read_bytes().decode("utf-8"))
        jobs = data["jobs"]
        if not isinstance(jobs, list):
            raise TypeError("jobs is not a list")
    except (ValueError, KeyError, TypeError) as exc:
        return [f"raw file {files[-1].name} is not a jobs list "
                f"({exc.__class__.__name__})"]

    ids = [str(job.get("id")) for job in jobs if isinstance(job, dict)]
    unique = list(dict.fromkeys(ids))
    count = len(unique)

    if entry.get("postings_seen") != count:
        flags.append(f"summary says {entry.get('postings_seen')} postings, "
                     f"raw file has {count} distinct ids")

    if entry.get("ats") == "greenhouse":
        meta = data.get("meta")
        total = meta.get("total") if isinstance(meta, dict) else None
        if not _is_number(total):
            flags.append("Greenhouse response has no meta.total to check "
                         "against")
        elif len(jobs) != total:
            flags.append(f"Greenhouse len(jobs) = {len(jobs)} but "
                         f"meta.total = {total}")

    previous = _previous_ids(run_dir, name)
    if previous and count == 0:
        flags.append(f"board previously had {len(previous)} postings but "
                     f"now reports 0")
    expected_new = 0 if previous is None else \
        len([i for i in unique if i not in previous])
    if entry.get("new") != expected_new:
        flags.append(f"summary says new = {entry.get('new')}, recomputed "
                     f"{expected_new}")
    return flags


def check_run(run_dir, root=ROOT, out=sys.stdout):
    """Print PASS/FLAG per board. Returns the exit code."""
    run_dir = Path(run_dir)
    if not run_dir.is_absolute():
        run_dir = Path(root) / run_dir
    try:
        summary = json.loads((run_dir / "summary.json").read_text(
            encoding="utf-8"))
        run_id = summary["run_id"]
        boards = summary["boards"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"cannot read run at {run_dir}: {exc}", file=out)
        return 2
    raw_dir = Path(root) / "out" / "raw"
    print(f"Independent check of run {run_id} "
          f"[{summary.get('mode', 'unknown mode')}], agent exit "
          f"{summary.get('exit')!r}", file=out)
    flagged = False
    for entry in boards:
        try:
            flags = check_board(entry, run_dir, raw_dir, run_id)
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            flags = [f"could not check: {exc.__class__.__name__}: {exc}"]
        if flags:
            flagged = True
            for flag in flags:
                print(f"FLAG {entry.get('name')}: {flag}", file=out)
        else:
            print(f"PASS {entry.get('name')}", file=out)
    return 1 if flagged else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m checks.independent_check")
    parser.add_argument("run_dir", help="out/runs/<run_id>")
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="project root (default: this checkout)")
    args = parser.parse_args(argv)
    return check_run(args.run_dir, root=args.root)


if __name__ == "__main__":
    sys.exit(main())
