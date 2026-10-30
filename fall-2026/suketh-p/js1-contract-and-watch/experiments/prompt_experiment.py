"""Prompt experiment (Chapter 2): one prompt contract on one set of hand-labelled postings.

    python3 experiments/prompt_experiment.py --prompt judge_v1 --set development
    python3 experiments/prompt_experiment.py --prompt judge_v2 --set development
    python3 experiments/prompt_experiment.py --prompt judge_v1 --set held_out --final
    python3 experiments/prompt_experiment.py --prompt judge_v2 --set held_out --final
    python3 experiments/prompt_experiment.py --prompt judge_v1 --set development --summarize

Guards: every posting in the set needs a hand label first; the held-out set runs only with
--final, only once per prompt, and only when both prompt files are committed unchanged.
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from experiments import harness, scoring  # noqa: E402
from jobwatch import transports  # noqa: E402

OUT = harness.ROOT / "experiments" / "prompt-experiment"
PROMPTS = ("judge_v1", "judge_v2")


def prompts_frozen():
    prompts = harness.ROOT / "prompts"
    tracked = subprocess.run(["git", "-C", str(prompts), "ls-files", *[f"{p}.md" for p in PROMPTS]],
                             capture_output=True, text=True).stdout.split()
    changed = subprocess.run(["git", "-C", str(prompts), "status", "--porcelain", "--", "."],
                             capture_output=True, text=True).stdout.strip()
    return len(tracked) == len(PROMPTS) and not changed


def summarize(run_dir, ids, prompt, set_name):
    resume, postings = harness.persona(), harness.baseline_postings()
    calls = harness.read_calls(run_dir / "calls.jsonl")
    summary = scoring.score(calls, scoring.load_hand_labels(harness.HAND_LABELS, ids),
                            harness.rule_verdicts(resume, postings, ids))
    summary.update(prompt=prompt, set=set_name, posting_ids=ids)
    harness.write_json(run_dir / "summary.json", summary)
    print(f"{prompt} on {set_name}: {summary['passed']}/{summary['calls']} calls pass "
          f"({summary['valid']} valid); {summary['postings_all_calls_passed']}/{summary['postings']} postings pass every call")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", choices=PROMPTS, required=True)
    parser.add_argument("--set", choices=("development", "held_out"), required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--judge", choices=transports.CHOICES, default=transports.DEFAULT)
    parser.add_argument("--model", default=transports.DEFAULT_MODEL)
    parser.add_argument("--final", action="store_true", help="required for the held-out set")
    parser.add_argument("--summarize", action="store_true", help="only rescore saved calls")
    args = parser.parse_args()

    ids = harness.selection()[args.set]
    run_dir = OUT / f"{args.prompt}__{args.set}"
    scoring.load_hand_labels(harness.HAND_LABELS, ids)  # labels first, or stop here
    if not args.summarize:
        if args.set == "held_out" and not args.final:
            sys.exit("the held-out set runs only once, at the end: add --final")
        if args.set == "held_out" and not prompts_frozen():
            sys.exit("commit prompts/judge_v1.md and prompts/judge_v2.md unchanged before the held-out run")
        if (run_dir / "calls.jsonl").exists():
            sys.exit(f"{run_dir} already has calls; each prompt runs once per set")
        postings = harness.baseline_postings()
        jobs = [(postings[i], args.prompt, k) for k in range(1, args.repeats + 1) for i in ids]
        run_dir.mkdir(parents=True, exist_ok=True)
        harness.write_json(run_dir / "session.json", {"started_at": harness.now(), "judge": args.judge,
                                                        "model": args.model, "prompt": args.prompt, "set": args.set,
                                                        "repeats": args.repeats, "posting_ids": ids,
                                                        "git": harness.git_state()})
        harness.run_calls(jobs, judge_name=args.judge, model=args.model, workers=args.workers,
                          out_path=run_dir / "calls.jsonl")
    summarize(run_dir, ids, args.prompt, args.set)


if __name__ == "__main__":
    main()
