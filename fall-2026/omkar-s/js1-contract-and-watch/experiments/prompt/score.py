"""Pass rate = Claude's verdict equals Omkar's hand label; a rejected output counts as a fail.
Also reports the rule's agreement with the hand labels on the same postings."""
import glob
import os

from experiments.common import EXP, read_jsonl

print("| prompt | split | n | valid | pass | pass rate | rule = hand |")
print("|---|---|---:|---:|---:|---:|---:|")
for path in sorted(glob.glob(os.path.join(EXP, "results", "*.jsonl"))):
    rows = read_jsonl(path)
    n = len(rows)
    valid = sum(r["status"] == "valid" for r in rows)
    ok = sum(r["pass"] for r in rows)
    rule_ok = sum(r["rule_verdict"] == r["hand_label"] for r in rows)
    print(f"| {rows[0]['prompt']} | {rows[0]['split']} | {n} | {valid} | {ok} | {ok}/{n} = {ok / n:.0%} | {rule_ok}/{n} |")
