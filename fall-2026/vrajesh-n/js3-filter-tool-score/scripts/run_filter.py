"""Apply FILTER.md v1 (earlybird.rule.judge) to every posting in a snapshot. Usage:
python scripts/run_filter.py data/snapshot-2026-11-01 results/filter-v1.json
Read-only on the snapshot; writes one JSON file of verdicts."""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from earlybird import boards, rule  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402

snap, out = Path(sys.argv[1]), Path(sys.argv[2])
resume = load_resume(Path(__file__).resolve().parent.parent / "data/resume/rohan-desai.example.json")
rows = []
for f in sorted(snap.glob("*.json")):
    platform = f.stem.split("_")[0]
    for p in boards.parse(platform, f.read_text(encoding="utf-8")):
        v = rule.judge(p, resume)
        rows.append({"board": f.stem, "id": p["id"], "title": p["title"], "location": p["location"],
                     "url": p["url"], "verdict": v["verdict"], "failed_check": v["failed_check"],
                     "justification": v["justification"]})
out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
c = collections.Counter((r["verdict"], r["failed_check"]) for r in rows)
print(len(rows), "postings")
for k, n in sorted(c.items(), key=lambda kv: -kv[1]):
    print(f"{n:5d}  {k[0]:12s} {k[1]}")
