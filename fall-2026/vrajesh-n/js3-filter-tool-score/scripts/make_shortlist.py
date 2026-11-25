"""Build the source-grounded shortlist: every relevant posting (filter v2) with every claim labelled against its text.
Usage: python scripts/make_shortlist.py   (reads results/filter-v2c-r1.json and the snapshot; writes results/shortlist.*)"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from earlybird import boards, claims  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402

resume = load_resume(ROOT / "data/resume/rohan-desai.example.json")
rows = [r for r in json.loads((ROOT / "results/filter-v2c-r1.json").read_text(encoding="utf-8"))
        if r["verdict"] == "relevant"]
posts = {}
for f in sorted((ROOT / "data/snapshot-2026-11-01").glob("*.json")):
    for p in boards.parse(f.stem.split("_")[0], f.read_text(encoding="utf-8")):
        posts[(f.stem, p["id"])] = p

short = []
for r in rows:
    p = posts[(r["board"], r["id"])]
    cl = claims.label_claims(p, resume)
    short.append({"board": r["board"], "id": r["id"], "title": r["title"], "location": r["location"], "url": r["url"],
                  "claims": cl})
(ROOT / "results/shortlist.json").write_text(json.dumps(short, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Source-grounded shortlist (filter v2, snapshot 2026-11-01)\n",
      "Every claim is labelled against the posting's own text. `insufficient` is printed as \"I cannot tell\".\n"]
count = collections.defaultdict(collections.Counter)
for s in short:
    md.append(f"\n## {s['title'].strip()} - {s['board']}\n- {s['location']}  |  {s['url']}\n")
    for c in s["claims"]:
        count[c["claim"]][c["label"]] += 1
        if c["label"] == "insufficient":
            md.append(f"- **{c['claim']}**: I cannot tell ({c['why']})\n")
        else:
            md.append(f"- **{c['claim']}**: {c['label']} - {c['quote']}\n")
(ROOT / "results/shortlist.md").write_text("".join(md), encoding="utf-8")
print(len(short), "shortlisted")
for k, v in count.items():
    print(f"{k:13s}", dict(v))
