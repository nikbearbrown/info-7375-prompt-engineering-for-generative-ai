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


def load_filter_cfg(path: str) -> dict:
    return json.loads(policy.check_read(path).read_text(encoding="utf-8"))


def run_filter(cfg: dict, run_id: str) -> tuple[list[dict], dict]:
    from . import filter as flt
    postings = collect.load_postings(policy.ROOT / "data" / "collections" / run_id)
    results = [flt.evaluate(cfg, p) for p in postings]
    counts: dict = {}
    for r in results:
        b = counts.setdefault(r["board"], {"keep": 0, "reject": 0, "cannot_tell": 0})
        b[r["verdict"]] += 1
    gate_fail: dict = {}
    for r in results:
        for reason in r["reasons"]:
            gate_fail[reason] = gate_fail.get(reason, 0) + 1
    hist: dict = {}
    for r in results:
        if r["score"] is not None:
            hist[str(r["score"])] = hist.get(str(r["score"]), 0) + 1
    short = flt.shortlist(cfg, results)
    summary = {"filter_version": cfg["version"], "collection_run": run_id, "postings": len(results),
               "verdicts": {v: sum(1 for r in results if r["verdict"] == v) for v in ("keep", "reject", "cannot_tell")},
               "by_board": counts, "reason_counts": dict(sorted(gate_fail.items())),
               "score_histogram_after_gates": dict(sorted(hist.items(), key=lambda kv: int(kv[0]))),
               "shortlist": [{"board": r["board"], "id": r["id"], "title": r["title"], "score": r["score"]}
                             for r in short]}
    return results, summary


def _filter(args) -> int:
    cfg = load_filter_cfg(args.config)
    results, summary = run_filter(cfg, args.run)
    out = policy.ROOT / "output" / "filter" / cfg["version"] / args.run
    policy.write_bytes(out / "results.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n"
                                                      for r in results).encode("utf-8"))
    policy.write_bytes(out / "summary.json", (json.dumps(summary, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"wrote {out.relative_to(policy.ROOT).as_posix()}/results.jsonl and summary.json")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m js3")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("collect", help="collect the three boards with text (FILTER.md §C)").set_defaults(fn=_collect)
    f = sub.add_parser("filter", help="run a filter version over one collection run (FILTER.md A)")
    f.add_argument("--run", required=True, help="collection run id under data/collections/")
    f.add_argument("--config", default="config/filter.v1.json")
    f.set_defaults(fn=_filter)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
