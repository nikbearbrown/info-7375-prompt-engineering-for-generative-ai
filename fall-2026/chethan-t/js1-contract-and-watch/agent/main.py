"""Run the watch: python -m agent.main [--board BOARD] [--resume PATH] [--no-claude]."""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from agent import claude_judge, fetch, rule, watch
from agent.resume import load_resume

PROJECT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT / "config.json"
RAW_DIR = PROJECT / "raw"
STATE_PATH = PROJECT / "state" / "seen_ids.json"
BOARD_NAME = re.compile(r"^[A-Za-z0-9_-]+$")


def parse_args(argv):
    config = json.loads(CONFIG_PATH.read_text())
    parser = argparse.ArgumentParser(prog="python -m agent.main")
    parser.add_argument("--board", default=config["board"], help="Greenhouse board name")
    parser.add_argument("--resume", default=str(PROJECT / config["resume"]), help="persona résumé JSON")
    parser.add_argument("--no-claude", action="store_true", help="skip the Claude verdict (judgment)")
    parser.add_argument("--replay", metavar="FILE", help="judge a saved raw Greenhouse response instead of fetching")
    parser.add_argument("--state", default=str(STATE_PATH), help="seen-postings file")
    parser.add_argument("--out", default=str(PROJECT), help="folder for results/ and claude_responses/")
    parser.add_argument("--label", default="", help="label stored with the run, e.g. SEEDED")
    return parser.parse_args(argv)


def rel(path):
    path = Path(path).resolve()
    return str(path.relative_to(PROJECT)) if path.is_relative_to(PROJECT) else str(path)


def load_seen(state_path, board):
    """Seen ids for this board, or None when this is the board's baseline run."""
    if not state_path.exists():
        return None
    return json.loads(state_path.read_text()).get(board)


def save_seen(state_path, board, ids):
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    state[board] = ids
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n")


def result_for(posting, resume, use_claude=True):
    record = rule.judge(posting, resume)
    if use_claude:
        judgment = claude_judge.judge(posting, resume)
    else:
        judgment = claude_judge.not_run("skipped (--no-claude)")
    return {
        "posting_id": posting["id"],
        "title": posting.get("title"),
        "location": (posting.get("location") or {}).get("name"),
        "url": posting.get("absolute_url"),
        "flags": rule.auth_flags(posting),
        "record": record,
        "judgment": judgment,
    }


def print_result(r):
    rec, jud, flags = r["record"], r["judgment"], r["flags"]
    print(f"{r['title']} — {r['location']} (id {r['posting_id']})")
    print(f"  {r['url']}")
    print(f"  record:   [{rec['verdict']}] {rec['reason']}")
    print(f"            posting {rec['posting_fields']} / résumé {rec['resume_fields']}")
    if jud["status"] == "ok":
        print(f"  judgment: [{jud['verdict']}] {jud['reason']}")
        print(f"            posting {jud['posting_fields']} / résumé {jud['resume_fields']}")
    else:
        detail = jud.get("error") or f"reply saved to {jud.get('raw_file')}"
        print(f"  judgment: {jud['status']} ({detail})")
    print("  flags:    " + ", ".join(f"{k}={v}" for k, v in flags.items()))


def save_raw(board, raw, now):
    """Write the response bytes untouched; never overwrite an earlier run's file."""
    RAW_DIR.mkdir(exist_ok=True)
    stem = f"{board}_{now:%Y%m%dT%H%M%S}"
    path, n = RAW_DIR / f"{stem}.json", 2
    while path.exists():
        path, n = RAW_DIR / f"{stem}_{n}.json", n + 1
    path.write_bytes(raw)
    return path


def save_results(results_dir, run, now):
    """Append this run to results/<date>.json so same-day runs are kept."""
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f"{now:%Y-%m-%d}.json"
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

    out = Path(args.out)
    state_path = Path(args.state)
    claude_judge.RESPONSES_DIR = out / "claude_responses"

    now = datetime.now().astimezone()
    if args.replay:
        raw_path = Path(args.replay)
        raw = raw_path.read_bytes()
    else:
        try:
            raw = fetch.fetch_board(fetch.board_url(args.board))
        except ValueError as e:
            sys.exit(str(e))
        raw_path = save_raw(args.board, raw, now)

    postings = json.loads(raw)["jobs"]
    seen = load_seen(state_path, args.board)
    new, updated = watch.find_new(postings, seen)
    save_seen(state_path, args.board, updated)

    results = [result_for(p, resume, use_claude=not args.no_claude) for p in new]
    if args.label:
        print(f"[{args.label}] replayed {rel(raw_path)}" if args.replay else f"[{args.label}]")
    if seen is None:
        print(f"Baseline run for {args.board}: {len(postings)} postings saved as seen, 0 new.")
    else:
        print(f"{args.board}: {len(postings)} postings, {len(new)} new since last run.")
    for r in results:
        print()
        print_result(r)

    results_path = save_results(out / "results", {
        "run_at": now.isoformat(timespec="seconds"),
        "label": args.label or None,
        "board": args.board,
        "baseline": seen is None,
        "replay": bool(args.replay),
        "raw_file": rel(raw_path),
        "state_file": rel(state_path),
        "postings_fetched": len(postings),
        "new_count": len(new),
        "results": results,
    }, now)
    print(f"\nRaw response: {rel(raw_path)}" + (" (replayed, not fetched)" if args.replay else ""))
    print(f"Results:      {rel(results_path)}")


if __name__ == "__main__":
    main()
