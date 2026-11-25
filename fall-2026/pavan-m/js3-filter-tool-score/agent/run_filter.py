"""Score every posting in one saved run with FILTER.md v1.0. No network.

    python -m agent.run_filter --run out/runs/<run folder> [--filter-config config/<name>.json]

Reads <run>/summary.json to find boards that succeeded and their raw files, parses each
with agent/adapters.py, scores with agent/filter.py, and writes (through policy.check_write)
    out/filter/<run folder>/decisions.jsonl                  (no --filter-config: plain v1.0)
    out/filter/<run folder>/summary.json
or, with --filter-config config/<stem>.json (v1.0 with that file's overrides),
    out/filter/<run folder>/<stem>/decisions.jsonl
    out/filter/<run folder>/<stem>/summary.json
so the plain v1.0 output is never overwritten.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from agent import adapters
from agent.filter import FILTER_VERSION, resolve_config, score_posting
from agent.policy import PolicyError, check_read, make_dir, write_atomic

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ("KEEP", "REJECT", "CANNOT TELL")


def _read_json(path, root):
    with open(check_read(path, root), encoding="utf-8") as f:
        return json.load(f)


def _resolve(path, root):
    path = Path(path)
    return path if path.is_absolute() else Path(root) / path


def load_filter_config(path, root=PROJECT_ROOT):
    """Read a config file (a JSON object of overrides). Returns (file stem, overrides dict).

    Raises ValueError for a non-object or an unknown key, before anything is scored."""
    path = _resolve(path, root)
    overrides = _read_json(path, root)
    if not isinstance(overrides, dict):
        raise ValueError(f"{path.name}: filter config must be a JSON object")
    resolve_config(overrides)  # validate now
    return path.stem, overrides


def score_run(run_dir, root=PROJECT_ROOT, config=None):
    """Parse every ok board of a saved run and score each posting.

    Returns (records, per_board, skipped); each record is (board, posting, result).
    agent/measure_filter.py uses this too, so both score the same adapter text."""
    run_dir = _resolve(run_dir, root)
    run_summary = _read_json(run_dir / "summary.json", root)

    records, per_board, skipped = [], {}, {}
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
            r = score_posting(p, config)
            counts[r["decision"]] += 1
            records.append((board, p, r))
        per_board[board] = {d: counts[d] for d in DECISIONS} | {"total": len(postings)}
    return records, per_board, skipped


def filter_run(run_dir, root=PROJECT_ROOT, config_path=None):
    run_dir = _resolve(run_dir, root)
    stem, overrides = (None, None)
    if config_path is not None:
        stem, overrides = load_filter_config(config_path, root)

    records, per_board, skipped = score_run(run_dir, root, overrides)
    lines = []
    for board, p, r in records:
        flags = list(r["flags"])
        if not adapters._usable_posting_id(p.get("id")):
            flags.append("data-quality: missing posting id")
        line = {
            "board": board, "id": p.get("id"), "title": p.get("title"),
            "location": p.get("location"), "decision": r["decision"], "score": r["score"],
            "categories": r["categories"], "flags": flags, "reasons": r["reasons"],
        }
        if config_path is not None:
            line["config"] = r["config"]
        lines.append(json.dumps(line, ensure_ascii=False))

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
    out_dir = Path(root) / "out" / "filter" / run_dir.name
    if config_path is not None:
        summary["filter_config"] = {
            "file": str(Path(config_path)), "name": stem,
            "overrides": overrides, "values": resolve_config(overrides),
        }
        out_dir = out_dir / stem

    out = make_dir(out_dir, root)
    write_atomic(out / "decisions.jsonl", "".join(l + "\n" for l in lines), root)
    write_atomic(out / "summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n", root)
    summary["output_dir"] = str(out)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, help="out/runs/<run folder>")
    ap.add_argument("--filter-config", metavar="PATH", default=None,
                    help="JSON object of overrides to FILTER.md v1.0, e.g. config/filter_c1_years5.json")
    args = ap.parse_args(argv)
    try:
        summary = filter_run(args.run, config_path=args.filter_config)
    except (PolicyError, OSError, ValueError) as e:  # json.JSONDecodeError is a ValueError
        print(json.dumps({"status": "error", "reason": f"{type(e).__name__}: {e}"}, indent=2))
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
