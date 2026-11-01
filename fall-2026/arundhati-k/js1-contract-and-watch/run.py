"""Job-Search Agent 1 — one watch run. See README.md for exact commands.

    python3 run.py                                   # live fetch of the Stripe board (allow-listed)
    python3 run.py --from-file PATH                  # run against a saved response; always labeled SEEDED
    python3 run.py --claude                          # also ask Claude for a labeled model judgment per new posting
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from jsagent import claude_judge, rule
from jsagent.checks import alignment_errors, evidence_errors, rule_record_as_evidence
from jsagent.fetch import board_url, fetch
from jsagent.resume import load_resume, skill_fields
from jsagent.watch import load_raw, load_state, new_postings, next_state, parse_jobs, save_raw, save_state

HERE = Path(__file__).resolve().parent


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--board", default="stripe")
    p.add_argument("--resume", default=str(HERE / "persona" / "rohan-desai.resume.example.json"))
    p.add_argument("--state", default=str(HERE / "state" / "seen_ids.json"))
    p.add_argument("--evidence", default=str(HERE / "evidence" / "raw"))
    p.add_argument("--reports", default=str(HERE / "reports"))
    p.add_argument("--from-file", help="saved response to use instead of a live fetch (run is labeled seeded)")
    p.add_argument("--claude", action="store_true", help="ask Claude (claude -p) for a model judgment per new posting")
    p.add_argument("--prompt", default=str(HERE / "prompts" / "baseline.txt"))
    p.add_argument("--model", default=None)
    args = p.parse_args(argv)

    resume = load_resume(args.resume)
    skills = skill_fields(resume)
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")

    if args.from_file:
        source, label = str(args.from_file), "seeded"
        raw = load_raw(args.from_file)
    else:
        source, label = board_url(args.board), "live"
        raw = fetch(source)
    evidence = save_raw(raw, args.evidence, stamp, label)
    jobs = parse_jobs(raw)

    state = load_state(args.state)
    baseline = state is None
    fresh = new_postings(state, jobs)

    records = []
    for job in fresh:
        r = rule.judge(job, skills)
        r["location"] = rule.location_name(job)
        r["departments"] = rule.departments(job)
        r["url"] = job.get("absolute_url")
        r["rule_label"] = "RECORD (deterministic rule, CONTRACT §5) — recomputable by anyone"
        r["rule_evidence_errors"] = evidence_errors(rule_record_as_evidence(r), job, resume)
        if args.claude:
            try:
                r["claude"] = claude_judge.judge(job, resume, claude_judge.load_template(args.prompt), model=args.model,
                                                 log_path=Path(args.reports) / f"{stamp}-claude-calls.jsonl", tag="watch")
            except Exception as e:  # a failed call is reported, never replaced by a guess
                r["claude"] = {"label": claude_judge.LABEL, "valid": False, "verdict": None, "errors": [str(e)]}
        else:
            r["claude"] = {"label": claude_judge.LABEL, "valid": False, "verdict": None, "errors": ["not run (no --claude)"]}
        records.append(r)

    align = alignment_errors(fresh, [rule_record_as_evidence(r) for r in records])
    run_record = {
        "run_at_utc": now.isoformat(timespec="seconds"),
        "board": args.board,
        "label": label,
        "source": source,
        "raw": evidence,
        "postings_on_board": len(jobs),
        "baseline": baseline,
        "new_ids": [r["posting_id"] for r in records],
    }
    report = {"run": run_record, "alignment_errors": align, "postings": records}
    Path(args.reports).mkdir(parents=True, exist_ok=True)
    stem = evidence["file"].removesuffix(".json.gz")
    (Path(args.reports) / f"{stem}.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    (Path(args.reports) / f"{stem}.md").write_text(render(report))
    save_state(args.state, next_state(state, jobs, run_record))

    print(render(report))
    bad = align or any(r["rule_evidence_errors"] for r in records)
    return 1 if bad else 0


def render(report):
    run = report["run"]
    head = "SEEDED RUN (saved response, not a live fetch)" if run["label"] == "seeded" else "LIVE RUN"
    lines = [
        f"# Watch run {run['run_at_utc']} — {head}",
        "",
        f"- board: `{run['board']}` · source: `{run['source']}`",
        f"- raw response saved: `evidence/raw/{run['raw']['file']}` (sha256 {run['raw']['sha256_of_raw'][:16]}…, {run['raw']['bytes']} bytes)",
        f"- postings on board: {run['postings_on_board']} · baseline: {run['baseline']} · new since last run: {len(run['new_ids'])}",
        f"- alignment check (wrong version 1): {'PASS' if not report['alignment_errors'] else report['alignment_errors']}",
        "",
    ]
    if run["baseline"]:
        lines.append("Baseline run: every current posting id recorded as seen; none reported as new.")
    relevant = [r for r in report["postings"] if r["verdict"] == "RELEVANT"]
    lines.append(f"Rule verdicts: {len(relevant)} RELEVANT of {len(report['postings'])} new.\n")
    for r in report["postings"]:
        c = r["claude"]
        claude_line = (f"{c['verdict']} — {c.get('reason')}" if c.get("valid")
                       else f"no valid judgment ({'; '.join(c.get('errors', []))[:200]})")
        lines += [
            f"## {r['posting_id']} · {r['title']}",
            f"- location: {r['location']} · departments: {', '.join(r['departments']) or '—'}",
            f"- **Rule — {r['rule_label']}:** {r['justification']}",
            f"- rule evidence check (wrong version 2): {'PASS' if not r['rule_evidence_errors'] else r['rule_evidence_errors']}",
            f"- **Claude — {c['label']}:** {claude_line}",
            "",
        ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
