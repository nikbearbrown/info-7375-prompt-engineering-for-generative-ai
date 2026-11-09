"""CLI: python -m agent --config <path> [--out <dir>] [--fixture <path> [--seed-wrong-empty]]

--fixture runs offline against a saved response (one-board config only, F18).
--seed-wrong-empty (requires --fixture) is the labeled "Finished with the wrong answer" demo.

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
    parser.add_argument("--fixture", type=Path, metavar="PATH",
                        help="offline mode: answer the single configured board with this saved response")
    parser.add_argument("--seed-wrong-empty", action="store_true",
                        help="DELIBERATELY WRONG demo: save the fixture as raw evidence, then count an empty jobs list")
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
    if args.seed_wrong_empty and args.fixture is None:
        print(f"{loop.ERROR} (exit {loop.EXIT_CODES[loop.ERROR]}): --seed-wrong-empty requires --fixture; nothing was run")
        print("error: --seed-wrong-empty requires --fixture", file=sys.stderr)
        return loop.EXIT_CODES[loop.ERROR]
    result = loop.run(args.config, args.out, transport=transport, clock=clock, sleep=sleep, run_id=run_id,
                      fixture_path=args.fixture, seed_wrong_empty=args.seed_wrong_empty)
    print(result_line(result))
    if result.message:
        print(f"error: {result.message}", file=sys.stderr)
    if result.summary_path is None:
        print(json.dumps(result.summary, indent=2), file=sys.stderr)
    return result.code


if __name__ == "__main__":
    sys.exit(main())
