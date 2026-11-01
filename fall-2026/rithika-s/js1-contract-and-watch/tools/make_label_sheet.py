"""Build the hand-labeling sheet for the prompt experiment.

Picks 20 REAL postings from a saved board response (deterministic, fixed
seed), splits them 10 development / 10 held-out BEFORE any labeling, and
writes a CSV with blank label columns plus short excerpts to speed up
hand labeling. Labels are filled in by hand, not by this script.

Usage:
    python3 tools/make_label_sheet.py <raw.json> <out.csv>
"""
import csv
import html
import json
import random
import re
import sys
from pathlib import Path

ROLE_WORDS = ["engineer", "data", "machine learning", "ml", "ai",
              "scientist", "analyst", "analytics"]
FLAG_WORDS = ["years", "clearance", "sponsor", "visa", "authoriz",
              "citizen"]


def clean(text):
    text = html.unescape(html.unescape(text or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def has_word(text, word):
    pattern = r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None


def excerpts(text, limit=6):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    hits = [s for s in sentences if any(w in s.lower() for w in FLAG_WORDS)]
    return " | ".join(s[:220] for s in hits[:limit])


def main():
    raw = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    jobs = sorted(raw["jobs"], key=lambda j: j["id"])
    role = [j for j in jobs if any(has_word(j["title"], w) for w in ROLE_WORDS)]
    other = [j for j in jobs if j not in role]

    rng = random.Random(7375)
    picked = rng.sample(role, 14) + rng.sample(other, 6)
    rng.shuffle(picked)

    fields = ["posting_id", "split", "title", "location", "absolute_url",
              "excerpts", "label", "failed_condition", "note"]
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i, j in enumerate(picked):
            writer.writerow({
                "posting_id": j["id"],
                "split": "dev" if i < 10 else "heldout",
                "title": j["title"],
                "location": (j.get("location") or {}).get("name", ""),
                "absolute_url": j["absolute_url"],
                "excerpts": excerpts(clean(j.get("content"))),
                "label": "",
                "failed_condition": "",
                "note": "",
            })
    print(f"wrote {len(picked)} rows to {sys.argv[2]}")


if __name__ == "__main__":
    main()
