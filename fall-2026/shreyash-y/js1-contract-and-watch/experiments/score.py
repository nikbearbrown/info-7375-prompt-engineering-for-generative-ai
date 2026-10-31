"""Score Claude's answers for one set against (a) Shreyash's hand labels, the pass mark, and
(b) the rule's record of failed conditions, a recomputable comparison that is NOT a hand label.

  PYTHONPATH=. python3 experiments/score.py --set development --summary experiments/prompt-experiment/dev-baseline/devbase-summary.jsonl
"""
import argparse
import csv
import json
import pathlib
import re

from jsagent import persona, posting, rule

ap = argparse.ArgumentParser()
ap.add_argument("--set", choices=["development", "held_out"], required=True)
ap.add_argument("--summary", required=True, nargs="+")
a = ap.parse_args()

sel = json.loads(pathlib.Path("experiments/selected_postings.json").read_text())
jobs = {j["id"]: j for j in json.loads(pathlib.Path(sel["raw_file"]).read_bytes())["jobs"]}
view = persona.public_view(persona.load("persona/alex_morgan.json"))
labels = {int(r["posting_id"]): r for r in csv.DictReader(open("labels/hand-labels.csv"))}
ids = [x["id"] for x in sel[a.set]]


def quotes_found(justification, p):
    """Double-quoted spans (4+ chars) in the justification, and how many appear word for word in
    the posting's title, departments, location, offices or content (case and spacing ignored)."""
    squash = lambda t: re.sub(r"\s+", " ", t).strip().lower()
    hay = squash(" | ".join([p["title"], *p["departments"], p["location"], *p["offices"], p["content"]]))
    spans = [q for q in re.findall(r"\"([^\"]*)\"", justification) if len(q) >= 4 and squash(q) != "not stated"]
    return len(spans), sum(squash(q).rstrip(".,;") in hay for q in spans)

for path in a.summary:
    rows = [json.loads(l) for l in open(path)]
    rows = [r for r in rows if r["posting_id"] in ids]
    valid = [r for r in rows if r["valid"]]
    verdict_ok = sum(r["parsed"]["verdict"] == labels[r["posting_id"]]["label"] for r in valid)
    exact = 0
    q_total = q_found = with_quote = 0
    per_cond = {n: 0 for n in range(1, 7)}
    lines = []
    for r in rows:
        rec = rule.judge(posting.normalize(jobs[r["posting_id"]], "oscar"), view)
        if not r["valid"]:
            lines.append(f"  {r['posting_id']}  REJECTED by validator: {r['errors']}")
            continue
        c = sorted(r["parsed"]["failed_conditions"])
        n_q, n_f = quotes_found(r["parsed"]["justification"], posting.normalize(jobs[r["posting_id"]], "oscar"))
        q_total, q_found, with_quote = q_total + n_q, q_found + n_f, with_quote + (n_q > 0)
        diff = sorted(set(c) ^ set(rec["failed_conditions"]))
        exact += not diff
        for n in diff:
            per_cond[n] += 1
        lines.append(f"  {r['posting_id']}  hand {labels[r['posting_id']]['label']:<12} Claude {r['parsed']['verdict']:<12} "
                     f"Claude failed {c}  rule failed {rec['failed_conditions']}  {'same' if not diff else 'differ on ' + str(diff)}  "
                     f"| {jobs[r['posting_id']]['title'].strip()}")
    print(f"{path}  (prompt sha256 {rows[0]['prompt_sha256'][:12]}, {rows[0]['model']})")
    print(f"  answers {len(rows)}; passed validator {len(valid)}/{len(rows)}")
    print(f"  PASS MARK, verdict = hand label: {verdict_ok}/{len(rows)}")
    print(f"  failed-condition set = rule record (not a hand label): {exact}/{len(rows)}; "
          f"disagreements by condition: {per_cond}")
    print(f"  evidence quotes: answers with a double-quoted posting span {with_quote}/{len(valid)}; "
          f"spans found word for word in the posting {q_found}/{q_total}")
    print("\n".join(lines))
