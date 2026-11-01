"""Sampling report (Chapter 1): ask Claude the same contract about each of 5 postings, 4 times each,
every time in a fresh `claude -p` conversation. Every reply is appended to sampling/results.jsonl.

Usage: python3 experiments/run_sampling.py [--trials 4] [--prompt prompts/judge_v1.txt]
       python3 experiments/run_sampling.py --summarize
"""
import argparse
import collections
import sys

from common import ROOT, append_jsonl, jobs_by_id, labels, maya, read_jsonl

sys.path.insert(0, str(ROOT))
from jobwatch import claude_judge, rule  # noqa: E402

IDS = [7983725, 8331124, 8195440, 8163193, 8127182]
OUT = ROOT / "experiments" / "sampling" / "results.jsonl"


def run(trials, prompt):
    jobs, resume = jobs_by_id(), maya()
    judge = claude_judge.make_judge(ROOT / prompt)
    done = collections.Counter(r["posting_id"] for r in read_jsonl(OUT))
    for pid in IDS:
        for t in range(done[pid] + 1, trials + 1):
            out = judge(jobs[pid], resume)
            append_jsonl(OUT, {"posting_id": pid, "trial": t, **out})
            print(pid, t, out["status"])


def summarize():
    hand = {r["id"]: r["hand_label"] for r in labels()}
    jobs, resume = jobs_by_id(), maya()
    rows = read_jsonl(OUT)
    print("| id | title | trials | relevant | not_relevant | invalid | rule (record) | hand label | Claude majority = hand? |")
    print("|---|---|---|---|---|---|---|---|---|")
    for pid in IDS:
        rs = [r for r in rows if r["posting_id"] == pid]
        c = collections.Counter(r.get("verdict", "invalid") if r["status"] == "valid" else "invalid" for r in rs)
        maj = c.most_common(1)[0][0] if rs else "-"
        print(f"| {pid} | {jobs[pid]['title'].strip()} | {len(rs)} | {c['relevant']} | {c['not_relevant']} | "
              f"{c['invalid']} | {rule.judge(jobs[pid], resume)['verdict']} | {hand[pid]} | "
              f"{'yes' if maj == hand[pid] else 'no'} |")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=4)
    ap.add_argument("--prompt", default="prompts/judge_v1.txt")
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    summarize() if a.summarize else run(a.trials, a.prompt)
