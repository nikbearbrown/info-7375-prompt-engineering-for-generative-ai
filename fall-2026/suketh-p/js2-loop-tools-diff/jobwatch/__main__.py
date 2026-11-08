"""Command line. Run every command from the js2-loop-tools-diff folder (README.md).

  python3 -m jobwatch run --run-id ID [--failure-control] [--approve-state ID:state/state.json]
  python3 -m jobwatch verify runs/ID
  python3 -m jobwatch boards

Exit codes: 0 finished, 1 error, 3 incomplete, 4 budget-exhausted; 2 is a usage error."""

import argparse
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

from jobwatch import boards, loop, net
from jobwatch.errors import PolicyDenied
from jobwatch.files import Files
from jobwatch.policy import Approval, Policy

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXIT_CODES = {"finished": 0, "error": 1, "incomplete": 3, "budget-exhausted": 4}


def _approval(text):
    try:
        return Approval.parse(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from None


def _parser():
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch",
                                     description="Job-Search Agent 2: a bounded watch over three job boards.")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="one bounded run over the configured boards")
    run.add_argument("--run-id", required=True, help="a new name for this run's folder under runs/")
    run.add_argument("--failure-control", action="store_true",
                     help="add the board that should answer 404 (the deliberate failure)")
    run.add_argument("--approve-state", type=_approval, metavar="RUN_ID:state/state.json",
                     help="your approval, given before the run starts, to replace state/state.json in this run")
    verify = commands.add_parser("verify", help="recheck each saved raw body against the sha256 in its trace")
    verify.add_argument("run_dir", help="for example runs/2026-11-08-normal-1")
    commands.add_parser("boards", help="list the configured boards and their endpoints")
    return parser


def main(argv=None, *, root=None, fetch=None, clock=None, wall=None):
    args = _parser().parse_args(argv)
    root = Path(root) if root is not None else PROJECT_ROOT
    if args.command == "boards":
        for board in boards.CONFIGURED:
            print(f"{board.name:40} {board.role:16} GET {board.url}")
        return 0
    if args.command == "verify":
        return _verify(root, args.run_dir)
    requested = list(boards.FAILURE_RUN if args.failure_control else boards.NORMAL_RUN)
    result = loop.run(root=root, run_id=args.run_id, requested=requested, approval=args.approve_state,
                      fetch=fetch or net.https_get, clock=clock or time.monotonic, wall=wall or loop.utc_now)
    print(f"run {result['run_id']}: {result['status']} — {result['reason']}")
    for row in result["boards"]:
        jobs = "unknown" if row["jobs"] is None else row["jobs"]
        new = "" if row["new_keys"] is None else (" baseline" if row["baseline"] else f" new={len(row['new_keys'])}")
        why = f" ({row['reason']})" if row["reason"] else ""
        print(f"  {row['board']:40} {row['outcome']:22} jobs={jobs}{new}{why}")
    used = result["used"]
    print(f"  used {used['boards']} boards, {used['requests']} requests, {used['seconds']} s; "
          f"state advanced: {result['state_advanced']}")
    if result["status"] != "error" or (root / "runs" / result["run_id"]).exists():
        print(f"  evidence: runs/{result['run_id']}/ (results.md, trace.md, raw/)")
    return EXIT_CODES[result["status"]]


def _verify(root, run_dir):
    files = Files(Policy(root, None, set(), None))
    try:
        trace = json.loads(files.read_bytes(f"{run_dir}/trace.json").decode("utf-8"))
    except (OSError, ValueError, PolicyDenied) as error:
        print(f"cannot read {run_dir}/trace.json: {error}")
        return 1
    problems = 0
    for event in trace["events"]:
        if event.get("event") != "request" or not event.get("raw"):
            continue
        body = gzip.decompress(files.read_bytes(f"{run_dir}/{event['raw']}"))
        ok = hashlib.sha256(body).hexdigest() == event["sha256"]
        problems += not ok
        print(f"{'OK      ' if ok else 'MISMATCH'} {event['raw']}  {len(body)} bytes  sha256 {event['sha256']}")
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
