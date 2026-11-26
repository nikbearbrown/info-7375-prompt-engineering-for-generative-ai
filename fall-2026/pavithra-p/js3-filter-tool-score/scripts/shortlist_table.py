"""Prints the shortlist tables for SHORTLIST.md from the saved Claude replies and my claim labels (no Claude call).

    python3 scripts/shortlist_table.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.chdir(HERE)

from agent import evidence  # noqa: E402

entries = json.load(open("runs/20261125T204144Z/shortlist-v1.1/shortlist.json"))
mine = {r["claim_id"]: r for r in csv.DictReader(open("audit/claim-labels.csv"))}


def cell(text):
    return text.replace("|", "/").replace("\n", " ")


for n, e in enumerate(entries, 1):
    labels = [(c["about"], mine[f"{e['key']}#{i}"]["my_label"]) for i, c in enumerate(e["claims"], 1)]
    verdict = "I cannot tell if this fits" if evidence.abstain(labels) else "recommended to read"
    print(f"### {n}. {e['title']} (`{e['key']}`, score {e['score']})\n")
    print(f"Claude asked {e['asked_at']}. Abstention rule on my labels: {verdict}.\n")
    print("| # | About | Claude's claim | Claude's quote | Checker | Mine |")
    print("|---|---|---|---|---|---|")
    for i, c in enumerate(e["claims"], 1):
        m = mine[f"{e['key']}#{i}"]
        changed = " (changed, see below)" if m["changed_after_review"] else ""
        print(f"| {m['n']} | {c['about']} | {cell(c['claim'])} | {cell(c['quote']) or '(none)'} | {c['machine_label']} | "
              f"{m['my_label']}{changed} |")
    print()
