"""Command line: `run` (the loop) and `approve` (the one write that needs Mayank).

Exit codes: 0 nothing needs Mayank · 3 a board needs Mayank (GATE §4, 4b-B) · 2 run-level error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from . import loop, net, policy

ROOT = Path(__file__).resolve().parents[2]  # the js2-loop-tools-diff folder


def _load(rel):
    return json.loads(policy.read_text(ROOT, rel))


def _replay_fetch(mapping: dict):
    """SEEDED mode: serve saved bytes instead of the network. Labeled in the run id and report."""
    from . import boards
    files = {boards.board_url(*k.split("/", 1)): v for k, v in mapping["responses"].items()}

    def fetch(url, timeout):
        policy.check_url(url)
        if url not in files:
            raise net.NetError(f"seeded run has no response for {url}")
        f = files[url]
        return f["status"], policy.authorize(ROOT, f["file"], "read").read_bytes()
    return fetch


def cmd_run(a) -> int:
    run_id = a.run_id or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ") + (f"-{a.label}" if a.label else "")
    try:
        plan = _load(a.plan)["plan"]
        budget = _load("config/budgets.json")
        persona = _load(a.persona)
        try:
            seen = _load("state/seen-ids.json")
        except FileNotFoundError:
            seen = {}
        fetch = net.fetch
        if a.replay:
            fetch = _replay_fetch(_load(a.replay))
        s = loop.run(str(ROOT), run_id, plan, budget, persona, seen, fetch=fetch)
        if a.replay:  # label the seeded run inside its own report, first line
            rep = ROOT / f"runs/{run_id}/report.md"
            policy.write_text(ROOT, f"runs/{run_id}/report.md",
                              f"SEEDED RUN (no network): every response replayed from files listed in {a.replay}\n" + rep.read_text(), run_id=run_id)
    except (loop.RunError, policy.PolicyError, json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        msg = f"run-level error: {e}"
        try:
            policy.write_text(ROOT, f"runs/{run_id}/report.json", json.dumps({"run_id": run_id, "exit": "error", "reason": str(e)}, indent=1), run_id=run_id)
        except policy.PolicyError:
            pass
        print(f"exit: error\n{msg}\nstate/ not touched", file=sys.stderr)
        return 2
    print(open(ROOT / f"runs/{run_id}/report.md").read())
    print(f"run folder: runs/{run_id}/   next: python3 checker/check.py runs/{run_id} --plan {a.plan}")
    return 3 if s["needs_mayank"] else 0


def cmd_approve(a) -> int:
    rid = a.run_id
    try:
        check = _load(f"runs/{rid}/check.json")
    except FileNotFoundError:
        print(f"refused: run the independent checker first (runs/{rid}/check.json is missing)", file=sys.stderr)
        return 2
    report = _load(f"runs/{rid}/report.json")
    proposed = _load(f"runs/{rid}/proposed-seen-ids.json")
    try:
        current = _load("state/seen-ids.json")
    except FileNotFoundError:
        current = {}
    flagged = set(report.get("needs_mayank", [])) | {b for b, v in check["boards"].items() if v["verdict"] != "ok"}
    acked = {x.casefold() for x in a.ack}
    new_state, held = dict(current), []
    for board, ids in proposed.items():
        if board in flagged and board not in acked:
            held.append(board)
            continue
        new_state[board] = ids
    try:
        policy.write_text(ROOT, "state/seen-ids.json", json.dumps(new_state, indent=1, sort_keys=True),
                          run_id=rid, approval=a.approve_state)
    except policy.PolicyError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    log = {"run_id": rid, "approved_with": a.approve_state, "acked": sorted(acked), "held": sorted(held),
           "applied": sorted(b for b in proposed if b not in held),
           "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    policy.write_text(ROOT, f"runs/{rid}/approval.json", json.dumps(log, indent=1), run_id=rid)
    print(json.dumps(log, indent=1))
    return 3 if held else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="agent.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--plan", default="config/boards.json")
    r.add_argument("--persona", default="persona/priya-nair.resume.json")
    r.add_argument("--run-id")
    r.add_argument("--label", help="suffix for the run id, e.g. finished-wrong")
    r.add_argument("--replay", help="SEEDED run: config/replay/<file>.json mapping boards to saved responses (no network)")
    ap = sub.add_parser("approve")
    ap.add_argument("run_id")
    ap.add_argument("--approve-state", required=True, help="must equal the run id exactly")
    ap.add_argument("--ack", action="append", default=[], help="<ats>/<slug> of a flagged board to release")
    a = p.parse_args(argv)
    return cmd_run(a) if a.cmd == "run" else cmd_approve(a)
