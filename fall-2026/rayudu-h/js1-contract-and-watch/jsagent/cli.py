"""Command line: one watch run against one Greenhouse board for one persona résumé.

    python -m jsagent run --board anthropic --resume persona/priya-nair.resume.json
    python -m jsagent run --board anthropic --resume persona/priya-nair.resume.json \
        --from-raw evidence/seeded/anthropic-2026-10-31T0336.json.gz --state state/seeded_seen_ids.json --label seeded

Refusals are skipped and logged, never silently ignored (CONTRACT.md, Refuses).
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import sys
from pathlib import Path

from . import claude_judge, resume as resume_mod, rule, watch

ROOT = Path(__file__).resolve().parent.parent


def now_local() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).astimezone()


def read_raw_file(path: Path) -> bytes:
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix == ".gz" else data


def run(args) -> int:
    started = now_local()
    run_id = started.strftime("%Y-%m-%dT%H%M%S") + (f"-{args.label}" if args.label else "")
    run_dir = Path(args.runs_dir) / run_id
    n = 2
    while run_dir.exists():  # never reuse a run folder (raw responses are never overwritten)
        run_dir = Path(args.runs_dir) / f"{run_id}-{n}"
        n += 1
    run_id = run_dir.name
    state_path = Path(args.state)
    refusals, notes = [], []

    # 1. Résumé (Refuses 7). Invalid -> nothing is judged, and state is not advanced,
    #    so the postings are still reported as new on a later, valid run.
    resume = None
    try:
        resume = resume_mod.load(args.resume)
    except resume_mod.ResumeInvalid as e:
        refusals.append(f"résumé failed validation, so nothing was judged: {e}")

    # 2. Fetch (Refuses 1, 8) or read a saved earlier response (a seeded run, labeled).
    raw, source = None, None
    try:
        if args.from_raw:
            raw = read_raw_file(Path(args.from_raw))
            source = f"SEEDED: saved earlier response {args.from_raw} (not fetched by this run)"
        else:
            url = watch.board_url(args.board)
            raw = watch.fetch(url)
            source = f"live fetch {url}"
        jobs = watch.parse_jobs(raw)
    except watch.Refused as e:
        refusals.append(f"refused: {e}")
        jobs = None
    except watch.FetchFailed as e:
        refusals.append(f"fetch failed: {e}")
        jobs = None

    result = {"run_id": run_id, "started_at": started.isoformat(timespec="seconds"), "board": args.board,
              "source": source, "label": args.label or "live", "refusals": refusals, "notes": notes}

    if jobs is None:
        result["status"] = "fetch failed (this is NOT 'nothing new')"
        run_dir.mkdir(parents=True, exist_ok=True)
        write_report(run_dir, result, [], None)
        print_summary(result, [])
        return 1

    meta = watch.save_raw(run_dir, raw, {"source": source, "saved_at": now_local().isoformat(timespec="seconds"),
                                         "board": args.board, "label": args.label or "live"})
    seen = watch.load_seen(state_path)
    new = watch.new_postings(jobs, seen)
    result.update({"raw": meta, "postings_in_response": len(jobs),
                   "baseline": seen is None, "seen_before": 0 if seen is None else len(seen),
                   "new": len(new)})

    rows = []
    if resume is not None:
        claude_budget = args.max_claude
        for posting in new:
            row = {"record": rule.judge(posting, resume)}
            if args.no_claude:
                row["judgment"] = {"valid": False, "errors": ["Claude judge not requested (--no-claude)"]}
            elif claude_budget <= 0:
                row["judgment"] = {"valid": False, "errors": ["Claude judge skipped: --max-claude budget used up"]}
            else:
                claude_budget -= 1
                row["judgment"] = claude_judge.judge(posting, resume, version=args.prompt)
            rows.append(row)
        if rows:
            with open(run_dir / "judgments.jsonl", "w") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        watch.save_seen(state_path, (seen or set()) | {j["id"] for j in jobs}, run_id)
        result["status"] = "baseline: no postings reported as new" if seen is None else f"{len(new)} new posting(s)"
    else:
        result["status"] = "résumé invalid: nothing judged; state not advanced"

    (run_dir / "run.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    write_report(run_dir, result, rows, meta)
    print_summary(result, rows)
    return 0


def _cell(text) -> str:
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def write_report(run_dir: Path, result: dict, rows: list, meta) -> None:
    lines = [f"# Watch run {result['run_id']}", ""]
    if result.get("label") and result["label"] != "live":
        lines += [f"> **{result['label'].upper()} RUN.** The input is a saved earlier response, not a fetch made by this run.", ""]
    lines += [f"- Board: `{result['board']}`", f"- Source: {result.get('source')}",
              f"- Started: {result['started_at']}", f"- Status: **{result['status']}**"]
    if meta:
        lines += [f"- Raw response: `{meta['saved_as']}`, {meta['raw_bytes']} bytes, sha256 `{meta['raw_sha256']}`",
                  f"- Postings in response: {result['postings_in_response']}; ids seen before this run: "
                  f"{result['seen_before']}; new: {result['new']}"]
    lines.append("")
    if result["refusals"]:
        lines += ["## Refusals (skipped and logged)", ""] + [f"- {r}" for r in result["refusals"]] + [""]
    if result.get("baseline"):
        lines += ["Baseline run: every posting id was recorded as seen; none is reported as new.", ""]
    if rows:
        lines += ["## New postings", "",
                  "**Record** = the rule in CONTRACT.md; anyone can recompute it. "
                  "**Judgment** = Claude under the prompt contract; an opinion, not a fact. "
                  "Where they disagree, the record is the rule's verdict.", "",
                  "| id | title | location | Record (rule) | Judgment (Claude) | agree? |", "|---|---|---|---|---|---|"]
        for r in rows:
            rec, jud = r["record"], r["judgment"]
            if jud.get("valid"):
                j = jud["judgment"]
                jtxt = f"{j['verdict']} ({j['confidence']} confidence)"
                agree = "yes" if j["verdict"] == rec["verdict"] else "**no**"
            else:
                jtxt, agree = "no valid judgment", "n/a"
            lines.append(f"| {rec['id']} | {_cell(rec['title'])} | {_cell(rec['location'])} | {rec['verdict']} | {jtxt} | {agree} |")
        lines += ["", "### Justifications", ""]
        for r in rows:
            rec, jud = r["record"], r["judgment"]
            lines += [f"**{rec['id']} — {rec['title']}**", "",
                      f"- Record (rule): {rec['verdict']}. {rec['justification']}"]
            if jud.get("valid"):
                j = jud["judgment"]
                lines.append(f"- Judgment (Claude, {', '.join(jud.get('models_used') or [])}, {jud.get('started_at')}, "
                             f"prompt {jud.get('prompt_version')}): {j['verdict']}, {j['confidence']} confidence. "
                             f"Fields: {', '.join(j['resume_fields'])} / {', '.join(j['posting_fields'])}. {j['justification']}")
                if jud.get("ungrounded_quotes"):
                    lines.append(f"- ⚠ Claude quoted words not found in the posting or résumé: {jud['ungrounded_quotes']}")
            else:
                lines.append(f"- Judgment (Claude): rejected or not requested: {'; '.join(jud.get('errors', []))}")
            lines.append("")
    (run_dir / "report.md").write_text("\n".join(lines) + "\n")


def print_summary(result: dict, rows: list) -> None:
    print(f"run {result['run_id']} [{result.get('label')}]: {result['status']}")
    for r in result["refusals"]:
        print(f"  REFUSED/FAILED: {r}")
    if result.get("raw"):
        print(f"  postings in response: {result['postings_in_response']}, seen before: {result['seen_before']}, new: {result['new']}")
    for r in rows:
        rec, jud = r["record"], r["judgment"]
        j = jud.get("judgment") if jud.get("valid") else None
        print(f"  {rec['id']}  {rec['title'][:60]!r}")
        print(f"    RECORD   (rule):   {rec['verdict']} — {rec['justification']}")
        print(f"    JUDGMENT (Claude): " + (f"{j['verdict']} ({j['confidence']}) — {j['justification']}" if j
                                            else f"none — {'; '.join(jud.get('errors', []))}"))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="jsagent")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="one watch run")
    r.add_argument("--board", required=True)
    r.add_argument("--resume", required=True)
    r.add_argument("--state", default=str(ROOT / "state" / "seen_ids.json"))
    r.add_argument("--runs-dir", default=str(ROOT / "runs"))
    r.add_argument("--from-raw", help="judge a saved earlier response instead of fetching (a seeded run)")
    r.add_argument("--label", help="label for the run id and report, e.g. seeded")
    r.add_argument("--prompt", default="v2", help="Claude judge prompt version (prompts/judge_<v>.md); v2 chosen by Hemanth after the prompt experiment")
    r.add_argument("--no-claude", action="store_true", help="rule judge only")
    r.add_argument("--max-claude", type=int, default=25, help="at most this many Claude calls per run")
    args = p.parse_args(argv)
    if args.from_raw and not args.label:
        p.error("--from-raw needs --label (e.g. seeded) so the run is labeled")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
