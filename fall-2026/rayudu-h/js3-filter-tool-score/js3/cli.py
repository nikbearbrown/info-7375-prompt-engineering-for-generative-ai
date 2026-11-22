"""Command line for JS3.

    python -m js3 filter                 # FILTER.md on everything collected -> filter-runs/v<version>/
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys

from . import ROOT, corpus, filterdoc, score


def run_filter(flt: dict = None, c: dict = None) -> tuple:
    flt = flt or filterdoc.load()
    c = c or corpus.load()
    results = [score.score(p, flt) for p in c["postings"].values()]
    latest = corpus.latest_keys(c)
    for r in results:
        r["in_latest_snapshot"] = r["key"] in latest
    return flt, c, sorted(results, key=lambda r: r["key"])


def summarize(flt: dict, c: dict, results: list) -> str:
    boards = sorted({r["board"] for r in results})
    table = collections.Counter((r["board"], r["decision"]) for r in results)
    by_rule = collections.Counter((r["decision"], r["decided_by"]) for r in results)
    lines = [f"# Filter run: FILTER.md v{flt['filter_version']}", "",
             f"- FILTER.md sha256: `{flt['filter_sha256']}`",
             f"- Corpus: {len(results)} unique postings from {len(c['snapshots'])} live snapshots "
             f"({', '.join(s['id'] for s in c['snapshots'])}); latest version of each posting used",
             f"- Run at: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}", "",
             "| board | kept | rejected | cannot tell | total |", "|---|---:|---:|---:|---:|"]
    for b in boards:
        k, r_, ct = (table[(b, d)] for d in (score.KEPT, score.REJECTED, score.CANNOT_TELL))
        lines.append(f"| {b} | {k} | {r_} | {ct} | {k + r_ + ct} |")
    tot = collections.Counter(r["decision"] for r in results)
    lines += [f"| **all** | **{tot[score.KEPT]}** | **{tot[score.REJECTED]}** | **{tot[score.CANNOT_TELL]}** | "
              f"**{len(results)}** |", "", "**Which rule decided:**", "",
              "| decision | rule | postings |", "|---|---|---:|"]
    for (d, rule), n in sorted(by_rule.items(), key=lambda x: (x[0][0], x[0][1])):
        lines.append(f"| {d} | {rule} | {n} |")
    missing = [(s["id"], b["board"], b["reason"]) for s in c["snapshots"] for b in s["boards_without_result"]]
    lines += ["", "**Boards with no result** (FILTER.md section 4: \"no result\", never \"nothing relevant\"):", ""]
    lines += [f"- {sid}: `{b}`: no result ({reason})" for sid, b, reason in missing] or ["- none"]
    kept_latest = sum(1 for r in results if r["decision"] == score.KEPT and r["in_latest_snapshot"])
    lines += ["", f"Kept postings still listed in the latest snapshot ({c['latest']}): {kept_latest}."]
    return "\n".join(lines) + "\n"


def cmd_filter(a) -> int:
    flt, c, results = run_filter()
    out = ROOT / "filter-runs" / f"v{flt['filter_version']}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    summary = summarize(flt, c, results)
    (out / "summary.md").write_text(summary)
    print(summary)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m js3")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("filter", help="run FILTER.md on everything collected").set_defaults(fn=cmd_filter)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
