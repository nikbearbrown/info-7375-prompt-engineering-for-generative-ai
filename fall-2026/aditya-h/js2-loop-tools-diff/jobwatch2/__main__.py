"""CLI: python3 -m jobwatch2 run [--approve-reset BOARD_KEY ...] | reset BOARD_KEY --approve-reset BOARD_KEY"""
import argparse
import json
import pathlib
import sys

from . import loop
from .policy import Policy

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jobwatch2")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="one bounded loop over boards.json")
    r.add_argument("--boards", default="boards.json")
    r.add_argument("--approve-reset", action="append", default=[], help="pre-approve resetting this board")
    s = sub.add_parser("reset", help="delete one board's state (needs your explicit approval)")
    s.add_argument("board")
    s.add_argument("--approve-reset", action="append", default=[])
    a = ap.parse_args(argv)
    if a.cmd == "reset":
        try:
            loop.reset_board(ROOT, a.board, approvals=a.approve_reset)
        except loop.PolicyError as e:
            print(f"refused: {e}", file=sys.stderr)
            return 3
        print(f"state for {a.board} reset")
        return 0
    d = Policy(ROOT).read(a.boards)
    if not d.allowed:
        print(f"refused: {d.reason}", file=sys.stderr)
        return 3
    path = pathlib.Path(a.boards) if pathlib.Path(a.boards).is_absolute() else ROOT / a.boards
    boards = json.loads(path.read_text())["boards"]
    res = loop.run(ROOT, boards, approvals=a.approve_reset)
    print(f"exit: {res['exit']}  budget used: {res['budget_used']}")
    for e in res["boards"]:
        print(f"  {e['key']:<28} {e['status']:<17} http={e['http_status']} attempts={e['attempts']} "
              f"fetched={e['fetched']} new={e['new']} relevant={e['relevant']} {e['reason'] or ''}")
    print(f"trace: {res['trace_path']}\nreport: {res['report_path']}")
    return {"finished": 0, "incomplete": 1, "budget-exhausted": 2, "error": 3}[res["exit"]]


if __name__ == "__main__":
    sys.exit(main())
