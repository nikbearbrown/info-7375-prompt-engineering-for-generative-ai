"""Independent check of one run. It does NOT import the agent and does not trust its counts: it recounts postings from
the saved raw responses and compares every empty board against a roster probed separately (check/verified_boards.json).

    python check/independent_check.py evidence/runs/<run_id>
Exit 0 = nothing contradicts the agent's report; 1 = the report is not supported by the evidence.
"""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def recount(provider: str, raw: Path) -> int | None:
    try:
        d = json.loads(raw.read_bytes().decode("utf-8"))
    except Exception:
        return None
    if provider in ("greenhouse", "ashby"):
        return len(d["jobs"]) if isinstance(d, dict) and isinstance(d.get("jobs"), list) else None
    return len(d["content"]) if isinstance(d, dict) and isinstance(d.get("content"), list) else None


def main(run_dir: str) -> int:
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    rd = (ROOT / run_dir).resolve()
    summary = json.loads((rd / "summary.json").read_text(encoding="utf-8"))
    roster = json.loads((HERE / "verified_boards.json").read_text(encoding="utf-8"))
    known = {(b["provider"], b["slug"]): b["postings"] for b in roster["boards"]}
    problems = []
    print(f"independent check of run {summary['run_id']} (agent reported: {summary['exit']})")
    for b in summary["boards"]:
        key = (b["provider"], b["slug"])
        raws = [ROOT / p for p in b.get("raw_paths", [])]
        counts = [recount(b["provider"], p) for p in raws if p.exists()]
        recounted = sum(c for c in counts if c is not None) if counts and None not in counts else None
        line = f"  {b['provider']:15} {b['slug']:10} agent: {b['status']:9} postings={b['postings']}  recount from raw: {recounted}"
        if b["status"] == "success":
            if recounted is None or recounted != b["postings"]:
                problems.append(f"{b['slug']}: agent says {b['postings']} postings, raw files give {recounted}")
            if b["postings"] == 0:
                if key in known and known[key] > 0:
                    problems.append(f"{b['slug']}: reported empty, but the roster saw {known[key]} postings at {roster['probed_at']}")
                elif key not in known:
                    near = difflib.get_close_matches(b["slug"], [s for p, s in known if p == b["provider"]], n=1)
                    problems.append(f"{b['slug']}: reported as a valid empty board, but nothing independent shows this board "
                                    f"exists" + (f" (closest verified board: {near[0]!r})" if near else ""))
        elif b["postings"] is not None:
            problems.append(f"{b['slug']}: board failed ({b['reason']}) but a count of {b['postings']} was reported")
        print(line)
    failed = [b for b in summary["boards"] if b["status"] != "success"]
    if summary["exit"] == "finished" and failed:
        problems.append(f"exit 'finished' although {len(failed)} board(s) did not succeed")
    if summary["exit"] == "finished" and summary.get("budget_reached"):
        problems.append("exit 'finished' although a budget was reached")
    if problems:
        print("CHECK FAILED: the agent's report is not supported by the evidence:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("CHECK PASSED: nothing in the raw evidence or the roster contradicts the agent's report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
