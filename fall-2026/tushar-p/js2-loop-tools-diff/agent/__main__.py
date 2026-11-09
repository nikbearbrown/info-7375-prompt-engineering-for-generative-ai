"""CLI: python -m agent --config <path> [--out <dir>]

Prints one result line and exits with the F15 code: finished 0, error 2, incomplete 3,
budget-exhausted 4. If the output folder is unavailable, the summary goes to stderr.
"""

import argparse
import json
import sys
import time
from pathlib import Path

from . import loop
from .fsio import DEFAULT_ROOT


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m agent", description="Job-Search Agent 2 (see GATE.md).")
    parser.add_argument("--config", type=Path, required=True, metavar="PATH", help="board config JSON")
    parser.add_argument("--out", type=Path, default=DEFAULT_ROOT, metavar="DIR",
                        help="output folder (default: out/ in the project folder)")
    return parser.parse_args(argv)


def result_line(result: loop.RunResult) -> str:
    boards = result.summary.get("boards", [])
    succeeded = sum(b["status"] == "succeeded" for b in boards)
    failed = sum(b["status"] == "failed" for b in boards)
    pending = len(result.summary.get("pending", []))
    duplicates = len(result.summary.get("duplicates_skipped", []))
    where = f"{result.output_root}/{result.summary_path}" if result.summary_path else "stderr"
    return (f"{result.exit} (exit {result.code}): {succeeded} succeeded, {failed} failed, "
            f"{pending} pending, {duplicates} duplicate(s) skipped; summary: {where}")


def main(argv=None, *, transport=None, clock=time.monotonic, sleep=time.sleep, run_id=None) -> int:
    args = parse_args(argv)
    result = loop.run(args.config, args.out, transport=transport, clock=clock, sleep=sleep, run_id=run_id)
    print(result_line(result))
    if result.message:
        print(f"error: {result.message}", file=sys.stderr)
    if result.summary_path is None:
        print(json.dumps(result.summary, indent=2), file=sys.stderr)
    return result.code


if __name__ == "__main__":
    sys.exit(main())
