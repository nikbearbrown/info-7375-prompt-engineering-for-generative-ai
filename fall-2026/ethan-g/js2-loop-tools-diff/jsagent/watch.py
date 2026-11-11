"""The watch (v3): fetch (or replay) every board in config/boards.json, find postings new since the last run,
and judge each new data-titled posting twice (rule record + Claude judgment).

    python3 -m jsagent.watch --resume persona/evan-gordon.resume.json
    python3 -m jsagent.watch --resume ... --from-dir evidence/raw/<run folder> --seeded "why"
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from . import audit, claude_judge, fetch, resume, rule, state

ROOT = Path(__file__).resolve().parent.parent


def rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def summarize_record(v):
    failed = [f"{c['check']}✗" for c in v["checks"] if not c["passed"]]
    r4 = v["checks"][3]["matched"]
    prefs = [name for name, key in [("location", "preferred_location"), ("years", "preferred_years")] if v.get(key)]
    # Preferences are printed only for relevant postings (a preference on a rejected posting misleads); the report keeps both flags.
    pref = f"; PREFERRED {' + '.join(prefs)}" if prefs and v["verdict"] == "relevant" else ""
    return f"{v['verdict']}  (failed: {', '.join(failed) or 'none'}; skills matched: {', '.join(r4) or 'none'}{pref})"


def digest(raws):
    h = hashlib.sha256()
    for board in sorted(raws):
        h.update(board.encode() + b"\0" + hashlib.sha256(raws[board]).digest())
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resume", required=True)
    ap.add_argument("--boards", default=str(fetch.BOARDS_PATH), help="board list (default config/boards.json)")
    ap.add_argument("--state", default=str(ROOT / "state" / "seen_ids.json"))
    ap.add_argument("--raw-dir", default=str(ROOT / "evidence" / "raw"))
    ap.add_argument("--runs-dir", default=str(ROOT / "evidence" / "runs"))
    ap.add_argument("--from-dir", help="replay a saved run folder instead of fetching")
    ap.add_argument("--seeded", help="required with --from-dir: say how the saved run was made")
    ap.add_argument("--prompt", default=str(ROOT / "prompts" / "judge_v1_baseline.txt"))
    ap.add_argument("--model", default=claude_judge.DEFAULT_MODEL)
    ap.add_argument("--no-claude", action="store_true", help="skip the Claude judge (rule judge only)")
    args = ap.parse_args(argv)

    r = resume.load_resume(args.resume)  # refuses non-fictional résumés
    now = datetime.now().astimezone()

    if args.from_dir:
        if not args.seeded:
            ap.error("--from-dir needs --seeded '<how this run folder was made>' so the run is labeled")
        run_dir = Path(args.from_dir)
        raws, fetch_errors = fetch.load_run_dir(run_dir), {}
        for board in raws:
            fetch.board_url(board)  # validates every token, even for replays
        source = "seeded"
    else:
        boards = fetch.load_boards(args.boards)
        run_dir = fetch.unused_path(Path(args.raw_dir) / f"{now:%Y-%m-%dT%H%M%S}_live")
        raws, fetch_errors = fetch.fetch_lists(boards, run_dir)
        source = "live"

    postings = [p for board, body in raws.items() for p in fetch.parse_postings(body, board)]
    state.check_unique_ids(postings)
    prev = state.load_state(args.state)
    is_baseline, new = state.diff_new(prev, postings)
    baselined_boards = state.new_boards(prev, postings)
    run_id = f"{now:%Y-%m-%dT%H%M%S}_{source}"

    # Only data-titled postings (R1) are judged; R1 needs only the title, so nothing else needs a description.
    new_data = [p for p in new if rule.check_r1(p, r)["passed"]]
    judged = []
    for p in new_data:
        body = fetch.saved_job(run_dir, p["board"], p["id"]) if source == "seeded" else fetch.fetch_job(p["board"], p["id"], run_dir)
        judged.append(fetch.parse_job(body, p["board"]))

    records = [rule.judge(p, r) for p in judged]
    errors = audit.audit_verdicts(judged, r, records)
    judgments = [] if args.no_claude else [claude_judge.judge(p, r, args.prompt, model=args.model) for p in judged]

    run_meta = {
        "run_id": run_id,
        "timestamp": now.isoformat(timespec="seconds"),
        "source": source,
        "seeded_note": args.seeded,
        "raw_dir": rel(run_dir),
        "raw_digest_sha256": digest(raws),
        "boards_ok": len(raws),
        "boards_failed": fetch_errors,
        "boards_baselined": baselined_boards,
        "n_postings": len(postings),
        "baseline": is_baseline,
        "n_new_total": len(new),
        "n_new_data": len(new_data),
        "n_new_other": len(new) - len(new_data),
    }
    report = {
        **run_meta,
        "resume_file": rel(args.resume),
        "audit_errors": errors,
        "new_postings": [
            {"board": p["board"], "id": p["id"], "title": p["title"], "location": p["location"]["name"], "url": p["absolute_url"],
             "rule_verdict_record": rec,
             "claude_verdict_judgment": next((j for j in judgments if j["posting_id"] == p["id"]), None)}
            for p, rec in zip(judged, records)
        ],
    }
    runs_dir = Path(args.runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)
    report_path = fetch.unused_path(runs_dir / f"{run_id}.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n")

    label = f"SEEDED ({args.seeded})" if source == "seeded" else "LIVE"
    print(f"Run {run_id}  [{label}]  boards={len(raws)} ok, {len(fetch_errors)} failed  postings={len(postings)}  raw={rel(run_dir)}")
    if fetch_errors:
        print(f"Failed boards (contribute nothing this run, lose nothing from state): {', '.join(sorted(fetch_errors))}")
    if baselined_boards:
        print(f"Boards seen for the first time (baselined, none reported as new): {', '.join(baselined_boards)}")
    if is_baseline:
        print("Baseline run: every id recorded as seen; 0 postings reported as new.")
    else:
        print(f"New since last run: {len(new)} ({len(new_data)} with a data title, judged below; {len(new) - len(new_data)} others counted only)")
    for p, rec in zip(judged, records):
        print(f"\n- [{p['board']} {p['id']}] {p['title']} — {p['location']['name']}")
        print(f"    Rule verdict (record): {summarize_record(rec)}")
        j = next((j for j in judgments if j["posting_id"] == p["id"]), None)
        if j is None:
            print("    Claude judgment: skipped (--no-claude)")
        elif j["status"] == "valid":
            print(f"    {j['label']}: {j['verdict']} — {j['reason']}")
            print(f"      cites résumé {j['resume_fields']} / posting {j['posting_fields']}")
        else:
            print(f"    Claude judgment: {j['status'].upper()} by validator — {'; '.join(j['errors'])[:200]}")

    if errors:
        print("\nAUDIT FAILED — state not updated:", *errors, sep="\n  ")
        print(f"Report: {rel(report_path)}")
        return 2
    state.save_state(args.state, state.update_state(prev, postings, run_meta, fetched_boards=list(raws)))
    print(f"\nAudit: {len(records)} rule verdict(s) recomputed and citations verified.")
    print(f"Report: {rel(report_path)}   State: {rel(args.state)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
