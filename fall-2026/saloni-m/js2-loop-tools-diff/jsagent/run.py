"""Run the watch loop once.

    python3 -m jsagent.run                    # live; new history goes to a pending file
    python3 -m jsagent.run --approve-state    # live; Saloni approves overwriting saved history

Exit code: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error.
"""
import argparse
import datetime as dt
import json
import os
import sys

from jsagent.fetch import make_fetcher
from jsagent.gate import mismatches, read_gate
from jsagent.loop import Loop, empty_state, write_run
from jsagent.policy import Policy

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXIT = {"finished": 0, "incomplete": 1, "budget-exhausted": 2, "error": 3}


def build_policy(cfg, root=HERE):
    out = os.path.join(root, "out")
    return Policy(root, out, cfg["allowed_hosts"],
                  approval_files=[os.path.join(out, "state", "seen_ids.json")])


def print_report(r):
    print(f"run {r['run_id']} [{r['label']}]: {r['status'].upper()}  "
          f"({r['requests_used']} requests, {r['seconds']} s, {r['total_new']} new)")
    for b in r["boards"]:
        counts = (f"seen {b['count_seen']}, new {b['count_new']}" + (" (baseline)" if b["baseline"] else "")
                  if b["result"] == "ok" else "no counts")
        print(f"  {b['system']:<10} {b['board']:<24} {b['result']:<17} {counts:<28} {b['reason']}")
        for n in (b["new"] or [])[:20]:
            print(f"      NEW {n['key']}  {n['title']}")
    sw = r.get("state_written")
    print(f"  state -> {sw}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "config", "run.json"))
    ap.add_argument("--label", default="live")
    ap.add_argument("--approve-state", action="store_true",
                    help="Saloni's approval to overwrite out/state/seen_ids.json")
    args = ap.parse_args(argv)

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{args.label}"
    policy = build_policy(cfg)
    loop = Loop(cfg, policy, make_fetcher(policy), os.path.join(HERE, "out"), run_id, args.label)
    state_path = os.path.join(HERE, "out", "state", "seen_ids.json")

    with open(os.path.join(HERE, "GATE.md"), encoding="utf-8") as f:
        problems = mismatches(cfg, read_gate(f.read()))
    state = empty_state()
    if not problems and os.path.exists(state_path):
        try:
            state = json.loads(policy.read_bytes(state_path))
        except ValueError as e:
            problems = [f"saved state unreadable: {e}"]
    if problems:
        loop.log("start", run_id=run_id, label=args.label)
        loop.log("config_error", problems=problems)
        loop.log("exit", status="error", requests_used=0, total_new=0)
        report = {"run_id": run_id, "label": args.label, "status": "error", "requests_used": 0,
                  "seconds": 0, "total_new": 0, "boards": [], "problems": problems}
        write_run(loop, report, None, state_path)
        print(f"run {run_id}: ERROR before any request: {problems}")
        return EXIT["error"]

    report, new_state = loop.run(state)
    write_run(loop, report, new_state, state_path, approve_state=args.approve_state)
    print_report(report)
    return EXIT[report["status"]]


if __name__ == "__main__":
    sys.exit(main())
