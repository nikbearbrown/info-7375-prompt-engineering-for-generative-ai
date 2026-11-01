"""Sampling report data: ask Claude the same contract about 5 postings, N fresh conversations each.

    python3 experiments/sampling/run_sampling.py            # N=4 calls per posting, appends to results.jsonl
    python3 experiments/sampling/run_sampling.py --summary  # table: verdict spread vs hand label

Each call is a new `claude -p` process with --no-session-persistence: no shared history between calls.
The 5 postings are the first 5 of the dev split (never the held-out set).
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import ROOT, load_postings, load_resume, read_labels, select_split, write_jsonl  # noqa: E402
from jsagent import claude_judge  # noqa: E402

RESULTS = HERE / "results.jsonl"
PROMPT = ROOT / "prompts" / "judge_v1_baseline.txt"

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=4)
ap.add_argument("--summary", action="store_true")
args = ap.parse_args()

ids = select_split()[0][:5]

if not args.summary:
    ps, r = load_postings(), load_resume()
    batch = datetime.now().astimezone().isoformat(timespec="seconds")
    for pid in ids:
        for k in range(args.n):
            j = claude_judge.judge(ps[pid], r, PROMPT)
            row = {"batch": batch, "posting_id": pid, "title": ps[pid]["title"], "trial": k + 1, **j}
            write_jsonl(RESULTS, [row])
            print(pid, k + 1, j["status"], j.get("verdict", ""), (j.get("errors") or [""])[0][:80])

rows = [json.loads(line) for line in RESULTS.open()] if RESULTS.exists() else []
labels = read_labels()
print("\n| posting | title | calls | relevant | not_relevant | rejected/error | hand label | agree w/ hand |")
print("|---|---|---|---|---|---|---|---|")
for pid in ids:
    rs = [x for x in rows if x["posting_id"] == pid]
    c = Counter(x.get("verdict") if x["status"] == "valid" else "bad" for x in rs)
    hand = labels.get(pid, {}).get("human_label") or "(unlabeled)"
    agree = sum(1 for x in rs if x["status"] == "valid" and x["verdict"] == hand)
    title = rs[0]["title"] if rs else ""
    print(f"| {pid} | {title} | {len(rs)} | {c['relevant']} | {c['not_relevant']} | {c['bad']} | {hand} | "
          f"{agree}/{len(rs) if hand != '(unlabeled)' else '-'} |")
