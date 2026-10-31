"""Run the watch: python -m agent.main [--board BOARD] [--resume PATH]."""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from agent import fetch, rule, watch
from agent.resume import load_resume

PROJECT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT / "config.json"
RAW_DIR = PROJECT / "raw"
STATE_PATH = PROJECT / "state" / "seen_ids.json"
RESULTS_DIR = PROJECT / "results"
BOARD_NAME = re.compile(r"^[A-Za-z0-9_-]+$")


def parse_args(argv):
    config = json.loads(CONFIG_PATH.read_text())
    parser = argparse.ArgumentParser(prog="python -m agent.main")
    parser.add_argument("--board", default=config["board"], help="Greenhouse board name")
    parser.add_argument("--resume", default=str(PROJECT / config["resume"]), help="persona résumé JSON")
    return parser.parse_args(argv)


def load_seen(board):
    """Seen ids for this board, or None when this is the board's baseline run."""
    if not STATE_PATH.exists():
        return None
    return json.loads(STATE_PATH.read_text()).get(board)


def save_seen(board, ids):
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    state[board] = ids
    STATE_PATH.parent.mkdir(exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def result_for(posting, resume):
    return {
        "posting_id": posting["id"],
        "title": posting.get("title"),
        "location": (posting.get("location") or {}).get("name"),
        "url": posting.get("absolute_url"),
        "flags": rule.auth_flags(posting),
        "record": rule.judge(posting, resume),
    }


def print_result(r):
    rec, flags = r["record"], r["flags"]
    print(f"[{rec['verdict']}] {r['title']} — {r['location']} (id {r['posting_id']})")
    print(f"  {r['url']}")
    print(f"  record: {rec['reason']}")
    print(f"  fields: posting {rec['posting_fields']} / résumé {rec['resume_fields']}")
    print("  flags:  " + ", ".join(f"{k}={v}" for k, v in flags.items()))


def save_raw(board, raw, now):
    """Write the response bytes untouched; never overwrite an earlier run's file."""
    RAW_DIR.mkdir(exist_ok=True)
    stem = f"{board}_{now:%Y%m%dT%H%M%S}"
    path, n = RAW_DIR / f"{stem}.json", 2
    while path.exists():
        path, n = RAW_DIR / f"{stem}_{n}.json", n + 1
    path.write_bytes(raw)
    return path


def save_results(run, now):
    """Append this run to results/<date>.json so same-day runs are kept."""
    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"{now:%Y-%m-%d}.json"
    runs = json.loads(path.read_text()) if path.exists() else []
    runs.append(run)
    path.write_text(json.dumps(runs, indent=2, ensure_ascii=False) + "\n")
    return path


def main(argv=None):
    args = parse_args(argv)
    if not BOARD_NAME.match(args.board):
        sys.exit(f"refusing board name {args.board!r}: letters, digits, '-' and '_' only")
    try:
        resume = load_resume(args.resume)
    except ValueError as e:
        sys.exit(str(e))

    now = datetime.now().astimezone()
    try:
        raw = fetch.fetch_board(fetch.board_url(args.board))
    except ValueError as e:
        sys.exit(str(e))
    raw_path = save_raw(args.board, raw, now)

    postings = json.loads(raw)["jobs"]
    seen = load_seen(args.board)
    new, updated = watch.find_new(postings, seen)
    save_seen(args.board, updated)

    results = [result_for(p, resume) for p in new]
    if seen is None:
        print(f"Baseline run for {args.board}: {len(postings)} postings saved as seen, 0 new.")
    else:
        print(f"{args.board}: {len(postings)} postings, {len(new)} new since last run.")
    for r in results:
        print()
        print_result(r)

    results_path = save_results({
        "run_at": now.isoformat(timespec="seconds"),
        "board": args.board,
        "baseline": seen is None,
        "raw_file": str(raw_path.relative_to(PROJECT)),
        "postings_fetched": len(postings),
        "new_count": len(new),
        "results": results,
    }, now)
    print(f"\nRaw response: {raw_path.relative_to(PROJECT)}")
    print(f"Results:      {results_path.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
