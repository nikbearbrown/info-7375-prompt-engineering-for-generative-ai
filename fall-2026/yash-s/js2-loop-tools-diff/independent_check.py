#!/usr/bin/env python3
"""Independent check of one agent run (GATE.md section 4, Empty Response).

This script does not import the agent or its parsers, and it does not trust the run's own
report. For every board the run reports as "ok", it recounts the postings straight from the
run's saved raw response. It then compares that count with the same board's most recent
earlier saved response.

It flags:
  DROP-TO-ZERO   the board had postings in an earlier response and now has none
  MISMATCH       the run's reported posting count differs from the recount

usage (from this folder):
  python3 independent_check.py <run folder> [--earlier <runs folder> ...]
exit codes: 0 nothing flagged, 1 something flagged, 2 the run folder cannot be checked
"""
import argparse
import json
import sys
from pathlib import Path


def recount(raw_path):
    """Both Greenhouse and Ashby list postings under "jobs"."""
    return len(json.loads(Path(raw_path).read_bytes())["jobs"])


def last_ok_raw(run_dir, ats, slug):
    found = sorted(Path(run_dir).glob(f"raw-{ats}-{slug}-attempt*-http200.json"))
    return found[-1] if found else None


def earlier_raw(roots, ats, slug, before):
    """The newest saved 200 response for this board in any run folder older than `before`."""
    runs = sorted({d for root in roots for d in Path(root).glob("run-*") if d.is_dir() and d.name < before},
                  key=lambda d: d.name)
    for d in reversed(runs):
        raw = last_ok_raw(d, ats, slug)
        if raw:
            return raw
    return None


def check(run_dir, earlier_roots):
    run_dir = Path(run_dir)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    rows, flagged = [], False
    for b in summary["boards"]:
        if b["status"] != "ok" or b.get("repeat_of"):
            rows.append((b["name"], b["status"], "-", "-", "-", "not checked here (the run did not report it as ok)"))
            continue
        raw = last_ok_raw(run_dir, b["ats"], b["slug"])
        now = recount(raw)
        prev_raw = earlier_raw(earlier_roots + [run_dir.parent], b["ats"], b["slug"], run_dir.name)
        prev = recount(prev_raw) if prev_raw else None
        notes = []
        if now != b["postings"]:
            notes.append(f"MISMATCH: the run reported {b['postings']}, the raw response holds {now}")
        if prev and now == 0:
            notes.append(f"DROP-TO-ZERO: {prev} postings in {prev_raw.parent.name}, none now")
        flagged = flagged or bool(notes)
        rows.append((b["name"], b["status"], now, "-" if prev is None else prev,
                     prev_raw.parent.name if prev_raw else "none", "; ".join(notes) or "consistent"))
    return summary, rows, flagged


def main(argv=None):
    ap = argparse.ArgumentParser(description="Independently recount one run's boards.")
    ap.add_argument("run_dir")
    ap.add_argument("--earlier", action="append", default=[], help="another runs folder to look in for earlier responses")
    a = ap.parse_args(argv)
    try:
        summary, rows, flagged = check(a.run_dir, a.earlier)
    except (OSError, ValueError, KeyError) as e:
        print(f"CANNOT CHECK: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    print(f"Independent check of {Path(a.run_dir).name}: the agent reported '{summary['exit_status']}' ({summary['source']})")
    print(f"{'board':20} {'status':12} {'now':>6} {'before':>7}  earlier run                  result")
    for name, status, now, prev, where, note in rows:
        print(f"{name:20} {status:12} {now!s:>6} {prev!s:>7}  {where:28} {note}")
    print("FLAGGED: the run's own report is not enough." if flagged else "Nothing flagged.")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
