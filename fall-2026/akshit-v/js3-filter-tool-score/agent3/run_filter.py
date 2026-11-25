"""Run one filter version over the whole corpus and write the record.

    python -B -m agent3.run_filter --version v1.0
Writes out/filter/<version>/results.json (every posting's score and matches) and summary.txt.
"""
import argparse
import json
import sys
from collections import Counter

from agent3 import corpus, filter as flt, policy


def summarize(c: dict, res: dict, cfg: dict) -> str:
    rs = res["results"]
    lines = [f"# Filter {cfg['version']} over the corpus ({len(rs)} postings)", ""]
    by = Counter((r["board"], r["verdict"]) for r in rs.values())
    boards = sorted({r["board"] for r in rs.values()})
    lines.append(f"{'board':<20} {'keep':>5} {'reject':>7} {'cannot_tell':>12}")
    for b in boards:
        lines.append(f"{b:<20} {by[(b, 'keep')]:>5} {by[(b, 'reject')]:>7} {by[(b, 'cannot_tell')]:>12}")
    tot = Counter(r["verdict"] for r in rs.values())
    lines.append(f"{'total':<20} {tot['keep']:>5} {tot['reject']:>7} {tot['cannot_tell']:>12}")
    for m in c["missing"]:
        lines.append(f"MISSING {m['board']} in run {m['run_id']}: {m['outcome']} -> no data: I cannot tell (A3)")
    disq = sum(1 for r in rs.values() if r["disqualified_by"])
    close = [r for r in rs.values() if flt.is_close_call(r, cfg)]
    lines += ["", f"disqualified (F2/F3): {disq}; rejected on score: {tot['reject'] - disq}",
              f"close calls (score {cfg['threshold'] - cfg['close_band']}..{cfg['threshold'] + cfg['close_band']}, "
              f"not disqualified): {len(close)}",
              "score histogram (not disqualified): "
              + ", ".join(f"{s}:{n}" for s, n in sorted(Counter(r['score'] for r in rs.values()
                                                                 if not r['disqualified_by'] and r['verdict'] != 'cannot_tell').items())),
              "", "## Ranked kept postings (F9)"]
    for pid in res["ranked"]:
        r = rs[pid]
        star = "*" if pid in res["shortlist"] else " "
        listed = "" if c["postings"][pid]["last_seen_run"] == max(s["run_id"] for s in c["sources"]) else "  [no longer listed]"
        lines.append(f"{star}{r['rank']:>3}. {r['score']:>2}  {r['title']}  [{r['board']}]{listed}\n        {r['because']}")
    lines.append("\n(* = shortlist)")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1.0", choices=sorted(flt.VERSIONS))
    args = ap.parse_args(argv)
    cfg = flt.VERSIONS[args.version]
    c = corpus.load()
    res = flt.run(c["postings"].values(), cfg)
    folder = policy.OUT / "filter" / cfg["version"]
    policy.write_bytes(folder / "results.json", (json.dumps(res, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    text = summarize(c, res, cfg)
    policy.write_bytes(folder / "summary.txt", text.encode("utf-8"))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
