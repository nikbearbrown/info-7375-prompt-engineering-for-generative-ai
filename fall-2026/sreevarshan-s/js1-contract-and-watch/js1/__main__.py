"""python3 -m js1 | --baseline | --from-file RAW.json

No flags: the watch run. Refuses unless a baseline exists. Fetches once through the
allow-list, saves the raw response, reports fetched / new / removed by posting id, runs
the rule judge on new postings only, saves the records, and only then updates state
(keeping the previous state file beside it). The Claude judge is a separate command.

--baseline fetches once, saves the raw response, and records every posting id. It
refuses if state already exists, and it never runs the rule judge.

--from-file (seeded runs) is deferred; see IMPLEMENTATION_CHOICES.md.

Exit codes: 0 success, 1 persona refused, 2 seeded run not implemented,
3 baseline refused (state exists), 5 watch refused (no state), 6 fetch failed (state unchanged).
"""

import argparse
import json
import shutil
import sys
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from js1 import fetch, rule_judge, watch
from js1.allowlist import HostNotAllowed
from js1.persona import PersonaRefused, load_persona

ROOT = Path(__file__).resolve().parent.parent
RESUME = ROOT / "persona" / "priya-nair.resume.json"
PROFILE = ROOT / "persona" / "priya-nair.profile.json"
STATE = ROOT / "state" / "seen_ids.json"
RAW_DIR = ROOT / "evidence" / "raw"
RULE_DIR = ROOT / "evidence" / "rule"
BOARD = "databricks"

EXIT_OK = 0
EXIT_PERSONA = 1
EXIT_SEEDED_DEFERRED = 2
EXIT_BASELINE_EXISTS = 3
EXIT_NO_BASELINE = 5
EXIT_FETCH_FAILED = 6

FETCH_ERRORS = (urllib.error.URLError, HostNotAllowed, TimeoutError, OSError, ValueError)


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def run_baseline(state_path, raw_dir, fetch_raw, stamp, out=sys.stdout, err=sys.stderr):
    """Baseline-only run. Checks for existing state before any network call."""
    if Path(state_path).exists():
        print(f"refusing --baseline: {state_path} already exists; a baseline was already recorded.", file=err)
        return EXIT_BASELINE_EXISTS
    raw = fetch_raw()
    raw_path = fetch.save_raw(raw, raw_dir, stamp)
    board = json.loads(raw)
    result = watch.diff(board, None)
    watch.save_seen(state_path, result.seen_after, last_fetched=result.seen_after, last_run=stamp)
    print(f"raw response saved: {raw_path}", file=out)
    print(f"BASELINE: {len(result.seen_after)} postings recorded, {len(result.new_postings)} new", file=out)
    return EXIT_OK


def _previous_stamp(state, raw_dir, current_stamp):
    """The previous run's stamp: from state, else the newest earlier raw evidence file name."""
    if state.get("last_run"):
        return state["last_run"]
    earlier = sorted(p.stem for p in Path(raw_dir).glob("*.json") if p.stem < current_stamp)
    return earlier[-1] if earlier else "unknown-previous"


def run_watch(state_path, raw_dir, rule_dir, fetch_raw, stamp, resume, profile, judge=rule_judge.judge,
              out=sys.stdout, err=sys.stderr):
    state_path = Path(state_path)
    state = watch.load_state(state_path)
    if state is None:
        print(f"refusing: {state_path} does not exist. Run the baseline first: python3 -m js1 --baseline",
              file=err)
        return EXIT_NO_BASELINE

    try:
        raw = fetch_raw()
    except FETCH_ERRORS as exc:
        print(f"fetch failed ({type(exc).__name__}: {exc}); state unchanged.", file=err)
        return EXIT_FETCH_FAILED
    raw_path = fetch.save_raw(raw, raw_dir, stamp)
    try:
        board = json.loads(raw)
        jobs = board["jobs"]
    except (ValueError, KeyError, TypeError) as exc:
        print(f"fetch failed: response saved at {raw_path} is not a Greenhouse jobs list "
              f"({type(exc).__name__}: {exc}); state unchanged.", file=err)
        return EXIT_FETCH_FAILED

    fetched_ids = {job["id"] for job in jobs}
    previous_fetched = state["last_fetched_ids"] if state["last_fetched_ids"] is not None else state["seen_ids"]
    result = watch.diff(board, state["seen_ids"])
    removed = sorted(previous_fetched - fetched_ids)

    records = [judge(job, resume, profile) for job in result.new_postings]
    previous = _previous_stamp(state, raw_dir, stamp)
    backup = state_path.with_name(f"{state_path.stem}.{previous}{state_path.suffix}")
    run_info = {
        "stamp": stamp,
        "board": BOARD,
        "raw_evidence": str(Path(raw_path).relative_to(ROOT)) if Path(raw_path).is_relative_to(ROOT) else str(raw_path),
        "fetched": len(fetched_ids),
        "new": len(result.new_postings),
        "removed": len(removed),
        "removed_ids": removed,
        "previous_run": previous,
        "previous_state_backup": backup.name,
    }
    rule_path = Path(rule_dir) / f"{stamp}.json"
    rule_path.parent.mkdir(parents=True, exist_ok=True)
    rule_path.write_text(json.dumps({"run": run_info, "records": records}, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")

    print(f"raw response saved: {raw_path}", file=out)
    print(f"WATCH {stamp}: {len(fetched_ids)} fetched, {len(result.new_postings)} new, "
          f"{len(removed)} removed since {previous}", file=out)
    for rec in records:
        print(f"  NEW {rec['posting_id']}  {rec['title']}", file=out)
        print(f"      record: {rec['verdict']}", file=out)
        for check in rec["failed_checks"]:
            print(f"      failed check {check['check']} ({check['name']}): {check['reason']}", file=out)
    print(f"rule records saved: {rule_path}", file=out)

    # Everything above succeeded: keep the previous state, then update it.
    if not backup.exists():
        shutil.copy2(state_path, backup)
    watch.save_seen(state_path, result.seen_after, last_fetched=fetched_ids, last_run=stamp)
    print(f"state updated: {state_path} (previous kept as {backup.name})", file=out)
    return EXIT_OK


def main(argv=None):
    parser = argparse.ArgumentParser(prog="js1")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--baseline", action="store_true", help="record every posting id from one live fetch; no judging")
    mode.add_argument("--from-file", help="seeded run against a saved raw response (deferred)")
    args = parser.parse_args(argv)
    try:
        resume, profile = load_persona(RESUME, PROFILE)
    except PersonaRefused as exc:
        print(exc, file=sys.stderr)
        return EXIT_PERSONA
    if args.baseline:
        return run_baseline(STATE, RAW_DIR, lambda: fetch.fetch_board(BOARD), utc_stamp())
    if args.from_file:
        print("SEEDED js1: seeded runs are deferred (IMPLEMENTATION_CHOICES.md). Nothing fetched, no state written.",
              file=sys.stderr)
        return EXIT_SEEDED_DEFERRED
    return run_watch(STATE, RAW_DIR, RULE_DIR, lambda: fetch.fetch_board(BOARD), utc_stamp(), resume, profile)


if __name__ == "__main__":
    sys.exit(main())
