"""Command line: python -m js3 <command>. Each command prints what it wrote."""
from __future__ import annotations

import argparse
import json
import sys

from . import collect, policy


def _collect(args) -> int:
    cfg = json.loads(policy.check_read("config/sources.json").read_text(encoding="utf-8"))
    summary = collect.collect(cfg, policy.ROOT / "data" / "collections")
    print(json.dumps({k: summary[k] for k in ("run_id", "exit", "requests_used", "seconds_used",
                                               "postings_total", "boards")}, indent=2))
    return {"finished": 0, "incomplete": 1, "budget-exhausted": 2}.get(summary["exit"], 3)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m js3")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("collect", help="collect the three boards with text (FILTER.md §C)").set_defaults(fn=_collect)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
