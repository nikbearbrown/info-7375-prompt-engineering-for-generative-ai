"""SEEDED demonstration: a run that ends cleanly and is wrong, and the independent check that catches it.

No network. It replays the raw responses saved by a real run (default: evidence/run-live-1) in a sandbox
folder (out/demo-root/), with ONE change: Figma's response is replaced by a CONSTRUCTED empty board
{"jobs": [], "meta": {"total": 0}}, as if Figma's API had briefly returned nothing.

    A  replay of the real run                     -> baseline (sandbox state written; sandbox only)
    B  same, Figma empty, WRONG VERSION 1 swapped in (empty board treated as "ok")
                                                  -> exit "finished", Figma "0 new"  <- finished wrong answer
    C  check.py on B, with A as the previous run  -> flags it
    D  same input as B, the REAL agent            -> exit "incomplete", Figma "empty-unverified"

    python3 demo_wrong_answer.py [--from evidence/run-live-1]
"""

import argparse
import gzip
import json
import shutil
from pathlib import Path
from unittest import mock

from jsagent2 import loop as loop_mod
from jsagent2.check import check_run
from jsagent2.loop import run_loop
from jsagent2.policy import Policy

ROOT = Path(__file__).resolve().parent
EMPTY = b'{"jobs": [], "meta": {"total": 0}}'  # CONSTRUCTED, not a real Figma response


def wrong_empty_as_zero(status, body, ats):
    """GATE.md section 6, wrong version 1 (same as tests/test_wrong_versions.empty_as_zero)."""
    s, jobs = REAL_CLASSIFY(status, body, ats)
    return ("ok", jobs) if s == "empty-unverified" else (s, jobs)


REAL_CLASSIFY = loop_mod.classify


def replay_transport(src_root, trace, empty_board=None):
    """Serve the saved raw bytes per URL (last response per board), optionally emptying one board."""
    by_url = {}
    for o in trace["observations"]:
        if o.get("event") == "response":
            body = gzip.decompress((src_root / o["raw_file"]).read_bytes())
            if o["board"] == empty_board:
                body = EMPTY
            by_url[o["url"]] = (o["http_status"], body)

    def transport(url, timeout):
        return by_url[url]

    return transport


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default="evidence/run-live-1")
    a = ap.parse_args(argv)
    src = ROOT / a.src
    trace = json.loads((src / "trace.json").read_text())
    # raw_file paths in the trace are relative to the folder that held out/; evidence copies keep that layout
    src_root = src / "root"

    sandbox = ROOT / "out" / "demo-root"
    shutil.rmtree(sandbox, ignore_errors=True)
    (sandbox / "out").mkdir(parents=True)
    boards = json.loads((ROOT / "config/boards.json").read_text())["boards"]
    boards = [b for b in boards if any(o.get("board") == b["name"] and o.get("event") == "response" and o["http_status"] == 200
                                       for o in trace["observations"])]
    budgets = json.loads((ROOT / "config/budgets.json").read_text())
    policy = Policy(sandbox, approve_state_write=True)  # sandbox state only, never my real out/state

    print("SEEDED DEMONSTRATION — replayed raw responses; Figma's B/D response is constructed (empty).\n")
    a_res = run_loop(boards, budgets, policy, replay_transport(src_root, trace), run_id="A-replay")
    print(f"A replay of {a.src}: exit={a_res.exit}  " + ", ".join(f"{k}={v['postings']}" for k, v in a_res.boards.items()))

    with mock.patch.object(loop_mod, "classify", wrong_empty_as_zero):
        b_res = run_loop(boards, budgets, policy, replay_transport(src_root, trace, "Figma"), run_id="B-wrong-version")
    print(f"\nB WRONG VERSION, Figma empty: exit={b_res.exit}")
    for k, v in b_res.boards.items():
        print(f"   {k}: status={v['status']} postings={v['postings']} new={len(v['new']) if v['new'] is not None else v['new']}")
    print("   ^ the agent's own report: finished, Figma 0 new. Clean, and wrong.")

    findings = check_run(sandbox, sandbox / "out/runs/B-wrong-version/trace.json",
                         previous=[sandbox / "out/runs/A-replay/trace.json"])
    print(f"\nC independent check (check.py) on B, previous=A: {len(findings)} finding(s)")
    for f in findings:
        print(f"   [{f['kind']}] {f['board']}: {f['detail']}")

    policy_d = Policy(sandbox, approve_state_write=False)  # do not move the sandbox baseline
    d_res = run_loop(boards, budgets, policy_d, replay_transport(src_root, trace, "Figma"), run_id="D-real-agent")
    print(f"\nD REAL AGENT, same input as B: exit={d_res.exit}  Figma status={d_res.boards['Figma']['status']}"
          f" new={d_res.boards['Figma']['new']}")
    print(f"\nsandbox: {sandbox.relative_to(ROOT)}/out/runs/")
    return 0 if findings and d_res.exit != "finished" else 1


if __name__ == "__main__":
    raise SystemExit(main())
