"""Prompt experiment (Chapter 2): run one prompt contract over the dev or held-out set, score it
against the hand labels. A case passes only if Claude's reply is valid AND its verdict equals the
hand label. Held-out runs require --final, meaning both prompts are frozen. Collecting replies does
not read the hand labels; only --score does.

Usage: python3 experiments/run_experiment.py --prompt prompts/judge_v1.txt --set dev
       python3 experiments/run_experiment.py --prompt prompts/judge_v2.txt --set heldout --final
       python3 experiments/run_experiment.py --score
"""
import argparse
import json
import pathlib
import sys

from common import ROOT, append_jsonl, jobs_by_id, labels, maya, read_jsonl

sys.path.insert(0, str(ROOT))
from jobwatch import claude_judge, rule  # noqa: E402

RESULTS = ROOT / "experiments" / "prompt" / "results"


def out_path(prompt, split):
    return RESULTS / f"{pathlib.Path(prompt).stem}-{split}.jsonl"


def run(prompt, split):
    """Collect Claude replies. Needs no hand labels: scoring joins them later, so runs cannot see labels."""
    sel = json.loads((ROOT / "experiments" / "prompt" / "selection.json").read_text())["postings"]
    rows = [r for r in sel if r["set"] == split]
    jobs, resume = jobs_by_id(), maya()
    judge = claude_judge.make_judge(ROOT / prompt)
    path = out_path(prompt, split)
    done = {r["posting_id"] for r in read_jsonl(path)}
    for r in rows:
        if r["id"] in done:
            continue
        out = judge(jobs[r["id"]], resume)
        append_jsonl(path, {"posting_id": r["id"], **out})
        print(r["id"], out["status"])


def score():
    jobs, resume = jobs_by_id(), maya()
    lab = labels()
    hand = {r["id"]: r["hand_label"] for r in lab}
    rule_ok = sum(rule.judge(jobs[r["id"]], resume)["verdict"] == r["hand_label"] for r in lab)
    print(f"rule judge (record) vs hand labels: {rule_ok}/{len(lab)} agree")
    print("\n| prompt | set | n | valid | pass (valid and = hand label) |\n|---|---|---|---|---|")
    for path in sorted(RESULTS.glob("*.jsonl")):
        rs = read_jsonl(path)
        valid = sum(r["status"] == "valid" for r in rs)
        ok = sum(r["status"] == "valid" and r["verdict"] == hand[r["posting_id"]] for r in rs)
        prompt, split = path.stem.rsplit("-", 1)
        print(f"| {prompt} | {split} | {len(rs)} | {valid} | {ok}/{len(rs)} |")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt")
    ap.add_argument("--set", choices=("dev", "heldout"))
    ap.add_argument("--final", action="store_true", help="required for held-out: prompts are frozen")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.score:
        score()
    elif a.set == "heldout" and not a.final:
        raise SystemExit("held-out is run once, at the end: pass --final once both prompts are frozen")
    else:
        run(a.prompt, a.set)
