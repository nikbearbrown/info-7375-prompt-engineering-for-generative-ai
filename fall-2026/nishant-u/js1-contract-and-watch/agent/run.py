"""One command: watch -> rule judge -> (optional) Claude judge -> validator -> report.

    python3 -m agent.run                      # live fetch of the Faire board
    python3 -m agent.run --replay runs/<run>/raw.json     # no network
    python3 -m agent.run --replay edited.json --seeded    # a labeled seeded run
    python3 -m agent.run --claude             # also ask Claude for a judgment
"""
import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from agent import ROOT, claude_judge, rules, validator, watch
from agent.resume import RefusedResume, load_resume


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="python3 -m agent.run", description=__doc__.splitlines()[0])
    parser.add_argument("--replay", type=Path, help="re-run from a saved board response; no network")
    parser.add_argument("--seeded", action="store_true",
                        help="label a --replay run as seeded (a constructed or edited response)")
    parser.add_argument("--claude", action="store_true", help="also run the Claude judge on new postings")
    parser.add_argument("--board-url", default=watch.BOARD_URL)
    parser.add_argument("--state", type=Path, default=ROOT / "state" / "seen_ids.json")
    parser.add_argument("--runs", type=Path, default=ROOT / "runs")
    parser.add_argument("--resume", type=Path, default=ROOT / "data" / "resume.example.json")
    parser.add_argument("--requirements", type=Path, default=ROOT / "data" / "requirements.json")
    args = parser.parse_args(argv)
    if args.seeded and not args.replay:
        parser.error("--seeded only labels a --replay run")
    return args


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def claude_section(new_jobs, resume, new_ids, run_dir):
    judgments = []
    for job in new_jobs:
        outcome = claude_judge.judge(job, resume, run_dir / "claude")
        entry = {"posting_id": job["id"], "label": "judgment", "status": outcome["status"]}
        if outcome["status"] != "ran":
            entry["reason"] = outcome["reason"]
        else:
            entry["meta"] = outcome["meta"]
            entry["raw_result"] = outcome["result"]
            entry["validator_errors"] = validator.validate(outcome["result"], resume, new_ids)
            if not entry["validator_errors"]:
                parsed = json.loads(outcome["result"])
                entry["verdict"] = parsed["verdict"]
                entry["citations"] = [dict(c, support=validator.support_check(c, job))
                                      for c in parsed["citations"]]
        judgments.append(entry)
    return judgments


def main(argv=None):
    args = parse_args(argv)
    resume = load_resume(args.resume)
    requirements = json.loads(args.requirements.read_text(encoding="utf-8"))

    if args.replay:
        body = args.replay.read_bytes()
        meta = {"mode": "seeded" if args.seeded else "replay", "source": str(args.replay),
                "replayed_at": now()}
    else:
        fetched_at = now()
        body = watch.fetch(args.board_url)
        meta = {"mode": "live", "source": args.board_url, "host": watch.check_host(args.board_url),
                "fetched_at": fetched_at}

    run_dir = watch.new_run_dir(args.runs, date.today().isoformat())
    meta = watch.save_raw(run_dir, body, **meta)
    jobs = watch.parse_jobs(body)
    ids = [job["id"] for job in jobs]
    new_ids, baseline = watch.compare_seen(args.state, ids)
    new_jobs = sorted((j for j in jobs if j["id"] in set(new_ids)), key=lambda j: j["id"])

    rule_verdicts = rules.judge_all(new_jobs, resume, requirements)
    by_id = {j["id"]: j for j in new_jobs}
    for v in rule_verdicts:
        for c in v["citations"]:
            c["support"] = validator.support_check(c, by_id[v["posting_id"]])

    if not args.claude:
        claude = {"status": "not requested", "judgments": []}
    else:
        judgments = claude_section(new_jobs, resume, set(new_ids), run_dir)
        ran = any(j["status"] == "ran" for j in judgments)
        claude = {"status": "ran" if ran else ("not run" if judgments else "no new postings"),
                  "judgments": judgments}

    report = {
        "run": run_dir.name,
        "raw": meta,
        "total_postings": len(jobs),
        "baseline": baseline,
        "new_ids": new_ids,
        "rule_verdicts": rule_verdicts,
        "claude": claude,
        "unsupported_citations": sum(c["support"] != "supported"
                                     for v in rule_verdicts for c in v["citations"])
                                 + sum(c["support"] != "supported"
                                       for j in claude["judgments"] for c in j.get("citations", [])),
    }
    watch.write_json_atomic(run_dir / "report.json", report)
    (run_dir / "report.md").write_text(render_markdown(report), encoding="utf-8", newline="\n")
    # The state moves only after the report is written, so a crash cannot lose new postings.
    watch.save_seen(args.state, ids, run_dir.name)
    return report


def render_markdown(report):
    raw = report["raw"]
    when = raw.get("fetched_at") or raw.get("replayed_at")
    lines = [
        f"# Run {report['run']}",
        "",
        f"- Mode: **{raw['mode']}**" + (" (no network; labeled seeded)" if raw["mode"] == "seeded" else
                                         " (no network)" if raw["mode"] == "replay" else ""),
        f"- Source: `{raw['source']}`",
        f"- Time (UTC): {when}",
        f"- Raw response: `raw.json`, {raw['bytes']} bytes, sha256 `{raw['sha256']}`",
        f"- Postings in response: {report['total_postings']}",
        f"- Baseline: {'yes, all ids saved and 0 reported as new' if report['baseline'] else 'no'}",
        f"- New since last run: {len(report['new_ids'])}",
        f"- Citations not supported: {report['unsupported_citations']}",
        "",
        "## Rule verdicts [record]",
        "",
    ]
    if not report["rule_verdicts"]:
        lines.append("None: no new postings.")
    for v in report["rule_verdicts"]:
        lines.append(f"- **{v['posting_id']}** {v['title']}: `{v['verdict']}` [record]. {v['justification']}")
        for c in v["citations"]:
            quote = repr(c["quote"]) if c["quote"] is not None else f"absent: {', '.join(c['absent_terms'])}"
            lines.append(f"  - {c['check']} `{c['posting_field']}`"
                         + (f" / résumé `{c['resume_field']}`" if c["resume_field"] else "")
                         + f": {quote} ({c['support']})")
    lines += ["", "## Claude verdicts [judgment]", ""]
    claude = report["claude"]
    if claude["status"] == "not requested":
        lines.append("Claude judge: not requested (run without --claude).")
    elif not claude["judgments"]:
        lines.append("Claude judge: no new postings to judge.")
    for j in claude["judgments"]:
        if j["status"] != "ran":
            lines.append(f"- **{j['posting_id']}**: Claude judge: not run ({j['reason']}).")
        elif j["validator_errors"]:
            lines.append(f"- **{j['posting_id']}**: rejected by the validator [judgment]: "
                         + "; ".join(j["validator_errors"]))
        else:
            meta = j["meta"]
            lines.append(f"- **{j['posting_id']}**: `{j['verdict']}` [judgment], {meta['model']}, "
                         f"session {meta['session_id']}, {meta['date']}")
            for c in j["citations"]:
                lines.append(f"  - `{c['posting_field']}` / résumé `{c['resume_field']}`: "
                             f"{c['quote']!r} ({c['support']})")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    try:
        result = main()
    except (watch.RefusedHost, RefusedResume) as exc:
        sys.exit(f"refused: {exc}")
    print(f"{result['run']}: {result['total_postings']} postings, "
          f"{'baseline' if result['baseline'] else str(len(result['new_ids'])) + ' new'}, "
          f"report in runs/{result['run']}/report.md")
