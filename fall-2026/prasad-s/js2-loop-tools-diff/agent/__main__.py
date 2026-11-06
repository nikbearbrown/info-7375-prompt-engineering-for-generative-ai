"""Command line: python3.13 -m agent [--config config.json] [--seed BOARD_KEY=PATH ...] [--approve PATH ...]."""

import argparse
import sys

from .replies import CLAUDE_LABEL
from .run import run

# Decision 2026-11-06: one exit code per GATE.md §1 exit; "finished — with failures" is still 0.
EXIT_CODES = {"finished": 0, "error": 1, "refused": 2, "incomplete": 3, "budget-exhausted": 4}


def seed_arg(text):
    key, sep, path = text.partition("=")
    if not sep or not key or not path:
        raise argparse.ArgumentTypeError(f"{text!r} is not BOARD_KEY=PATH, e.g. greenhouse:stripe=evidence/snapshots/x.json")
    return key, path


def print_summary(report):
    print(report["exit"]["line"])
    for line in report["boards"]:
        print(f"- {line['board']} [{line['mode']}]: {line['line']}")
        for record in line.get("new_postings", []):
            print(f"    {record['posting_id']}  {record['title']}  [{record['location.name']}]")
            print(f"        rule verdict (record): {record['rule_verdict']}")
            print(f"        {CLAUDE_LABEL}: {record['claude_line']}")
    if report.get("report_file"):
        print(f"report: {report['report_file']}")
    for key in ("report_error", "state_error"):
        if report.get(key):
            print(f"{key}: {report[key]}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3.13 -m agent", description="JS2 loop (GATE.md v0.2, CONTRACT.md v0.6)")
    parser.add_argument("--config", default="config.json", help="config file (default: config.json)")
    parser.add_argument("--seed", type=seed_arg, action="append", default=[], metavar="BOARD_KEY=PATH",
                        help="read this board from a saved response under evidence/ instead of fetching it (repeatable)")
    parser.add_argument("--approve", action="append", default=[], metavar="PATH",
                        help="approve one write to this exact path on this run (GATE.md §5; repeatable)")
    args = parser.parse_args(argv)
    seeds = {}
    for key, path in args.seed:
        if key in seeds:
            parser.error(f"--seed names {key} twice")
        seeds[key] = path
    report = run(args.config, seeds=seeds, approvals=args.approve)
    print_summary(report)
    return EXIT_CODES[report["exit"]["kind"]]


if __name__ == "__main__":
    sys.exit(main())
