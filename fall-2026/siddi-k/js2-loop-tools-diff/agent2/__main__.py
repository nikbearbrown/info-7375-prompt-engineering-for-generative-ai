"""python -m agent2 run --config config/boards.json"""
from __future__ import annotations

import argparse
import sys

from . import loop

EXIT_CODES = {"finished": 0, "incomplete": 1, "budget-exhausted": 2, "error": 3}


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="python -m agent2")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--config", default="config/boards.json")
    a = ap.parse_args(argv)
    try:
        cfg = loop.load_config(a.config)
    except Exception as e:
        print(f"EXIT error: invalid configuration: {type(e).__name__}: {e}")
        return EXIT_CODES["error"]
    s = loop.run(cfg)
    print(f"EXIT {s['exit']}  run {s['run_id']}  requests {s['used']['requests']}/{s['budgets']['requests']}  "
          f"seconds {s['used']['seconds']}/{s['budgets']['seconds']}"
          + (f"  budget reached: {s['budget_reached']}" if s["budget_reached"] else ""))
    for x in s["boards"]:
        print(f"  {x['provider']:15} {x['slug']:12} {x['status']:12} "
              + (f"postings {x['postings']}" if x["status"] == "success" else f"reason {x['reason']} (no count reported)")
              + (f", new since previous run {x['new_since_previous']}" if x.get("new_since_previous") is not None else ""))
    if s["error"]:
        print(f"  error: {s['error']}")
    print(f"  outputs: {s['outputs']['summary']}, {s['outputs']['trace']}")
    return EXIT_CODES[s["exit"]]


if __name__ == "__main__":
    raise SystemExit(main())
