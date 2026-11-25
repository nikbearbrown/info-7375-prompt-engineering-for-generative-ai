"""Run the FILTER.md filter on the JS2 raw board files.

Usage (from the repo root):
    python3 -m js3.run_filter

Reads the raw files read-only and writes output/filter_results.json.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from js3.filter import Filter

RAW_DIR = Path("/Users/sreevarshansathiyamurthy/eng_job 2/output/raw")
SOURCES = {
    "databricks": RAW_DIR / "20261106T191045895303Z-greenhouse-databricks.json",
    "stripe": RAW_DIR / "20261106T191046089299Z-greenhouse-stripe.json",
    "spotify": RAW_DIR / "20261106T191046946413Z-lever-spotify.json",
}
OUTPUT = Path(__file__).resolve().parent.parent / "output" / "filter_results.json"

REASONS = ["title_match", "title_and_topic", "hard_reject", "no_match"]


def main() -> None:
    results: dict[str, list[dict]] = {}
    for board, path in SOURCES.items():
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        results[board] = Filter.from_raw(raw).run()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    grand = Counter()
    for board, rows in results.items():
        passed = sum(r["passed"] for r in rows)
        reasons = Counter(r["reason"] for r in rows)
        grand["total"] += len(rows)
        grand["passed"] += passed
        grand.update(reasons)
        print(f"== {board} ==")
        if not rows:
            print("  MISSING: board returned zero postings (not treated as zero-match)")
        print(f"  total:    {len(rows)}")
        print(f"  passed:   {passed}")
        print(f"  rejected: {len(rows) - passed}")
        for reason in REASONS:
            print(f"    {reason:<16} {reasons.get(reason, 0)}")
    print("== all boards ==")
    print(f"  total:    {grand['total']}")
    print(f"  passed:   {grand['passed']}")
    print(f"  rejected: {grand['total'] - grand['passed']}")
    for reason in REASONS:
        print(f"    {reason:<16} {grand.get(reason, 0)}")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
