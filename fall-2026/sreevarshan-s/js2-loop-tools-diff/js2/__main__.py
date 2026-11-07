"""Command line: python3 -m js2 [--dry-run | --from-file PATH].

  (no flags)        live run over loop.BOARDS
  --dry-run         print the boards and budget, fetch nothing
  --from-file PATH  replay a saved raw response for one board, no network;
                    the trace is labeled SEEDED. The board is taken from the
                    file name (<stamp>-<ats>-<token>.json) unless --board is set.

Exit code: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error.
"""

import argparse
import os
import re
import sys

from js2 import fetch, independent_check, loop, policy

EXIT_CODES = {"finished": 0, "incomplete": 1, "budget-exhausted": 2, "error": 3}


def board_for_file(path, token=None):
    """Find the BOARDS entry a raw file belongs to."""
    if token is None:
        m = re.match(r"^\d{8}T\d{6,12}Z-(greenhouse|lever)-(.+?)(-SEEDED)?\.json$", os.path.basename(path))
        if not m:
            raise ValueError("cannot tell the board from file name %r; pass --board" % os.path.basename(path))
        token = m.group(2)
    for board in loop.BOARDS:
        if board["token"] == token:
            return board
    raise ValueError("board %r is not in loop.BOARDS" % token)


def print_plan(out):
    print("Boards (GATE.md section 5):", file=out)
    for b in loop.BOARDS:
        print("  %-18s %-10s %s" % (b["name"], b["ats"], loop.URLS[b["ats"]](b["token"])), file=out)
    print("Budget: max_boards=%d max_requests=%d max_seconds=%d"
          % (loop.MAX_BOARDS, loop.MAX_REQUESTS, loop.MAX_SECONDS), file=out)
    print("Allowed hosts: %s" % ", ".join(sorted(policy.ALLOWED_HOSTS)), file=out)
    print("Output dir: %s" % policy.ALLOWED_OUTPUT, file=out)


def print_summary(trace, out):
    label = " [%s]" % trace["label"] if trace.get("label") else ""
    print("Exit status: %s%s (%s)" % (trace["status"], label, trace["stop_reason"]), file=out)
    print("Boards: %d planned, %d checked, %d succeeded, %d failed; %d request(s), %.1fs"
          % (trace["boards_planned"], trace["boards_checked"], trace["boards_succeeded"],
             trace["boards_failed"], trace["requests_used"], trace["elapsed_s"]), file=out)
    for b in trace["boards"]:
        if b["outcome"] == "ok":
            detail = "%d postings%s" % (b["posting_count"], " (reused)" if b.get("reused") else "")
        else:
            detail = b.get("message") or b.get("reason", "")
        print("  %-18s %-12s %s" % (b["board"], b["outcome"], detail), file=out)
    print("Output files:", file=out)
    for b in trace["boards"]:
        if b.get("raw_path") and not b.get("reused"):
            print("  raw:   %s" % b["raw_path"], file=out)
    if trace.get("trace_path"):
        print("  trace: %s" % trace["trace_path"], file=out)
    else:
        print("  trace: NOT WRITTEN (%s)" % trace.get("trace_write_decision"), file=out)


def main(argv=None, out=sys.stdout):
    parser = argparse.ArgumentParser(prog="python3 -m js2", description="Job-Search Agent 2")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print boards and budget, fetch nothing")
    mode.add_argument("--from-file", metavar="PATH", help="replay a saved raw response for one board")
    parser.add_argument("--board", metavar="TOKEN", help="board token for --from-file")
    args = parser.parse_args(argv)
    if args.board and not args.from_file:
        parser.error("--board only applies with --from-file")

    if args.dry_run:
        print_plan(out)
        return 0

    if args.from_file:
        try:
            board = board_for_file(args.from_file, args.board)
        except ValueError as e:
            parser.error(str(e))
        path = args.from_file

        def replay(token, timeout):
            return fetch.replay_from_file(path, board["ats"], token)

        trace = loop.run(boards=[board], fetchers={board["ats"]: replay}, label="SEEDED",
                         notes="SEEDED: replayed from %s, no network request made" % os.path.realpath(path))
    else:
        trace = loop.run()

    print_summary(trace, out)
    if trace.get("trace_path"):
        problems = independent_check.check_trace(trace["trace_path"], os.path.join(policy.ALLOWED_OUTPUT, "raw"))
        print("Independent check: %s" % ("passed" if not problems else "%d discrepancy(ies)" % len(problems)),
              file=out)
        for p in problems:
            print("  %s %s: %s" % (p["board"], p["type"], p["detail"]), file=out)
    return EXIT_CODES[trace["status"]]


if __name__ == "__main__":
    sys.exit(main())
