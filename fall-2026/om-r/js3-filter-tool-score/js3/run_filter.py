"""Run the v1.0.0 filter over every posting from one JS2 collection run.

    python3 -m js3.run_filter                          # latest logs/run_*.json
    python3 -m js3.run_filter logs/run_<stamp>.json

Writes logs/filter_run_<run stamp>.json: one record per posting (bucket,
reasons, matched skills with exact quotes) plus the summary counts. Reads
evidence only; makes no network calls.

The "palantir_lists_sensitivity" block is a MEASUREMENT, not a verdict: it
re-runs the same filter with Lever's `lists`/`additionalPlain` appended to
descriptionPlain and counts how many palantir buckets would change. The
reported buckets always use FILTER.md's descriptionPlain.
"""
import json
import sys
from collections import Counter
from pathlib import Path

from js3 import filter as flt
from js3.postings import load_run

ROOT = Path(__file__).resolve().parent.parent


def _reason_kind(r):
    rules = sorted({x.split(":")[0] for x in r["reasons"]})
    return " + ".join(rules) if rules else "-"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    report_path = (Path(argv[0]) if argv else max((ROOT / "logs").glob("run_*.json"))).resolve()
    report, postings, per_board = load_run(report_path, ROOT)
    out = flt.run_filter(postings)
    summ = flt.summary(out)

    by_board = {}
    for b in per_board:
        rs = [r for r in out["results"] if r["board"] == b]
        by_board[b] = {"collected": per_board[b]["postings"], "status": per_board[b]["status"],
                       **{k: sum(r["bucket"] == k for r in rs) for k in flt.BUCKETS}}
    reject_reasons = Counter(_reason_kind(r) for r in out["rejected"])

    changed = []
    for p in postings:
        if p["board"] != "palantir":
            continue
        alt = dict(p, content=(p["content"] or "") + "\n" + p.get("lever_extra", ""))
        a, b = flt.classify(p)["bucket"], flt.classify(alt)["bucket"]
        if a != b:
            changed.append({"id": p["id"], "title": p["title"], "descriptionPlain_only": a, "with_lists": b})

    stamp = Path(report_path).stem.removeprefix("run_")
    record = {"filter_version": flt.VERSION, "source_run": str(Path(report_path).relative_to(ROOT)),
              "source_run_started_at": report["started_at"], "source_run_exit": report["exit"],
              "summary": summ, "by_board": by_board, "reject_reasons": dict(reject_reasons),
              "palantir_lists_sensitivity": {"changed": len(changed), "postings": changed},
              "results": out["results"]}
    log_path = ROOT / "logs" / f"filter_run_{stamp}.json"
    log_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")

    print(f"JS3 filter v{flt.VERSION} over {record['source_run']} "
          f"(JS2 run {report['started_at']}, exit {report['exit']})")
    print(f"  total {summ['total']}   relevant {summ['relevant']}   rejected {summ['rejected']}   "
          f"insufficient_data {summ['insufficient_data']}")
    assert summ["relevant"] + summ["rejected"] + summ["insufficient_data"] == summ["total"]
    print(f"  {'board':<10}{'collected':>10}{'relevant':>10}{'rejected':>10}{'insuff.':>10}")
    for b, d in by_board.items():
        print(f"  {b:<10}{d['collected']:>10}{d['relevant']:>10}{d['rejected']:>10}{d['insufficient_data']:>10}")
    print("  reject reasons: " + ", ".join(f"{k}: {v}" for k, v in sorted(reject_reasons.items())))
    print(f"  palantir sensitivity (measurement only): {len(changed)} bucket(s) would change if Lever "
          f"`lists`/`additionalPlain` were counted as content")
    for c in changed:
        print(f"    - {c['id']}: {c['title']}  ({c['descriptionPlain_only']} -> {c['with_lists']})")
    if out["insufficient_data"]:
        print("  insufficient_data:")
        for r in out["insufficient_data"]:
            print(f"    - [{r['board']}] {r['id']}: {r['title']}")
    print(f"  relevant ({summ['relevant']}):")
    for r in out["relevant"]:
        skills = ", ".join(m["skill"] for m in r["matched_skills"])
        extra = f"  [rule 2 exception: {r['sales_title_word']!r} + {r['ai_building_phrase']!r}]" \
            if r["sales_title_word"] else ""
        print(f"    - [{r['board']}] {r['id']}: {r['title']}  ({skills}){extra}")
    print(f"  filter run log: {log_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
