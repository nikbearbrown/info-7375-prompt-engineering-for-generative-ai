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
ap.add_argument("--selection", default="experiments/selected_postings.json")
ap.add_argument("--labels", default="labels/hand-labels.csv")
ap.add_argument("--board", default="oscar")
a = ap.parse_args()

sel = json.loads(pathlib.Path(a.selection).read_text())
jobs = {j["id"]: j for j in json.loads(pathlib.Path(sel["raw_file"]).read_bytes())["jobs"]}
view = persona.public_view(persona.load("persona/alex_morgan.json"))
labels = {int(r["posting_id"]): r for r in csv.DictReader(open(a.labels))}
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
        rec = rule.judge(posting.normalize(jobs[r["posting_id"]], a.board), view)
        if not r["valid"]:
            lines.append(f"  {r['posting_id']}  REJECTED by validator: {r['errors']}")
            continue
        c = sorted(r["parsed"]["failed_conditions"])
        n_q, n_f = quotes_found(r["parsed"]["justification"], posting.normalize(jobs[r["posting_id"]], a.board))
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


# Hand-label scoring of failed conditions and of the Relevant class, used only when the labels
# file has per-condition labels (experiment 2). Experiment 1's labels are verdicts only.
def hand_failed(r):
    return sorted(int(x) for x in r["failed_conditions"].split(";") if x.strip())


if all(r.get("failed_conditions", "") != "" or r["label"] == "Relevant" for r in (labels[i] for i in ids)):
    for path in a.summary:
        rows = [json.loads(l) for l in open(path) if json.loads(l)["posting_id"] in ids]
        cand = {"Claude": {r["posting_id"]: (r["parsed"]["verdict"], sorted(r["parsed"]["failed_conditions"]))
                           for r in rows if r["valid"]}}
        cand["rule v1 record"] = {}
        for pid in ids:
            rec = rule.judge(posting.normalize(jobs[pid], a.board), view)
            cand["rule v1 record"][pid] = (rec["verdict"], rec["failed_conditions"])
        print(f"\n{path}: scored against Shreyash's per-condition hand labels")
        for name, got in cand.items():
            tp = sum(got[i][0] == "Relevant" and labels[i]["label"] == "Relevant" for i in got)
            fp = sum(got[i][0] == "Relevant" and labels[i]["label"] != "Relevant" for i in got)
            fn = sum(got[i][0] != "Relevant" and labels[i]["label"] == "Relevant" for i in got)
            verdict_ok = sum(got[i][0] == labels[i]["label"] for i in got)
            exact = sum(got[i][1] == hand_failed(labels[i]) for i in got)
            per = {n: sum((n in got[i][1]) != (n in hand_failed(labels[i])) for i in got) for n in range(1, 7)}
            print(f"  {name:15} verdict = hand {verdict_ok}/{len(got)}; failed set = hand {exact}/{len(got)}; "
                  f"Relevant: TP {tp} FP {fp} FN {fn}; condition disagreements {per}")
            for i in got:
                if got[i] != (labels[i]["label"], hand_failed(labels[i])):
                    print(f"      {i} {jobs[i]['title'].strip()[:50]:50} hand {labels[i]['label']} {hand_failed(labels[i])}  {name} {got[i][0]} {got[i][1]}")
