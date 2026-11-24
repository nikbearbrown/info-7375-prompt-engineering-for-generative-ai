"""Score every posting in one saved run with FILTER.md v1.0. No network.

    python -m agent.run_filter --run out/runs/<run folder>

Reads <run>/summary.json to find boards that succeeded and their raw files, parses each
with agent/adapters.py, scores with agent/filter.py, and writes (through policy.check_write)
    out/filter/<run folder>/decisions.jsonl
    out/filter/<run folder>/summary.json
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from agent import adapters
from agent.filter import FILTER_VERSION, score_posting
from agent.policy import PolicyError, check_read, make_dir, write_atomic

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ("KEEP", "REJECT", "CANNOT TELL")


def _read_json(path, root):
    with open(check_read(path, root), encoding="utf-8") as f:
        return json.load(f)


def filter_run(run_dir, root=PROJECT_ROOT):
    run_dir = Path(run_dir)
    if not run_dir.is_absolute():
        run_dir = Path(root) / run_dir
    run_summary = _read_json(run_dir / "summary.json", root)

    lines, per_board, skipped = [], {}, {}
    for board, info in run_summary.get("boards", {}).items():
        if info.get("status") != "ok" or not info.get("raw_file"):
            skipped[board] = f"board status {info.get('status')!r} ({info.get('reason')})"
            continue
        system = board.split(":", 1)[0]
        try:
            postings = adapters.parse(system, _read_json(run_dir / info["raw_file"], root))
        except (adapters.BadResponse, ValueError, OSError) as e:
            skipped[board] = f"could not parse raw file: {type(e).__name__}: {e}"
            continue
        counts = Counter()
        for p in postings:
            r = score_posting(p)
            flags = list(r["flags"])
            if not adapters._usable_posting_id(p.get("id")):
                flags.append("data-quality: missing posting id")
            counts[r["decision"]] += 1
            lines.append(json.dumps({
                "board": board, "id": p.get("id"), "title": p.get("title"),
                "location": p.get("location"), "decision": r["decision"], "score": r["score"],
                "categories": r["categories"], "flags": flags, "reasons": r["reasons"],
            }, ensure_ascii=False))
        per_board[board] = {d: counts[d] for d in DECISIONS} | {"total": len(postings)}

    totals = Counter()
    for c in per_board.values():
        totals.update({d: c[d] for d in DECISIONS})
    summary = {
        "filter_version": FILTER_VERSION,
        "run": run_dir.name,
        "postings_scored": len(lines),
        "decisions": {d: totals[d] for d in DECISIONS},
        "per_board": per_board,
        "boards_skipped": skipped,
    }

    out = make_dir(Path(root) / "out" / "filter" / run_dir.name, root)
    write_atomic(out / "decisions.jsonl", "".join(l + "\n" for l in lines), root)
    write_atomic(out / "summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n", root)
    summary["output_dir"] = str(out)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, help="out/runs/<run folder>")
    args = ap.parse_args(argv)
    try:
        summary = filter_run(args.run)
    except (PolicyError, OSError, json.JSONDecodeError) as e:
        print(json.dumps({"status": "error", "reason": f"{type(e).__name__}: {e}"}, indent=2))
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
