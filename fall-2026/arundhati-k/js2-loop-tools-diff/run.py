"""Run the loop once against the live boards in config/boards.json.

    python3 run.py                         # live run; state write is HELD (needs approval)
    python3 run.py --approve-state-write   # live run; writes out/state/seen.json
"""

import argparse
import json
import sys
from pathlib import Path

from jsagent2.loop import run_loop
from jsagent2.policy import Policy
from jsagent2.transport import make_transport

ROOT = Path(__file__).resolve().parent


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--approve-state-write", action="store_true", help="allow writing out/state/seen.json")
    ap.add_argument("--run-id")
    args = ap.parse_args(argv)

    policy = Policy(ROOT, approve_state_write=args.approve_state_write)
    boards = json.loads(policy.read_bytes("config/boards.json"))["boards"]
    budgets = json.loads(policy.read_bytes("config/budgets.json"))
    res = run_loop(boards, budgets, policy, make_transport(policy), run_id=args.run_id)
    print((ROOT / res.trace_file).with_name("report.md").read_text())
    print(f"trace: {res.trace_file}")
    return 0 if res.exit == "finished" else 1


if __name__ == "__main__":
    sys.exit(main())
