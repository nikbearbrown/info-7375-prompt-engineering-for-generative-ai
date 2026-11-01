"""Build a STRATIFIED hand-labeling sheet (v2) for the prompt experiment.

v1 (commit a40d97b) drew 20 postings at random; almost none could
plausibly be relevant (base-rate problem). v2, built BEFORE any labels
existed, draws up to 10 'plausible' postings (data/ML/AI/engineering
title words, no seniority, research, or Public Sector words) and fills
the rest from all other postings. Each stratum is split evenly between
dev and held-out with a fixed seed. Labels are filled in by hand.

Usage:
    python3 tools/make_label_sheet_v2.py <raw.json> <out.csv>
"""
import csv
import json
import random
import sys
from pathlib import Path

from make_label_sheet import clean, excerpts, has_word

ROLE = ["machine learning", "ml", "ai", "data", "analyst", "analytics",
        "scientist", "engineer"]
NOT_ENTRY = ["senior", "sr", "staff", "principal", "lead", "manager",
             "director", "head", "research"]


def plausible(title):
    t = title.lower()
    return (any(has_word(t, w) for w in ROLE)
            and not any(has_word(t, w) for w in NOT_ENTRY)
            and "public sector" not in t)


def main():
    raw = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    jobs = sorted(raw["jobs"], key=lambda j: j["id"])
    pl = [j for j in jobs if plausible(j["title"])]
    other = [j for j in jobs if not plausible(j["title"])]
    print(f"{len(pl)} plausible candidates on the board:")
    for j in pl:
        print("  ", j["id"], j["title"])

    rng = random.Random(7375)
    n_pl = min(10, len(pl))
    groups = [("plausible", rng.sample(pl, n_pl)),
              ("other", rng.sample(other, 20 - n_pl))]
    rows = []
    for stratum, group in groups:
        for i, j in enumerate(group):
            rows.append((stratum, "dev" if i % 2 == 0 else "heldout", j))
    rows.sort(key=lambda r: (r[1], r[2]["id"]))

    fields = ["posting_id", "split", "stratum", "title", "location",
              "absolute_url", "excerpts", "label", "failed_condition", "note"]
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for stratum, split, j in rows:
            writer.writerow({
                "posting_id": j["id"], "split": split, "stratum": stratum,
                "title": j["title"],
                "location": (j.get("location") or {}).get("name", ""),
                "absolute_url": j["absolute_url"],
                "excerpts": excerpts(clean(j.get("content"))),
                "label": "", "failed_condition": "", "note": "",
            })
    print(f"\nwrote {len(rows)} rows to {sys.argv[2]}:")
    for stratum, split, j in rows:
        print(f"  {split:8} {stratum:9} {j['id']} {j['title']}")


if __name__ == "__main__":
    main()
