"""Everything one watch run collected, read back from its saved raw responses (never from the network).

A failed board gives no postings and is listed as failed: its postings are never counted as rejected (FILTER.md, 3).
"""
import json
from pathlib import Path

from . import ats, config


def load_run(run_dir, policy):
    """Returns (postings, failed): postings are (board, job) pairs in report order; failed are (board, reason)."""
    run_dir = Path(run_dir)
    report = json.loads(policy.check_read(run_dir / "report.json").read_text(encoding="utf-8"))
    postings, failed = [], []
    for b in report["boards"]:
        if b["result"] != "checked":
            failed.append((b["board"], b.get("reason") or b["result"]))
            continue
        raw = b["attempts"][-1]["raw"]
        body = policy.check_read(config.ROOT / raw).read_bytes()
        postings += [(b["board"], job) for job in ats.parse(b["system"], body)]
    return postings, failed


def latest_run(policy):
    runs = sorted(p for p in config.RUNS_DIR.iterdir() if p.is_dir() and p.name[:8].isdigit() and "WRONG" not in p.name)
    if not runs:
        raise FileNotFoundError("no watch run under runs/: run `python3 -m agent watch` first")
    return policy.check_read(runs[-1])
