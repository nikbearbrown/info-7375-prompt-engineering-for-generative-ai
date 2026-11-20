"""Command line for the JS2 agent.

    python3 agent.py run [--config config/boards.json] [--state state/seen.json] [--label NAME]
    python3 agent.py reset-state [--state state/seen.json]    asks for approval
    python3 agent.py delete-run runs/FOLDER                   asks for approval

Exit codes: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error.
"""
import argparse
import json
import sys

import loop
from policy import Policy, PolicyViolation
from tools import Tools


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p_run = sub.add_parser("run", help="watch the configured boards once")
    p_run.add_argument("--config", default="config/boards.json")
    p_run.add_argument("--state", default="state/seen.json")
    p_run.add_argument("--label", help="added to the run folder name, for example SIMULATED-timeout")
    p_reset = sub.add_parser("reset-state", help="empty a state file (needs approval)")
    p_reset.add_argument("--state", default="state/seen.json")
    p_del = sub.add_parser("delete-run", help="delete one run folder (needs approval)")
    p_del.add_argument("run_dir")
    args = parser.parse_args(argv)
    tools = Tools(Policy())
    try:
        if args.command == "run":
            run_dir, s = loop.run(tools, args.config, args.state, args.label)
            print(f"{s['exit']}: {s['requests']} requests, {s['seconds']} s -> {run_dir}/report.md"
                  + (f"\n  reason: {s['reason']}" if s["reason"] else ""))
            for key, r in s["results"].items():
                detail = (f"{r['count']} postings, {len(r['new'])} new, {len(r['closed'])} closed"
                          + (" (baseline)" if r["baseline"] else "")) if r["status"] == "ok" else r["reason"]
                print(f"  {key}: {r['status']}: {detail}")
            for key in s["unvisited"]:
                print(f"  {key}: not visited")
            return loop.EXIT_CODES[s["exit"]]
        if args.command == "reset-state":
            old = loop.load_json(tools, args.state, missing=None)
            empty = {"board_list": None, "boards": {}}
            tools.policy.check_state_update(old, empty)
            tools.write_text(args.state, json.dumps(empty, indent=2) + "\n", overwrite=True)
            print(f"reset {args.state}")
            return 0
        tools.delete_run(args.run_dir)
        print(f"deleted {args.run_dir}")
        return 0
    except PolicyViolation as e:
        print(f"error: {e}", file=sys.stderr)
        return loop.EXIT_CODES["error"]


if __name__ == "__main__":
    sys.exit(main())
