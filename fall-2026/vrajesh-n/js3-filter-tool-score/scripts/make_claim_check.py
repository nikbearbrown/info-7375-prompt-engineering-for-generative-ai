"""Blind hand-check of the claim labeler. Seeded sample of (posting, claim) pairs. Vrajesh reads the posting text
excerpts and writes supported / contradicted / insufficient; the labeler's labels are in claim-check-key.json,
opened only after his labels are saved. Excerpts use BROAD patterns (not the labeler's own) so a labeler miss is visible."""
import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from earlybird import boards  # noqa: E402

SEED = 7376
PLAN = {"early_career": 6, "stack_fit": 6, "sponsorship": 4, "no_clearance": 4, "ai_focus": 2, "us_location": 2}
BROAD = {
    "early_career": r"years?|experience",
    "stack_fit": r"\b(python|golang|go|java|javascript|typescript|sql|react|next\.js|tailwind|postgres\w*|mongodb|redis|aws|gcp|docker|kubernetes|k8s|jenkins|terraform|protobuf)\b",
    "sponsorship": r"sponsor|visa|work authori[sz]ation|citizen|u\.?s\.? person",
    "no_clearance": r"clearance|citizen|u\.?s\.? person|top secret|ts/sci",
    "ai_focus": r"\bai\b|\bllm|agent|generative|machine learning",
    "us_location": r"\Z",
}
short = json.loads((ROOT / "results/shortlist.json").read_text(encoding="utf-8"))
posts = {}
for f in sorted((ROOT / "data/snapshot-2026-11-01").glob("*.json")):
    for p in boards.parse(f.stem.split("_")[0], f.read_text(encoding="utf-8")):
        posts[(f.stem, p["id"])] = p
rng = random.Random(SEED)
pairs = []
for name, n in PLAN.items():
    pool = [(s, c) for s in short for c in s["claims"] if c["claim"] == name]
    pairs += rng.sample(pool, min(n, len(pool)))
rng.shuffle(pairs)

md = ["# Claim-label check sheet (blind)\n",
      "For each item, read the excerpts and the claim. Write **supported**, **contradicted** or **insufficient** in "
      "`claim-check-labels.csv`: does the posting's own text say it, say the opposite, or neither? You do not see the "
      "labeler's label. Open `claim-check-key.json` only after your labels are saved.\n"]
labels, key = [["n", "verdict", "note"]], []
for n, (s, c) in enumerate(pairs, 1):
    p = posts[(s["board"], s["id"])]
    t = p["descriptionPlain"]
    ex = []
    for m in re.finditer(BROAD[c["claim"]], t, re.I):
        a, b = max(0, m.start() - 80), min(len(t), m.end() + 80)
        if not ex or a > ex[-1][1]:
            ex.append([a, b])
        else:
            ex[-1][1] = b
    shown = " ... ".join(re.sub(r"\s+", " ", t[a:b]) for a, b in ex[:8]) or "(no matching words anywhere in the text)"
    md.append(f"\n## {n}. {s['title'].strip()} ({s['board']})\n- location: {s['location']}\n- **claim:** {c['statement']}\n"
              f"- excerpts: {shown[:1800]}\n")
    labels.append([n, "", ""])
    key.append({"n": n, "board": s["board"], "id": s["id"], "title": s["title"], "claim": c["claim"],
                "labeler_label": c["label"], "labeler_quote": c["quote"]})
(ROOT / "review/claim-check-sheet.md").write_text("".join(md), encoding="utf-8")
csv.writer(open(ROOT / "review/claim-check-labels.csv", "w", newline="", encoding="utf-8")).writerows(labels)
(ROOT / "review/claim-check-key.json").write_text(json.dumps(key, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(pairs), "items, seed", SEED)
