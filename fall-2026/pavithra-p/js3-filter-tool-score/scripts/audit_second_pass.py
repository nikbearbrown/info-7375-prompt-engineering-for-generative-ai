"""The audit of filter v1.0 on my second-pass labels (AUDIT.md section 8).

Each tuning posting uses its second-pass label if it was re-read (audit/reread-labels.csv), and its first label
otherwise (audit/hand-labels.csv). Offline; reads only saved files.

    python3 scripts/audit_second_pass.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.chdir(HERE)

from agent import audit  # noqa: E402

sample = json.load(open("audit/sample.json"))
first = audit.read_labels(open("audit/hand-labels.csv").read())
second = {r["key"]: (r["label"], r["note"]) for r in csv.DictReader(open("audit/reread-labels.csv"))}
decisions = {audit.key(d): d for d in map(json.loads, open(f"runs/{sample['run']}/filter-v1.0/decisions.jsonl"))}
print("| Set | First pass: filter wrong | Second pass: filter wrong | 95% Wilson (second pass) |")
print("|---|---|---|---|")
for name in ("random_rejects", "close_calls", "kept", "gate_close_calls"):
    keys = sample["sets"][name]
    counts = []
    for labels in (first, {**first, **second}):
        judged = [k for k in keys if labels.get(k) and labels[k][0] != "cannot tell"]
        wrong = [k for k in judged if audit.is_error(decisions[k]["verdict"], labels[k][0])]
        counts.append((len(wrong), len(judged), wrong))
    (w1, n1, _), (w2, n2, wrong2) = counts
    print(f"| {name.replace('_', ' ')} | {w1} of {n1} | {w2} of {n2} | {audit.pct(audit.wilson(w2, n2))} |")
    for k in wrong2:
        print(f"|   | | {decisions[k]['title'].strip()} ({decisions[k]['verdict']}) | |")
