"""Run the filter on every posting in a snapshot.

    python3 scripts/run_filter.py [--snapshot out/snapshots/<t>] [--filter FILTER.md | --filter-json f.json] [--tag name]

Writes out/filter/<tag or version>/results.jsonl and summary.json.
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from js3.collect import HERE, latest_snapshot, load_postings  # noqa: E402
from js3.filter import DEFAULT_DOC, load_filter, rank, score  # noqa: E402


def run(snapshot, flt):
    posts = load_postings(snapshot)
    return rank([score(p, flt) for p in posts])


def summarize(results, snapshot, flt):
    rules = collections.Counter(f["rule"] for r in results for f in r["fired"])
    by_board = collections.Counter((r["uid"].rsplit(":", 1)[0], r["decision"]) for r in results)
    words = collections.Counter(w for r in results for f in r["fired"] if f["rule"] in ("R1", "R3") for w in f["matched"])
    return {
        "snapshot": os.path.relpath(snapshot, HERE),
        "filter_version": flt["filter_version"],
        "threshold": flt["threshold"],
        "postings": len(results),
        "kept": sum(r["decision"] == "keep" for r in results),
        "rejected": sum(r["decision"] == "reject" for r in results),
        "vetoed": sum(r["vetoed"] for r in results),
        "text_missing": sum(r["text_missing"] for r in results),
        "score_histogram": dict(sorted(collections.Counter(r["score"] for r in results).items())),
        "rule_fired_counts": dict(sorted(rules.items())),
        "matched_word_counts": dict(words.most_common()),
        "by_board": {f"{b} {d}": n for (b, d), n in sorted(by_board.items())},
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot")
    ap.add_argument("--filter", default=DEFAULT_DOC)
    ap.add_argument("--filter-json")
    ap.add_argument("--tag")
    a = ap.parse_args(argv)
    snap = a.snapshot or latest_snapshot()
    flt = load_filter(a.filter, a.filter_json)
    results = run(snap, flt)
    out = os.path.join(HERE, "out", "filter", a.tag or f"v{flt['filter_version']}")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "results.jsonl"), "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    s = summarize(results, snap, flt)
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)
    print(json.dumps(s, indent=2))
    print("kept:")
    for r in results:
        if r["decision"] == "keep":
            print(f"  {r['score']:>2}  {r['uid']:<45} {r['title']}")


if __name__ == "__main__":
    main()
