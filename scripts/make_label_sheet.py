"""JS3 Step 2: write labels/labels.csv, the postings Ethan hand-labels before any score change (FILTER.md section 5).

Pool (Ethan's choice, 2026-11-25): every posting in the 2026-11-25 snapshot whose title has a data-ish word
(data, analytics, analyst, BI, business intelligence, ETL, warehouse, pipeline). This is broader than F1 on purpose, so the
labels are not chosen by the filter being measured. Order is shuffled with a fixed seed, and each posting is assigned to
"tuning" or "heldout" before any label exists. The sheet shows no filter, score or Claude output.

    python3 scripts/make_label_sheet.py
"""
import csv
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsagent import snapshot  # noqa: E402

LABELS = ROOT / "labels" / "labels.csv"
POOL = re.compile(r"\b(data|analytics?|analyst|BI|business intelligence|ETL|warehouse|pipeline)\b", re.I)
SEED = 7375
FIELDS = ["n", "split", "board", "posting_id", "title", "location", "url", "human_label", "label_note"]


def main():
    if LABELS.exists():
        sys.exit(f"refused: {LABELS.relative_to(ROOT)} already exists; hand labels are never overwritten")
    postings, _ = snapshot.load()
    pool = sorted((p for p in postings if POOL.search(p["title"])), key=lambda p: (p["board"], p["id"]))
    rng = random.Random(SEED)
    rng.shuffle(pool)
    half = len(pool) // 2
    LABELS.parent.mkdir(exist_ok=True)
    with LABELS.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for i, p in enumerate(pool, 1):
            w.writerow({"n": i, "split": "tuning" if i <= half else "heldout", "board": p["board"], "posting_id": p["id"],
                        "title": p["title"], "location": p["location"]["name"], "url": p["absolute_url"],
                        "human_label": "", "label_note": ""})
    print(f"wrote {LABELS.relative_to(ROOT)}: {len(pool)} postings ({half} tuning, {len(pool) - half} heldout), human_label empty")


if __name__ == "__main__":
    main()
