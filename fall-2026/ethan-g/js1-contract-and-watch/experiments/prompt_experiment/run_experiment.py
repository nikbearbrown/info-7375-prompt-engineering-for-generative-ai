"""Prompt experiment: run one prompt contract on one split and score it against your hand labels.

    python3 experiments/prompt_experiment/run_experiment.py --prompt prompts/judge_v1_baseline.txt --tag v1 --split dev
    python3 experiments/prompt_experiment/run_experiment.py --prompt prompts/judge_v2_revision.txt --tag v2 --split dev
    # only at the very end, once, after both prompts are frozen:
    python3 experiments/prompt_experiment/run_experiment.py --prompt ... --tag v1 --split heldout --unlock-heldout
    python3 experiments/prompt_experiment/run_experiment.py --summary

Pass = Claude's output passed the validator AND its verdict equals your hand label.
A rejected output counts as a fail. The rule judge is scored on the same postings for comparison (free).
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import ROOT, load_postings, load_resume, read_labels, write_jsonl  # noqa: E402
from jsagent import claude_judge, rule  # noqa: E402

RES = HERE / "results"
LOG = RES / "HELDOUT_LOG.txt"

ap = argparse.ArgumentParser()
ap.add_argument("--prompt")
ap.add_argument("--tag")
ap.add_argument("--split", choices=["dev", "heldout"])
ap.add_argument("--unlock-heldout", action="store_true")
ap.add_argument("--summary", action="store_true")
args = ap.parse_args()


def score(path):
    rows = [json.loads(x) for x in path.open()]
    p = sum(r["pass"] for r in rows)
    rej = sum(r["claude"]["status"] != "valid" for r in rows)
    rp = sum(r["rule_pass"] for r in rows)
    return len(rows), p, rej, rp


if args.summary:
    print("| prompt tag | split | n | Claude pass | rejected | rule-judge pass (same postings) |")
    print("|---|---|---|---|---|---|")
    for f in sorted(RES.glob("*__*.jsonl")):
        tag, split = f.stem.split("__")
        n, p, rej, rp = score(f)
        print(f"| {tag} | {split} | {n} | {p}/{n} | {rej} | {rp}/{n} |")
    sys.exit()

if not (args.prompt and args.tag and args.split):
    ap.error("--prompt, --tag and --split are required (or use --summary)")
labels = {pid: row for pid, row in read_labels().items() if row["split"] == args.split}
missing = [pid for pid, row in labels.items() if row["human_label"] not in ("relevant", "not_relevant")]
if missing:
    sys.exit(f"hand-label the {args.split} split first (missing: {missing}). Run label.py.")
out = RES / f"{args.tag}__{args.split}.jsonl"
if out.exists():
    sys.exit(f"{out} exists; results are append-only evidence. Use a new --tag.")
if args.split == "heldout":
    if not args.unlock_heldout:
        sys.exit("held-out is locked. Freeze both prompts on dev first, then pass --unlock-heldout.")
    if not (RES / f"{args.tag}__dev.jsonl").exists():
        sys.exit(f"run --tag {args.tag} on dev before held-out")

prompt_text = Path(args.prompt).read_text()
ps, r = load_postings(), load_resume()
stamp = datetime.now().astimezone().isoformat(timespec="seconds")
if args.split == "heldout":
    RES.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"{stamp} held-out unlocked for tag={args.tag} prompt={args.prompt} "
                f"sha256={hashlib.sha256(prompt_text.encode()).hexdigest()[:12]}\n")

for pid, row in labels.items():
    j = claude_judge.judge(ps[pid], r, args.prompt)
    rv = rule.judge(ps[pid], r)["verdict"]
    hand = row["human_label"]
    rec = {"tag": args.tag, "split": args.split, "posting_id": pid, "title": ps[pid]["title"],
           "prompt_file": args.prompt, "prompt_sha256": hashlib.sha256(prompt_text.encode()).hexdigest()[:12],
           "hand_label": hand, "claude": j, "pass": j["status"] == "valid" and j["verdict"] == hand,
           "rule_verdict": rv, "rule_pass": rv == hand}
    write_jsonl(out, [rec])
    print(f"{pid} hand={hand:<12} claude={j.get('verdict', j['status'].upper()):<12} rule={rv:<12} {'PASS' if rec['pass'] else 'FAIL'}  {ps[pid]['title'][:40]}")
n, p, rej, rp = score(out)
print(f"\n{args.tag} on {args.split}: Claude {p}/{n} pass ({rej} rejected); rule judge {rp}/{n} on the same postings")
