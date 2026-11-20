"""Independent check of a run's report. It does NOT import or reuse the loop:
it parses the raw files itself and compares the report's claims with
(a) what the raw responses actually contain and (b) an earlier real run.

Check a report against an earlier run:
    python3 -m agent.independent_check --previous evidence/run-20261110-025626Z \
        --current out/<run folder>

Recompute "new jobs" between two real runs from their raw files alone:
    python3 -m agent.independent_check --recompute-new \
        evidence/run-20261109-041358Z evidence/run-20261110-025626Z

Exit code 1 if anything is suspicious, else 0.
"""

import argparse
import json
import sys
from pathlib import Path

DROP_RATIO = 0.5   # a board losing more than half its jobs since the last run is suspicious


def raw_ids(run_dir: Path) -> dict[str, list[str]]:
    """Job ids per board, parsed directly from the saved raw responses
    (last successful attempt per board)."""
    out = {}
    for f in sorted((run_dir / "raw").glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("timeout") or not 200 <= rec.get("status", 0) <= 299:
            continue
        try:
            data = json.loads(rec["body"])
        except ValueError:
            continue
        jobs = data.get("jobs") if isinstance(data, dict) else data
        if isinstance(jobs, list):
            out[rec["board"]] = [str(j.get("id")) for j in jobs]
    return out


def check(previous: Path, current: Path) -> int:
    report = json.loads((current / "report.json").read_text(encoding="utf-8"))
    before = {b: len(ids) for b, ids in raw_ids(previous).items()}
    now = {b: len(ids) for b, ids in raw_ids(current).items()}
    problems = []
    print(f"report: {current}  (agent says: {report['exit']})")
    print(f"compared with earlier real run: {previous}\n")
    print(f"  {'board':<20}{'agent says':<20}{'raw has':<10}{'earlier run':<13}verdict")
    for r in report["boards"]:
        b = r["board"]
        claim = f"{r['status']}" + (f", {r['jobs']} jobs" if "jobs" in r else "")
        raw_n, prev_n = now.get(b), before.get(b)
        verdict = "ok"
        if "jobs" in r and raw_n is not None and r["jobs"] != raw_n:
            verdict = f"MISMATCH: report {r['jobs']} vs raw {raw_n}"
        elif raw_n is not None and prev_n:
            if raw_n == 0:
                verdict = f"SUSPICIOUS: dropped from {prev_n} to 0"
            elif raw_n < prev_n * DROP_RATIO:
                verdict = f"SUSPICIOUS: dropped from {prev_n} to {raw_n}"
        if verdict != "ok":
            problems.append(f"{b}: {verdict}")
        print(f"  {b:<20}{claim:<20}{str(raw_n if raw_n is not None else '-'):<10}"
              f"{str(prev_n if prev_n is not None else '-'):<13}{verdict}")
    print()
    if problems and report["exit"] == "finished":
        print("FINISHED WRONG ANSWER: the agent reported 'finished', but:")
    elif problems:
        print("Problems found:")
    for p in problems:
        print(f"  - {p}")
    if not problems:
        print("No problems found by this check.")
    return 1 if problems else 0


def recompute_new(day1: Path, day2: Path) -> int:
    a, b = raw_ids(day1), raw_ids(day2)
    print(f"day 1: {day1}\nday 2: {day2}\n")
    print(f"  {'board':<20}{'day 1':<8}{'day 2':<8}{'new':<6}removed")
    for board in sorted(set(a) | set(b)):
        x, y = set(a.get(board, [])), set(b.get(board, []))
        print(f"  {board:<20}{len(x):<8}{len(y):<8}{len(y - x):<6}{len(x - y)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m agent.independent_check")
    ap.add_argument("--previous")
    ap.add_argument("--current")
    ap.add_argument("--recompute-new", nargs=2, metavar=("DAY1", "DAY2"))
    args = ap.parse_args(argv)
    if args.recompute_new:
        return recompute_new(Path(args.recompute_new[0]), Path(args.recompute_new[1]))
    if not (args.previous and args.current):
        ap.error("give --previous and --current, or --recompute-new DAY1 DAY2")
    return check(Path(args.previous), Path(args.current))


if __name__ == "__main__":
    sys.exit(main())
