"""CLI.

  python -m jsloop run [--demo-failure] [--approve-state-write] [--seeded BOARD=PATH ...] [--json]
  python -m jsloop policy --request METHOD URL [--demo]
  python -m jsloop policy --write PATH [--approve-state-write]
  python -m jsloop policy --read PATH

Paths are relative to the repository root, wherever the command is run from.
"""
import argparse
import json
import pathlib
import sys

from .loop import EXIT_CODES, run_watch
from .policy import DEMO_SELECTION, NORMAL_SELECTION, PolicyDenied, Workspace, check_request

REPO = pathlib.Path(__file__).resolve().parent.parent


def _seeded(pairs):
    seeded = {}
    for pair in pairs or []:
        board, sep, path = pair.partition("=")
        if not sep or not board or not path:
            raise SystemExit(f"--seeded expects BOARD=PATH, got {pair!r}")
        seeded[board] = path
    return seeded


def print_summary(trace):
    print(f"status={trace['status']}  exit={trace['exit_code']}  mode={trace['run_mode']}  "
          f"requests={trace['requests_made']}  elapsed={trace['elapsed_seconds']} s")
    if trace["stop_reason"]:
        print(f"stopped by: {trace['stop_reason']['limit']} budget — {trace['stop_reason']['detail']}")
    if trace["error"]:
        print(f"error: {trace['error']}")
    for b in trace["boards"]:
        label = "  [DELIBERATE FAILURE]" if b.get("deliberate_failure") else ""
        print(f"\n[{b['board']}] {b.get('provider', '?')} {b.get('mode', '')}{label}")
        print(f"  outcome={b['outcome']}  http={b.get('http_status')}  "
              f"postings={b['postings_in_response']}  new={b['new_count']}")
        if b.get("error"):
            print(f"  error: {b['error']}")
        if b.get("reason"):
            print(f"  reason: {b['reason']}")
        if b.get("raw_path") or b.get("raw_note"):
            print(f"  raw: {b.get('raw_path') or b.get('raw_note')}")
        for p in b.get("new_postings", []):
            failed = f" (failed: {', '.join(p['rule_failed_conditions'])})" if p["rule_failed_conditions"] else ""
            print(f"    NEW {p['posting_id']} | {p['title']} | {p['location']} -> RULE {p['rule_verdict']}{failed}")
    print(f"\nstate_updated={trace['state_updated']}  ({trace['state_note']})")
    print(f"trace: {trace['trace_path']}")


def _policy(args):
    ws = Workspace(REPO)
    try:
        if args.request:
            board = check_request(args.request[0].upper(), args.request[1], demo=args.demo)
            print(f"ALLOW request: {board.name} ({board.provider})")
        elif args.write:
            real = ws.check_write(args.write, approve_state_write=args.approve_state_write)
            print(f"ALLOW write: {real}")
        else:
            print(f"ALLOW read: {ws.check_read(args.read)}")
        return 0
    except PolicyDenied as exc:
        print(exc)
        return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="jsloop")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="one bounded watch run over the GATE.md boards")
    run.add_argument("--demo-failure", action="store_true",
                     help="labeled demonstration run: also select the deliberately failing board")
    run.add_argument("--approve-state-write", action="store_true",
                     help="allow this run to update state/js2/ if it finishes cleanly")
    run.add_argument("--seeded", action="append", metavar="BOARD=PATH",
                     help="read this board from a fixtures/js2/ file instead of fetching it (labeled seeded)")
    run.add_argument("--json", action="store_true", help="print the full trace as JSON")

    pol = sub.add_parser("policy", help="ask the permission policy about one action, without doing it")
    which = pol.add_mutually_exclusive_group(required=True)
    which.add_argument("--request", nargs=2, metavar=("METHOD", "URL"))
    which.add_argument("--write", metavar="PATH")
    which.add_argument("--read", metavar="PATH")
    pol.add_argument("--demo", action="store_true")
    pol.add_argument("--approve-state-write", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "policy":
        return _policy(args)

    selection = DEMO_SELECTION if args.demo_failure else NORMAL_SELECTION
    trace = run_watch(selection, base_dir=REPO, demo=args.demo_failure,
                      approve_state_write=args.approve_state_write, seeded=_seeded(args.seeded))
    print_summary(trace)
    if args.json:
        print(json.dumps(trace, indent=2, ensure_ascii=False))
    return trace["exit_code"] if trace["exit_code"] is not None else EXIT_CODES["error"]


if __name__ == "__main__":
    sys.exit(main())
