"""Pick 20 Klaviyo postings for hand-labeling and split them into dev/heldout.

Run from the project folder: python3 experiment/select_postings.py

14 postings whose title contains "engineer" or "developer" (case-insensitive),
6 from the rest, seed 7; then a random 10/10 split into "dev" and "heldout".
Writes experiment/labels.csv with my_label and my_note blank. No rule or
Claude verdicts are computed or written here.
"""

import csv
import json
import random
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT / "raw" / "klaviyo_20261031T175121.json"
LABELS_PATH = PROJECT / "experiment" / "labels.csv"
SEED = 7
N_ENGINEERING, N_OTHER, N_DEV = 14, 6, 10
COLUMNS = ["id", "title", "location", "url", "set", "my_label", "my_note"]


def is_engineering(posting):
    title = posting["title"].lower()
    return "engineer" in title or "developer" in title


def already_labeled():
    if not LABELS_PATH.exists():
        return False
    with LABELS_PATH.open(newline="") as f:
        return any(row["my_label"].strip() for row in csv.DictReader(f))


def main():
    if already_labeled():
        sys.exit(f"refusing to overwrite {LABELS_PATH.name}: it already has labels")

    jobs = sorted(json.loads(RAW_PATH.read_text())["jobs"], key=lambda j: j["id"])
    engineering = [j for j in jobs if is_engineering(j)]
    other = [j for j in jobs if not is_engineering(j)]

    rng = random.Random(SEED)
    picked = rng.sample(engineering, N_ENGINEERING) + rng.sample(other, N_OTHER)
    rng.shuffle(picked)

    with LABELS_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for i, job in enumerate(picked):
            writer.writerow({
                "id": job["id"],
                "title": job["title"],
                "location": (job.get("location") or {}).get("name", ""),
                "url": job.get("absolute_url", ""),
                "set": "dev" if i < N_DEV else "heldout",
                "my_label": "",
                "my_note": "",
            })

    print(f"{len(jobs)} postings: {len(engineering)} engineer/developer, {len(other)} other")
    print(f"Wrote {len(picked)} rows to {LABELS_PATH.relative_to(PROJECT)} (seed {SEED})")


if __name__ == "__main__":
    main()
