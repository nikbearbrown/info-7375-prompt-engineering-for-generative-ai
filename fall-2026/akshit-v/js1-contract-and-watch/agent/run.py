"""One watch run: résumé check -> raw response -> new ids -> two judges -> report -> state.

Live run (fetches the board and saves the raw response):
    python -m agent.run --board figma --resume data/resume_jack_spencer.json
Run against a saved response (the report is labeled with the file's kind, e.g. SEEDED):
    python -m agent.run --board figma --resume data/resume_jack_spencer.json --from-file evidence/raw/<file>.json
Add --no-claude to skip the Claude judge.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import claude_judge, rule, watch
from agent.config import CLAUDE_MODEL, DEFAULT_BOARD, JUDGE_PROMPT, RUNS_DIR, STATE_FILE
from agent.fetch import check_board, fetch_board
from agent.postings import load_postings
from agent.resume import ResumeRejected, load_resume


def build_rows(new_postings: list[dict], rule_by_id: dict, claude_by_id: dict | None) -> list[dict]:
    """Pair each posting with its own verdicts by id; refuse to pair mismatched ids (W1)."""
    rows = []
    for p in new_postings:
        r = rule_by_id[p["id"]]
        if r["id"] != p["id"]:
            raise AssertionError(f"rule verdict for {r['id']} attached to posting {p['id']}")
        c = None
        if claude_by_id is not None:
            c = claude_by_id[p["id"]]
            if c["asked_id"] != p["id"]:
                raise AssertionError(f"Claude verdict for {c['asked_id']} attached to posting {p['id']}")
        rows.append({"posting": p, "rule": r, "claude": c})
    return rows


def render_row(row: dict) -> str:
    p, r, c = row["posting"], row["rule"], row["claude"]
    lines = [f"id {p['id']} | {p['title']} | {p['location_name']}",
             f"  RULE (record, recomputable):  {r['verdict']}",
             f"    because: {r['because']}",
             f"    cited: resume.{', resume.'.join(r['cited_resume_fields'])}, "
             f"posting.{', posting.'.join(r['cited_posting_fields'])}"]
    if c is None:
        lines.append("  CLAUDE: not run (--no-claude)")
    elif not c["valid"]:
        lines.append(f"  CLAUDE: invalid output (rejected): {c['rejection']}")
    else:
        date = c["asked_at_utc"][:10]
        parsed = c["parsed"]
        lines.append(f"  CLAUDE (judgment, model output, not verified; {c['model_requested']}, {date}):  {c['verdict']}")
        lines.append(f"    cited: resume.{', resume.'.join(parsed['cited_resume_fields'])}, "
                     f"posting.{', posting.'.join(parsed['cited_posting_fields'])}")
        lines.append(f"    reason: {parsed['reason']}")
        if c["verdict"] != r["verdict"]:
            lines.append("  DISAGREE")
    lines.append(f"  url: {p['absolute_url']}")
    return "\n".join(lines)


def source_label(raw_path: Path, live: bool) -> str:
    if live:
        return "LIVE fetch"
    meta_path = raw_path.with_suffix(".meta.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    kind = meta.get("kind", "unknown").upper()
    note = f" - {meta['note']}" if meta.get("note") else ""
    return f"SAVED FILE, kind={kind}{note}"


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", default=DEFAULT_BOARD)
    ap.add_argument("--resume", required=True, type=Path)
    ap.add_argument("--from-file", type=Path, help="use a saved raw response instead of fetching")
    ap.add_argument("--state", type=Path, default=STATE_FILE)
    ap.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    ap.add_argument("--no-claude", action="store_true")
    args = ap.parse_args(argv)

    # Refuses (2): a résumé that fails the check stops the run before anything is printed.
    try:
        resume = load_resume(args.resume)
    except ResumeRejected as e:
        print("REFUSED: résumé failed validation; nothing else was run.", file=sys.stderr)
        for problem in e.args[0]:
            print(f"  - {problem}", file=sys.stderr)
        return 2
    check_board(args.board)

    started = datetime.now(timezone.utc)
    live = args.from_file is None
    raw_path = fetch_board(args.board) if live else args.from_file
    postings = load_postings(raw_path)
    state = watch.load_state(args.state)
    new_ids = watch.find_new(state, args.board, postings)
    baseline = new_ids is None
    new_postings = [] if baseline else [p for p in postings if p["id"] in set(new_ids)]

    rule_by_id = rule.judge_all(new_postings, resume)
    claude_by_id = None
    if new_postings and not args.no_claude:
        template = JUDGE_PROMPT.read_text(encoding="utf-8")
        claude_by_id = claude_judge.judge_all(new_postings, resume, template)
    rows = build_rows(new_postings, rule_by_id, claude_by_id)

    run_id = f"{started:%Y%m%dT%H%M%SZ}_{args.board}_{'baseline' if baseline else 'run'}"
    header = [
        f"# Watch run {run_id}",
        f"date (UTC): {started.isoformat(timespec='seconds')}",
        f"board: {args.board}   persona: {resume['name']} (fictional)",
        f"input: {source_label(Path(raw_path), live)}",
        f"raw response: {Path(raw_path).as_posix()}",
        f"postings in response: {len(postings)}   seen before: {0 if baseline else len(state['seen_ids'])}",
        ("BASELINE run: no state file yet, so no posting is reported as new."
         if baseline else f"new since last run: {len(new_postings)}"),
        f"Claude judge: {'off' if args.no_claude else CLAUDE_MODEL}",
        "",
    ]
    report = "\n".join(header) + "\n\n".join(render_row(r) for r in rows) + "\n"
    print(report)

    args.runs_dir.mkdir(parents=True, exist_ok=True)
    (args.runs_dir / f"{run_id}.txt").write_text(report, encoding="utf-8")
    (args.runs_dir / f"{run_id}.json").write_text(json.dumps({
        "run_id": run_id, "baseline": baseline, "input": source_label(Path(raw_path), live),
        "raw_response": Path(raw_path).as_posix(), "rows": rows,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # State is written last, only after the response parsed and the report was saved.
    record = {"run_id": run_id, "raw_response": Path(raw_path).as_posix(), "live": live,
              "postings": len(postings), "new": len(new_postings), "baseline": baseline}
    watch.save_state(args.state, watch.next_state(state, args.board, postings, record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
