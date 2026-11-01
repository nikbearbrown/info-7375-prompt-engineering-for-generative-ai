"""Spread per posting across the repeated fresh conversations, next to the rule's record
and Omkar's hand label. Agreement with itself is repeatability, not correctness.

    python3 -m experiments.sampling.summarize"""
from collections import Counter, defaultdict

from experiments.common import RESUME, SAMPLING_OUT, load_labels, load_postings, read_jsonl
from jsagent import persona, rule

rows = read_jsonl(SAMPLING_OUT)
labels, postings, resume = load_labels(), load_postings(), persona.load(RESUME)
by = defaultdict(list)
for r in rows:
    by[r["posting_id"]].append(r)
print("| posting | title | Claude verdicts (in order) | modal share | rejected | rule (record) | Omkar hand label | modal = hand? |")
print("|---|---|---|---:|---:|---|---|---|")
for pid, rs in by.items():
    vs = [r["verdict"] if r["status"] == "valid" else "REJECTED" for r in sorted(rs, key=lambda r: r["trial"])]
    valid = [v for v in vs if v != "REJECTED"]
    modal, k = Counter(valid).most_common(1)[0] if valid else ("-", 0)
    hand = labels.get(pid, {}).get("omkar_label", "").strip() or "(not labelled)"
    print(f"| {pid} | {postings[pid]['title']} | {', '.join(vs)} | {k}/{len(vs)} | {len(vs) - len(valid)} |"
          f" {rule.judge(postings[pid], resume)['verdict']} | {hand} | {'yes' if modal == hand else 'no'} |")
