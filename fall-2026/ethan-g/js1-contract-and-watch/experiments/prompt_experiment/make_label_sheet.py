"""Write labels.csv with the 20 selected postings and an empty human_label column.

    python3 experiments/prompt_experiment/make_label_sheet.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import LABELS, load_postings, select_split  # noqa: E402

dev, held = select_split()
ps = load_postings()
if LABELS.exists():
    sys.exit(f"{LABELS} already exists; not overwriting hand labels")
with LABELS.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["split", "board", "posting_id", "title", "location", "url", "human_label", "label_note"])
    w.writeheader()
    for split, ids in [("dev", dev), ("heldout", held)]:
        for pid in ids:
            p = ps[pid]
            w.writerow({"split": split, "board": p["board"], "posting_id": pid, "title": p["title"], "location": p["location"]["name"],
                        "url": p["absolute_url"], "human_label": "", "label_note": ""})
print(f"wrote {LABELS}: 10 dev + 10 heldout, human_label empty")
