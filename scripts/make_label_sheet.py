"""JS3 Step 2: write labels/labels.csv, the postings Ethan hand-labels before any score change (FILTER.md section 5).

Pool (Ethan's choice, 2026-11-25): every posting in the 2026-11-25 snapshot whose title has a data-ish word
(data, analytics, analyst, BI, business intelligence, ETL, warehouse, pipeline). This is broader than F1 on purpose, so the
labels are not chosen by the filter being measured. Order is shuffled with a fixed seed, and each posting is assigned to
"tuning" or "heldout" before any label exists. The sheet shows no filter, score or Claude output.

Ethan's second choice, 2026-11-25, before any label: drop postings located outside the US, but keep every remote posting
(including "Remote - Canada" and "Remote - Mexico"). The non-US locations are listed by hand below, read from the 141 location
strings; this does not use the filter's F3 code.

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
NON_US = {
    "Abu Dhabi, United Arab Emirates", "Amsterdam, Netherlands", "Amsterdam, The Netherlands; Dublin, Ireland", "Belgrade, Serbia",
    "Bengaluru, India", "Berlin, Germany; Munich, Germany", "Dublin", "Dublin, Ireland", "London", "London, United Kingdom",
    "Milan, Italy", "Paris, France", "Sao Paulo, Brazil", "Singapore, Singapore", "Stockholm", "Tokyo, Japan",
    "Vancouver, Canada", "Warsaw, Poland",
}  # bare "Dublin" is Toast's Ireland office; bare "London" and "Stockholm" are Spotify's European offices
SEED = 7375


def in_pool(p):
    loc = p["location"]["name"]
    return bool(POOL.search(p["title"])) and ("remote" in loc.lower() or loc not in NON_US)
FIELDS = ["n", "split", "board", "posting_id", "title", "location", "url", "human_label", "label_note"]


def main():
    if LABELS.exists():
        sys.exit(f"refused: {LABELS.relative_to(ROOT)} already exists; hand labels are never overwritten")
    postings, _ = snapshot.load()
    pool = sorted((p for p in postings if in_pool(p)), key=lambda p: (p["board"], p["id"]))
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
