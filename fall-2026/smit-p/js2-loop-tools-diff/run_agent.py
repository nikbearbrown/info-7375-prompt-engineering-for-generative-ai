"""Run the watch loop once.

    python3 run_agent.py                                  # live run against config/boards.json
    python3 run_agent.py --replay fixtures/<scenario>.json --run-id seeded-<name>

A replay run serves saved responses instead of calling the network. Its run id must start
with "seeded-" and every trace line and the summary are marked seeded.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from agent import fetch, loop, policy

BASE = os.path.dirname(os.path.abspath(__file__))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--boards", default="config/boards.json")
    ap.add_argument("--budgets", default="config/budgets.json")
    ap.add_argument("--replay", help="scenario file of saved responses (seeded run)")
    ap.add_argument("--run-id")
    args = ap.parse_args(argv)

    boards = json.loads(policy.guarded_read(BASE, args.boards))
    budgets = json.loads(policy.guarded_read(BASE, args.budgets))

    if args.replay:
        run_id = args.run_id or "seeded-" + _stamp()
        if not run_id.startswith("seeded-"):
            ap.error("a replay run id must start with 'seeded-'")
        transport = fetch.ReplayTransport(BASE, args.replay)
    else:
        run_id = args.run_id or _stamp()
        if run_id.startswith("seeded-"):
            ap.error("'seeded-' is reserved for replay runs")
        transport = fetch.LiveTransport()
    if os.path.exists(os.path.join(BASE, "jobs", "runs", run_id)):
        ap.error(f"run {run_id} already exists; runs are never overwritten")

    fetcher = fetch.GuardedFetcher(transport, min_gap_s=budgets.get("min_gap_per_host_s", 1.0))
    summary = loop.run(BASE, boards, budgets, fetcher, run_id, seeded=transport.seeded)
    print_report(summary)
    return summary["exit_code"]


def print_report(s):
    label = "SEEDED (replayed saved responses, not a live run)" if s["seeded"] else "LIVE"
    print(f"run {s['run_id']}  [{label}]  requests={s['requests']}  elapsed={s['elapsed_s']}s")
    for b in s["boards"]:
        count = "null" if b["count"] is None else b["count"]
        line = f"  {b['name']:<22} {b['ats']:<10} {b['status']:<26} count={count}"
        if b.get("baseline"):
            line += "  (baseline: nothing reported as new)"
        elif "new" in b:
            line += f"  new={len(b['new'])}"
        print(line)
        for p in b.get("new", [])[:10]:
            print(f"      + {p['id']}  {p['title']}")
    for item in s["needs_human"]:
        print(f"  NEEDS HUMAN: {item}")
    print(f"exit: {s['exit']} (code {s['exit_code']})")


def _stamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


if __name__ == "__main__":
    sys.exit(main())
