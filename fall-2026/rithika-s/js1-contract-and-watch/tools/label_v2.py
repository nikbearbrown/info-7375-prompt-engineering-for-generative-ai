"""Condition-by-condition hand labeling (applies LABELING_RULE.md).

For each posting, the labeler answers the four rule conditions as y/n.
The label is derived from those answers: relevant only if all pass;
otherwise the first failed condition is recorded. Every answer is the
labeler's own; the tool never suggests one. Saves after each posting.

Usage:
    python3 tools/label_v2.py reports/prompt_experiment/labels.csv
"""
import csv
import sys

QUESTIONS = [
    ("5", "Is the role located in the US (or remote within the US)?", "y"),
    ("1", "Is it a role that builds/uses ML/AI or data systems "
          "(not research/sales/ops/product/marketing/other)?", "y"),
    ("2", "Does it REQUIRE a security clearance?", "n"),
    ("3", "Does it say sponsorship is not provided / sponsorship "
          "candidates not eligible?", "n"),
    ("4", "Does it REQUIRE more than 2 years, or does the title say "
          "Senior/Staff/Principal/Lead/Manager/Director?", "n"),
]


def ask(prompt):
    while True:
        a = input(f"  {prompt} [y/n]: ").strip().lower()
        if a in ("y", "n"):
            return a


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
    failed = ""
    for num, question, passing in QUESTIONS:
        if ask(question) != passing:
            failed = num
            break
    r["label"] = "not_relevant" if failed else "relevant"
    r["failed_condition"] = failed
    r["note"] = input("  note, in your words (why): ").strip()
    print(f"  -> {r['label']}" + (f" (condition {failed})" if failed else ""))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

print("\nlabeled:", sum(1 for r in rows if r["label"]), "of", len(rows))
