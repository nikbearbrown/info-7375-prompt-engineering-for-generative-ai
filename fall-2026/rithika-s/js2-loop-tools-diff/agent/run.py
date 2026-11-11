"""CLI entry point for Job-Search Agent 1.

    python3 -m agent.run --board scaleai                    live fetch
    python3 -m agent.run --from-raw <file> --state <path>   offline, saved response
    add --claude to also ask Claude (judgment) about each new posting
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import claude_judge, fetch, resume as resume_mod, rule, state
from agent.check import check_verdicts

ROOT = Path(__file__).resolve().parent.parent
DEFAULTS = {
    "state": ROOT / "data" / "state.json",
    "resume": ROOT / "data" / "resume.example.json",
    "target": ROOT / "data" / "target.example.json",
    "raw_dir": ROOT / "data" / "raw",
    "reports_dir": ROOT / "reports" / "runs",
}
EXIT_REFUSED = 2
EXIT_CHECK_FAILED = 3


class RunError(Exception):
    """A refusal or bad input; the run stops with a clear message."""


def utc_timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _display_path(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_postings(data):
    """Return the jobs list from a Greenhouse response, ids deduplicated."""
    try:
        board = json.loads(data.decode("utf-8"))
        jobs = board["jobs"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError):
        raise RunError("raw response is not a Greenhouse jobs JSON object") \
            from None
    postings, seen = [], set()
    for job in jobs:
        pid = job.get("id") if isinstance(job, dict) else None
        if not isinstance(pid, int) or isinstance(pid, bool):
            raise RunError(f"posting without an integer id: {pid!r}")
        if pid not in seen:
            seen.add(pid)
            postings.append(job)
    return postings


def build_report(meta, postings, new_postings, verdicts, judgments):
    counts = {
        "postings_in_response": len(postings),
        "previously_seen": meta.pop("previously_seen"),
        "new": len(new_postings),
        "rule_relevant": sum(v["verdict"] == rule.RELEVANT for v in verdicts),
        "rule_not_relevant": sum(
            v["verdict"] == rule.NOT_RELEVANT for v in verdicts),
        "claude_judged": sum(
            j["status"] == claude_judge.JUDGED for j in judgments),
        "claude_rejected": sum(
            j["status"] == claude_judge.REJECTED for j in judgments),
        "claude_not_run": sum(
            j["status"] == claude_judge.NOT_RUN for j in judgments),
    }
    entries = []
    for posting, verdict, judgment in zip(new_postings, verdicts, judgments):
        entries.append({
            "id": posting["id"],
            "title": posting.get("title", ""),
            "absolute_url": posting.get("absolute_url", ""),
            "rule_verdict": {
                "label": "record",
                "verdict": verdict["verdict"],
                "failed_condition": verdict["failed_condition"],
                "justification": verdict["justification"],
                "citations": verdict["citations"],
            },
            "claude_verdict": dict(judgment, label="judgment"),
        })
    return dict(meta, counts=counts, new_postings=entries)


def render_markdown(report):
    c = report["counts"]
    lines = [
        f"# Run report {report['timestamp']}",
        "",
        f"- Run type: **{report['run_type']}**",
        f"- Source: {report['source']}",
        f"- Raw file: `{report['raw_file']}`",
        f"- Raw SHA-256: `{report['raw_sha256']}`",
        f"- State file: `{report['state_file']}`",
        "",
        "## Counts",
        "",
        "| count | value |",
        "| --- | --- |",
        *[f"| {key} | {value} |" for key, value in c.items()],
        "",
    ]
    if report["run_type"] == "baseline":
        lines += ["Baseline run: every current id was recorded; zero postings "
                  "are reported as new.", ""]
    lines += ["## New postings", ""]
    if not report["new_postings"]:
        lines += ["None.", ""]
    for entry in report["new_postings"]:
        rv, cv = entry["rule_verdict"], entry["claude_verdict"]
        lines += [
            f"### {entry['id']}: {' '.join(str(entry['title']).split())}",
            "",
            f"- absolute_url: {entry['absolute_url']}",
            f"- Rule verdict (record): **{rv['verdict']}**",
            *[f"  - {line}" for line in rv["justification"]],
        ]
        if cv["status"] == claude_judge.JUDGED:
            v = cv["verdict"]
            lines += [
                f"- Claude verdict (judgment, not a record): {v['verdict']}",
                f"  - resume_fields: {', '.join(v['resume_fields'])}",
                f"  - posting_fields: {', '.join(v['posting_fields'])}",
                f"  - reason: {' '.join(v['reason'].split())}",
            ]
        elif cv["status"] == claude_judge.REJECTED:
            lines += [f"- Claude verdict (judgment): rejected by validator "
                      f"({cv['error']})"]
        else:
            lines += ["- Claude verdict (judgment): not run"]
        lines.append("")
    return "\n".join(lines)


def assert_no_contact(texts, contact_values):
    """Refuse to write output that contains any résumé contact value."""
    for text in texts:
        lowered = text.lower()
        for value in contact_values:
            if value.lower() in lowered:
                raise RunError("refused: output would contain a résumé "
                               "contact field")


def write_report(report, reports_dir, timestamp, contact_values):
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    md_text = render_markdown(report) + "\n"
    assert_no_contact([json_text, md_text], contact_values)
    json_path = reports_dir / f"{timestamp}.json"
    md_path = reports_dir / f"{timestamp}.md"
    with open(json_path, "x", encoding="utf-8") as handle:
        handle.write(json_text)
    with open(md_path, "x", encoding="utf-8") as handle:
        handle.write(md_text)
    return json_path, md_path


def run(args, claude_runner=None, opener=None, timestamp=None):
    """Execute one run. Returns (report, json_path, md_path)."""
    timestamp = timestamp or utc_timestamp()

    # Inputs are validated before anything is fetched.
    resume = resume_mod.load_resume(args.resume)
    target = resume_mod.load_target(args.target)
    seen = state.load_seen(args.state)

    if args.from_raw:
        raw_path = Path(args.from_raw)
        data = raw_path.read_bytes()
        sha = fetch.sha256_hex(data)
        source, live_type = "saved response (offline)", "seeded"
    else:
        raw_path, sha = fetch.fetch_board(args.board, args.raw_dir, timestamp,
                                          opener=opener)
        data = raw_path.read_bytes()
        source, live_type = f"live fetch of {fetch.board_url(args.board)}", \
            "live"

    postings = parse_postings(data)
    ids = [p["id"] for p in postings]
    new_ids, baseline = state.split_new(ids, seen)
    new_set = set(new_ids)
    new_postings = [p for p in postings if p["id"] in new_set]

    verdicts = rule.evaluate_all(new_postings, resume, target)
    problems = check_verdicts(new_postings, verdicts)
    if problems:
        raise AssertionError("rule verdicts failed the checker:\n  "
                             + "\n  ".join(problems))

    if args.claude:
        judgments = [claude_judge.judge(p, resume, target, runner=claude_runner)
                     for p in new_postings]
    else:
        judgments = [{"status": claude_judge.NOT_RUN} for _ in new_postings]

    meta = {
        "timestamp": timestamp,
        "run_type": "baseline" if baseline else live_type,
        "board": args.board or "scaleai",
        "source": source,
        "raw_file": _display_path(raw_path),
        "raw_sha256": sha,
        "state_file": _display_path(args.state),
        "previously_seen": 0 if seen is None else len(seen),
    }
    report = build_report(meta, postings, new_postings, verdicts, judgments)
    json_path, md_path = write_report(report, args.reports_dir, timestamp,
                                      resume_mod.contact_values(resume))
    # State is saved last, so a failed report never hides postings forever.
    state.save_seen(args.state, (seen or set()) | set(ids), timestamp)
    return report, json_path, md_path


def build_parser():
    parser = argparse.ArgumentParser(prog="python3 -m agent.run",
                                     description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--board", help="board token to fetch live (scaleai)")
    source.add_argument("--from-raw", help="saved raw response to run offline")
    parser.add_argument("--state", type=Path, default=DEFAULTS["state"])
    parser.add_argument("--resume", type=Path, default=DEFAULTS["resume"])
    parser.add_argument("--target", type=Path, default=DEFAULTS["target"])
    parser.add_argument("--raw-dir", type=Path, default=DEFAULTS["raw_dir"])
    parser.add_argument("--reports-dir", type=Path,
                        default=DEFAULTS["reports_dir"])
    parser.add_argument("--claude", action="store_true",
                        help="also run the Claude judge on new postings")
    return parser


def main(argv=None, claude_runner=None, opener=None, timestamp=None):
    args = build_parser().parse_args(argv)
    try:
        if args.board:
            fetch.board_url(args.board)  # refuse a bad board before anything
        report, json_path, md_path = run(args, claude_runner=claude_runner,
                                         opener=opener, timestamp=timestamp)
    except (fetch.FetchRefused, resume_mod.ResumeInvalid,
            resume_mod.TargetInvalid, state.StateInvalid, RunError,
            OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_REFUSED
    except AssertionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_CHECK_FAILED
    c = report["counts"]
    print(f"{report['run_type']} run: {c['postings_in_response']} postings, "
          f"{c['new']} new ({c['rule_relevant']} relevant by rule)")
    print(f"raw: {report['raw_file']} sha256={report['raw_sha256']}")
    print(f"report: {_display_path(md_path)}, {_display_path(json_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
