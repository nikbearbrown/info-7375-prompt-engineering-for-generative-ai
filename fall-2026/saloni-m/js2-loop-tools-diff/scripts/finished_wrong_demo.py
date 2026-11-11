"""SIMULATED demonstration: a run that ends cleanly ("finished") and is wrong.

Inputs are the REAL raw responses saved by a live run (default: live run 1). Only one thing is
simulated: figma's response is replaced by a valid but empty body {"jobs": []}, as if the board
had silently returned nothing. The deliberate-404 board is left out so a run *can* finish.

  step 1  baseline replay of the real responses (correct loop)      -> state_before
  step 2  wrong version 1 (GATE 6.1) on the emptied figma response   -> "finished, 0 new"  (wrong)
  step 3  the independent check (scripts/independent_check.py) on step 2's report -> CONTRADICTED
  step 4  the real loop on the same input                             -> "incomplete", suspicious_empty

    python3 scripts/finished_wrong_demo.py [--from-run out/runs/<id>] [--live-check]
"""
import argparse
import glob
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from jsagent.fetch import FetchResult  # noqa: E402
from jsagent.loop import Loop, empty_state, write_run  # noqa: E402
from jsagent.providers import PROVIDERS  # noqa: E402
from jsagent.run import build_policy  # noqa: E402
from tests.wrong_versions import WV1EmptyIsSuccess  # noqa: E402
import independent_check  # noqa: E402

EMPTY = b'{"jobs": []}'


def replay(run_dir, boards, empty_board=None):
    table = {}
    for b in boards:
        url = PROVIDERS[b["system"]].url(b["board"])
        if f"{b['system']}:{b['board']}" == empty_board:
            table[url] = FetchResult(200, EMPTY, None)  # SIMULATED
            continue
        [path] = glob.glob(os.path.join(run_dir, "raw", f"{b['system']}-{b['board']}-a*.json.gz"))[-1:]
        with open(path, "rb") as f:
            table[url] = FetchResult(200, gzip.decompress(f.read()), None)
    return lambda url, timeout: table[url]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-run", default=sorted(glob.glob(os.path.join(HERE, "out", "runs", "*-live")))[0])
    ap.add_argument("--empty", default="greenhouse:figma")
    ap.add_argument("--live-check", action="store_true", help="independent check also re-counts live")
    a = ap.parse_args(argv)

    with open(os.path.join(HERE, "config", "run.json")) as f:
        cfg = json.load(f)
    cfg = dict(cfg, boards=[b for b in cfg["boards"] if "deliberate_failure" not in b])
    pol = build_policy(cfg)
    demo = os.path.join(HERE, "out", "demo", "finished-wrong")
    src = os.path.relpath(a.from_run, HERE)
    print(f"SIMULATED demo. Real raw responses from {src}; {a.empty} replaced by {EMPTY.decode()}\n")

    base = Loop(cfg, pol, replay(a.from_run, cfg["boards"]), demo, "1-baseline-replay", "SIMULATED-replay")
    r1, s1 = base.run(empty_state())
    write_run(base, r1, s1, os.path.join(demo, "state_before.json"))
    print(f"step 1 baseline replay (correct loop): {r1['status']}, counts "
          f"{ {b['board']: b['count_seen'] for b in r1['boards']} }")

    wrong = WV1EmptyIsSuccess(cfg, pol, replay(a.from_run, cfg["boards"], a.empty), demo,
                              "2-wrong-version-1", "SIMULATED-empty-figma")
    r2, s2 = wrong.run(s1)
    write_run(wrong, r2, s2, os.path.join(demo, "state_after_wrong.json"))
    print(f"step 2 WRONG VERSION 1 report: {r2['status'].upper()}, {r2['total_new']} new, "
          f"figma count {[b['count_seen'] for b in r2['boards'] if b['board'] == 'figma'][0]}")

    chk = independent_check.check(r2, s1, live=a.live_check, policy=pol)
    pol.write_bytes(os.path.join(demo, "3-independent-check.json"), json.dumps(chk, indent=1).encode())
    fig = [r for r in chk["boards"] if r["board"] == a.empty][0]
    print(f"step 3 independent check: overall {chk['overall']}; {a.empty}: {fig['verdict']} {fig.get('why', '')}")

    right = Loop(cfg, pol, replay(a.from_run, cfg["boards"], a.empty), demo, "4-correct-loop", "SIMULATED-empty-figma")
    r4, s4 = right.run(s1)
    write_run(right, r4, s4, os.path.join(demo, "state_after_correct.json"))
    fb = [b for b in r4["boards"] if b["board"] == "figma"][0]
    print(f"step 4 correct loop: {r4['status'].upper()}; figma {fb['result']} ({fb['reason']}); "
          f"figma history kept: {s4['boards']['greenhouse:figma'] == s1['boards']['greenhouse:figma']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
