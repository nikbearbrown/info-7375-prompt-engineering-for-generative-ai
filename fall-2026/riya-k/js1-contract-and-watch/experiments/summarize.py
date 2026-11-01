"""Recompute every number in SAMPLING.md and PROMPT_EXPERIMENT.md from the saved results.
    python3 -m experiments.summarize
"""

import collections
import csv
import json
from pathlib import Path

from jsagent import rules

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "experiments" / "results"


def load(name):
    return [json.loads(l) for l in open(RES / name)]


def main():
    print("## Sampling (v1_baseline, 4 fresh calls per posting)\n")
    print("| # | title | hand label | Claude verdicts (4 calls) | agree with hand |")
    print("|---|---|---|---|---|")
    by_n = collections.defaultdict(list)
    for r in load("sampling_v1.jsonl"):
        by_n[r["n"]].append(r)
    for n, rs in sorted(by_n.items()):
        rs.sort(key=lambda r: r["attempt"])
        verdicts = ", ".join(r["verdict"] or "REJECTED" for r in rs)
        title = next(x["title"] for x in csv.DictReader(open(ROOT / "labels" / "hand_labels.csv")) if int(x["n"]) == n)
        print(f"| {n} | {title} | {rs[0]['hand_label']} | {verdicts} | {sum(r['agrees'] for r in rs)}/4 |")

    print("\n## Prompt experiment (pass = Claude verdict equals hand label; a validator rejection is a fail)\n")
    rows = list(csv.DictReader(open(ROOT / "labels" / "hand_labels.csv")))
    resume = json.loads((ROOT / "persona" / "arya-sahni.json").read_text())
    jobs = {j["id"]: j for j in json.loads((ROOT / "snapshots" / "databricks-2026-10-31T233230Z-live.json").read_text())["jobs"]}
    print("| judge | dev (10) | held-out (10) | rejected by validator |")
    print("|---|---|---|---|")
    for p in ["v1", "v2"]:
        d, h = load(f"{p}_dev.jsonl"), load(f"{p}_heldout.jsonl")
        rej = sum(r["verdict"] is None for r in d + h)
        print(f"| Claude, {p} prompt | {sum(r['agrees'] for r in d)}/10 | {sum(r['agrees'] for r in h)}/10 | {rej} |")
    for s in ["dev", "heldout"]:
        rs = [x for x in rows if x["set"] == s]
        globals()[s] = sum(rules.judge(jobs[int(x["id"])], resume)["verdict"] == x["label"] for x in rs)
        globals()[s + "_no"] = sum(x["label"] == "not_relevant" for x in rs)
    print(f"| written rule (record) | {dev}/10 | {heldout}/10 | n/a |")
    print(f"| always 'not_relevant' | {dev_no}/10 | {heldout_no}/10 | n/a |")
    print(f"\nHand labels: dev {10 - dev_no} relevant / {dev_no} not; held-out {10 - heldout_no} relevant / {heldout_no} not.")


if __name__ == "__main__":
    main()
