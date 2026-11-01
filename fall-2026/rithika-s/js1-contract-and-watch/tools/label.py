"""Interactive hand-labeling for the prompt experiment.

Shows one posting at a time (title, location, excerpts, link) and records
the labeler's own decision. It never suggests a label. Saves after every
answer, so it can be stopped and resumed.

Usage:
    python3 tools/label.py reports/prompt_experiment/labels.csv
"""
import csv
import sys

path = sys.argv[1]
with open(path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
fields = list(rows[0].keys())

for n, r in enumerate(rows, 1):
    if r["label"]:
        continue
    print(f"\n[{n}/{len(rows)}] {r['posting_id']}  {r['title']}  ({r['location']})")
    print("  link:", r["absolute_url"])
    print("  excerpts:", r["excerpts"] or "(none)")
    while True:
        a = input("  [r]elevant / [n]ot relevant / [s]kip for now: ").strip().lower()
        if a in ("r", "n", "s"):
            break
    if a == "s":
        continue
    r["label"] = "relevant" if a == "r" else "not_relevant"
    if a == "n":
        r["failed_condition"] = input(
            "  failed condition (1 role, 2 clearance, 3 sponsorship, 4 experience): ").strip()
    r["note"] = input("  note, in your words (why): ").strip()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

print("\nlabeled:", sum(1 for r in rows if r["label"]), "of", len(rows))
