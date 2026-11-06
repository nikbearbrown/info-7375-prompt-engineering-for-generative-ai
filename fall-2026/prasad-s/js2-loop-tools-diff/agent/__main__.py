"""Command line: python3.13 -m agent [--seed evidence/FILE.json] [--report PATH]."""

import argparse
import sys

from .errors import Refusal, RunError
from .replies import CLAUDE_LABEL
from .run import run


def print_summary(report):
    summary = report["summary"]
    print(f"mode: {summary['mode']}")
    print(f"total_fetched: {summary['total_fetched']}")
    print(f"new_count: {summary['new_count']}")
    print(summary["message"])
    for record in report["new_postings"]:
        print(f"- {record['posting_id']}  {record['title']}  [{record['location.name']}]")
        print(f"    rule verdict (record): {record['rule_verdict']}")
        print(f"    {CLAUDE_LABEL}: {record['claude_verdict']}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3.13 -m agent", description="JS1 watch agent (CONTRACT.md v0.3)")
    parser.add_argument("--config", default="config.json", help="config file (default: config.json)")
    parser.add_argument("--seed", metavar="EVIDENCE_FILE",
                        help="seeded run: read a saved board response from evidence/ instead of fetching")
    parser.add_argument("--report", metavar="PATH",
                        help="where to write the run report (default: run_report.json next to the config)")
    args = parser.parse_args(argv)
    try:
        report = run(args.config, seed_path=args.seed, report_path=args.report)
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except RunError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    print_summary(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
