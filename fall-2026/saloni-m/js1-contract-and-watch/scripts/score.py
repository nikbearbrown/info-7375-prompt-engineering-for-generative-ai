"""Recompute every table in the sampling report and the prompt experiment from the saved calls.

    python3 scripts/score.py sampling
    python3 scripts/score.py experiment

A rejected or errored call counts as a miss: the contract says it is not a verdict.
"""
import collections
import csv
import json
import sys

sys.path.insert(0, ".")
from agent.resume import load_resume  # noqa: E402
from agent.rule import judge_rule  # noqa: E402

mode = sys.argv[1]
hand = {int(r["id"]): r["hand_label"] for r in csv.DictReader(open("labels/hand_labels.csv", encoding="utf-8"))}
calls = [json.loads(line) for line in open(f"results/{mode}/calls.jsonl", encoding="utf-8")]
resume = load_resume("personas/priya-nair.resume.json")
spec = json.load(open("labels/experiment_set.json", encoding="utf-8"))
jobs = {j["id"]: j for j in json.load(open(spec["source"], encoding="utf-8"))["jobs"]}
short = {"relevant": "R", "not_relevant": "N"}

if mode == "sampling":
    by = collections.defaultdict(list)
    for c in calls:
        by[(c["id"], c["title"])].append(short.get(c.get("verdict"), "X") if c["status"] == "ok" else "X")
    print("| id | title | hand | rule | Claude verdicts (in order) | modal share | modal = hand? |")
    print("|---|---|---|---|---|---|---|")
    for (pid, title), vs in by.items():
        modal, n = collections.Counter(vs).most_common(1)[0]
        print(f"| {pid} | {title} | {short.get(hand.get(pid), '?')} | {short[judge_rule(jobs[pid], resume)['verdict']]} "
              f"| {' '.join(vs)} | {n}/{len(vs)} | {'yes' if short.get(hand.get(pid)) == modal else 'no'} |")
else:
    rows = collections.defaultdict(dict)
    for c in calls:
        got = c.get("verdict") if c["status"] == "ok" else c["status"]
        rows[(c["split"], c["prompt"])][c["id"]] = got
    print("| split | judge | passes vs hand label | rejected/errored |")
    print("|---|---|---|---|")
    for split in ("dev", "heldout"):
        ids = [p["id"] for p in spec["postings"] if p["split"] == split]
        rule_pass = sum(judge_rule(jobs[i], resume)["verdict"] == hand.get(i) for i in ids)
        print(f"| {split} | rule (record) | {rule_pass}/{len(ids)} | 0 |")
        for (s, prompt), got in sorted(rows.items()):
            if s != split:
                continue
            ok = sum(got.get(i) == hand.get(i) for i in ids)
            bad = sum(got.get(i) in ("rejected", "error") for i in ids)
            print(f"| {split} | Claude {prompt} (judgment) | {ok}/{len(ids)} | {bad} |")
    print("\nPer posting:")
    for split in ("dev", "heldout"):
        for p in (q for q in spec["postings"] if q["split"] == split):
            cells = [f"{prompt.split('/')[-1]}={got.get(p['id'], '-')}" for (s, prompt), got in sorted(rows.items()) if s == split]
            print(f"- {split} {p['id']} {p['title']}: hand={hand.get(p['id'])} "
                  f"rule={judge_rule(jobs[p['id']], resume)['verdict']} {' '.join(cells)}")
