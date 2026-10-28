"""Command line: python3 -m jobwatch run|rule ... (see README.md for the exact commands)."""

import argparse
import json
import sys
from pathlib import Path

from jobwatch import board, net, rule, transports
from jobwatch.errors import AgentError, InputError
from jobwatch.resume import validate_resume
from jobwatch.run import run_once


def read_resume(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise InputError("résumé file could not be read as JSON") from None


def replay(path):
    """A saved earlier response, served as if fetched. Runs that use it are labelled seeded."""
    def fetch():
        return net.FetchResult(Path(path).read_bytes(), net.BOARD_URL, 200, "application/json (saved file)", net.utc_now())
    return fetch


def cmd_run(args):
    seeded = args.from_file is not None
    summary = run_once(
        fetch=replay(args.from_file) if seeded else net.fetch_board,
        resume=read_resume(args.resume),
        state_path=args.state,
        out_dir=args.out,
        send=transports.get(args.judge, args.model),
        mode="seeded" if seeded else "live",
        source=f"saved earlier response {args.from_file}" if seeded else "live GET of the board endpoint",
    )
    kind = "SEEDED replay" if seeded else "live fetch"
    first = "baseline (first run): 0 reported as new" if summary["baseline"] else f"{len(summary['new_ids'])} new since last run"
    print(f"{summary['run_id']}: {kind}, {summary['posting_count']} postings, {first}")
    for a in summary["assessments"]:
        print(f"  {a['posting_id']} {a['title']} | rule (record): {a['rule_verdict']['verdict']} "
              f"| Claude (model judgment): {a['claude_verdict']['verdict']}"
              f"{'' if a['verdicts_agree'] else ' | DISAGREE'}")
    print(f"  evidence: {summary['run_dir']}")


def cmd_rule(args):
    resume = validate_resume(read_resume(args.resume))
    postings = {p.id: p for p in board.parse_board(Path(args.raw).read_bytes())}
    if args.id not in postings:
        raise InputError(f"posting {args.id} is not in {args.raw}")
    print(json.dumps(rule.rule_verdict(resume, postings[args.id]), indent=2, ensure_ascii=False))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch",
                                     description="Job-Search Agent 1: one board, one fictional résumé, new postings only.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="fetch the board (or replay a saved response) and report new postings")
    run.add_argument("--resume", required=True, help="fictional persona résumé (JSON)")
    run.add_argument("--state", required=True, type=Path, help="state file of seen posting ids")
    run.add_argument("--out", required=True, type=Path, help="directory for run evidence")
    run.add_argument("--from-file", type=Path, help="replay a saved earlier response; the run is labelled SEEDED")
    run.add_argument("--judge", choices=transports.CHOICES, default=transports.DEFAULT, help="how Claude is reached")
    run.add_argument("--model", default=transports.DEFAULT_MODEL, help="Claude model id")
    run.set_defaults(func=cmd_run)

    recompute = sub.add_parser("rule", help="recompute the rule record for one posting in a saved response")
    recompute.add_argument("--resume", required=True)
    recompute.add_argument("--raw", required=True, type=Path)
    recompute.add_argument("--id", required=True, type=int)
    recompute.set_defaults(func=cmd_rule)

    args = parser.parse_args(argv)
    try:
        args.func(args)
    except AgentError as error:
        print(f"error ({type(error).__name__}): {error}", file=sys.stderr)
        print("state file unchanged", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
