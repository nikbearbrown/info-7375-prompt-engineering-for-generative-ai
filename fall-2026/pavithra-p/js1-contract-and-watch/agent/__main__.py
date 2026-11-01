"""Command line. `python3 -m agent watch` (live), `watch --from-file PATH` (SEEDED), plus the experiment commands."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config, fetch, resume, watch

BASELINE_PROMPT = config.ROOT / "experiment" / "prompts" / "baseline.md"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m agent")
    commands = parser.add_subparsers(dest="command", required=True)
    w = commands.add_parser("watch", help="fetch the board, save the raw response, judge new jobs")
    w.add_argument("--resume", default=str(config.RESUME), help="fictional résumé JSON")
    w.add_argument("--from-file", help="use a saved earlier response instead of fetching; the run is labelled SEEDED")
    w.add_argument("--no-claude", action="store_true", help="skip Claude's opinion (needs Claude Code); the rule still runs")
    s = commands.add_parser("snapshot", help="save one board's raw response for the experiment (no state, no verdicts)")
    s.add_argument("board", choices=config.EXPERIMENT_BOARDS)
    f = commands.add_parser("freeze", help="freeze the 20 postings and the dev/held-out split from saved responses")
    f.add_argument("raw", nargs="+", help="saved raw responses, the Pinterest baseline first")
    f.add_argument("--set", choices=("1", "2"), default="1", help="2 = experiment 2 in experiment-2/")
    commands.add_parser("sample", help="sampling report: 5 dev postings x 4 fresh Claude conversations")
    e = commands.add_parser("experiment", help="ask Claude once per posting with one prompt, on one split")
    e.add_argument("prompt", help="prompt file, e.g. experiment/prompts/baseline.md")
    e.add_argument("--split", choices=("dev", "held-out"), required=True)
    e.add_argument("--set", choices=("1", "2"), default="1", help="1 = experiment/, 2 = experiment-2/")
    commands.add_parser("audit", help="label audit: my labels vs the written rule vs both prompts, from saved replies only")
    a = commands.add_parser("surfaces", help="action surfaces: write the chat text, then let Claude Code read the files")
    a.add_argument("job_id", type=int, help="a job id from a saved Pinterest response")
    args = parser.parse_args(argv)

    if args.command == "surfaces":
        from . import surfaces
        job, raw_path = surfaces.find_job(args.job_id)
        print(f"job {job['id']} ({job['title']}) from {watch.rel(raw_path)}")
        print(f"way 1 (chat): paste {watch.rel(surfaces.chat_way(job, resume.load(config.RESUME)))} into claude.ai")
        print(f"way 2 (file): reply saved to {watch.rel(surfaces.file_way(job, config.RESUME))}")
        return 0

    if args.command == "audit":
        from . import experiments
        text = experiments.audit_table(experiments.audit(resume.load(config.RESUME)))
        path = experiments.EXPERIMENT / "label-audit.md"
        path.write_text(text, encoding="utf-8")
        print(text)
        print(f"(saved to {watch.rel(path)})")
        return 0

    if args.command == "snapshot":
        now = datetime.now(timezone.utc).replace(microsecond=0)
        try:
            raw = fetch.fetch(config.board_url(args.board))
            jobs = watch.parse_jobs(raw)
        except (fetch.RefusedHost, watch.NotAJobList, OSError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        path = watch.save_raw(raw, config.RAW_DIR, now, seeded=False, board=args.board)
        print(f"saved {len(jobs)} jobs from {config.board_url(args.board)} to {watch.rel(path)}")
        return 0

    if args.command == "freeze":
        from . import freeze
        raws = [Path(p).resolve() for p in args.raw]
        if args.set == "2":
            set1 = {p["id"] for p in json.loads((freeze.EXPERIMENT / "postings.json").read_text(encoding="utf-8"))["postings"]}
            frozen = freeze.freeze(raws, out=freeze.EXPERIMENT_2, selection=freeze.SET_2,
                                   pick=lambda lists: freeze.select_set2(lists, exclude=set1))
        else:
            frozen = freeze.freeze(raws)
        for p in frozen["postings"]:
            print(f"{p['split']:9} {p['company']:10} {p['id']}  {p['title']}")
        folder = "experiment-2" if args.set == "2" else "experiment"
        print(f"\nfroze {len(frozen['postings'])} postings at {frozen['frozen_at']}"
              f" -> {folder}/postings.json, {folder}/postings/, {folder}/labels.csv")
        return 0

    if args.command in ("sample", "experiment"):
        from . import experiments
        persona = resume.load(config.RESUME)
        if args.command == "sample":
            rows = experiments.sample(persona, BASELINE_PROMPT)
            text, path = experiments.sampling_table(rows, BASELINE_PROMPT.name), config.CLAUDE_DIR / "sampling" / "table.md"
        else:
            prompt = Path(args.prompt).resolve()
            folder = config.ROOT / ("experiment-2" if args.set == "2" else "experiment")
            rows = experiments.run_prompt(persona, prompt, args.split, experiment=folder)
            text = experiments.results_table(rows, prompt.name, args.split)
            path = config.CLAUDE_DIR / folder.name / f"{prompt.stem}-{args.split}" / "results.md"
        path.write_text(text, encoding="utf-8")
        print(text)
        print(f"(saved to {watch.rel(path)})")
        return 0

    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        persona = resume.load(args.resume)  # refuse a non-fictional résumé before any network call
        if args.from_file:
            raw = Path(args.from_file).read_bytes()
            source = f"saved response `{watch.rel(Path(args.from_file))}` (SEEDED, no fetch)"
            state_path, seeded = config.SEEDED_STATE, True
        else:
            raw = fetch.fetch(config.BOARD_URL)
            source = f"GET {config.BOARD_URL}"
            state_path, seeded = config.STATE, False
        result = watch.run_watch(raw, raw_dir=config.RAW_DIR, state_path=state_path, now=now, seeded=seeded)
    except (fetch.RefusedHost, resume.ResumeRefused) as e:
        print(e, file=sys.stderr)
        return 2
    except (watch.NotAJobList, OSError) as e:
        print(f"error: {e}; the state file was not changed", file=sys.stderr)
        return 1

    suffix = "-SEEDED" if seeded else ""
    judgments = judge_new_jobs(result.new_jobs, persona, args.no_claude, f"{watch.stamp(now)}{suffix}")
    report = watch.format_report(result, source, judgments)
    config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = config.RUNS_DIR / f"run-{watch.stamp(now)}{suffix}.md"
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"(report saved to {watch.rel(report_path)})")
    return 0


def judge_new_jobs(new_jobs, persona, no_claude, run_name):
    """Both judges for each new job: the rule (a record) and Claude (a judgment, saved as it came back)."""
    from . import claude_judge, rule
    judgments = {}
    for job in new_jobs:
        entry = {"rule": rule.judge(job, persona), "claude": None, "claude_file": None}
        if not no_claude:
            try:
                record = claude_judge.judge(job, persona, BASELINE_PROMPT)
            except (OSError, ValueError) as e:  # e.g. Claude Code not installed
                record = {"valid": False, "error": f"Claude not run: {e}", "parsed": None}
            entry["claude"] = record
            entry["claude_file"] = claude_judge.save(record, config.CLAUDE_DIR / "watch" / run_name, str(job["id"]))
        judgments[job["id"]] = entry
    return judgments


if __name__ == "__main__":
    sys.exit(main())
