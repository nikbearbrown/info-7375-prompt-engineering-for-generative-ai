"""JS3 Step 3/4: run the filter (the FILTER.md version in jsagent/filter.py) on the whole snapshot and write the results and the shortlist.

    python3 scripts/run_filter.py        # writes runs/filter-<version>/ (refuses to overwrite)

Run only after the hand labels are finished, so the labels stay blind to the filter (FILTER.md section 5).
"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsagent import filter as flt, shortlist, snapshot  # noqa: E402

OUT = ROOT / "runs" / ("filter-" + flt.FILTER_VERSION.split()[-1])


def main():
    if OUT.exists():
        sys.exit(f"refused: {OUT.relative_to(ROOT)} already exists")
    postings, outcomes = snapshot.load()
    results = [flt.evaluate(p) for p in postings]
    OUT.mkdir(parents=True)
    with (OUT / "results.jsonl").open("w") as f:
        for r in results:
            f.write(json.dumps({k: v for k, v in r.items() if k != "content"}) + "\n")
    sl = shortlist.build(results)
    (OUT / "shortlist.json").write_text(json.dumps(sl, indent=2) + "\n")
    buckets = collections.Counter(r["bucket"] for r in results)
    first_fail = collections.Counter(next(k for k, v in r["rules"].items() if v["result"] == "fail")
                                     for r in results if r["bucket"] == "rejected")
    labels = collections.Counter(c["label"] for k in sl["kept"] for c in k["claims"])
    summary = {"filter_version": flt.FILTER_VERSION, "snapshot": str(snapshot.DEFAULT.relative_to(ROOT)),
               "postings": len(results), "boards": outcomes, "buckets": dict(buckets),
               "rejected_by_first_failing_rule": dict(first_fail),
               "closest_calls": sum(r["closest_call"] for r in results), "claim_labels": dict(labels)}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
