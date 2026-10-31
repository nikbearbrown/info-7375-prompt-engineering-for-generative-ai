"""Sampling report (Chapter 1): ask Claude the prompt contract about each of the 5 sampling
postings in fresh conversations, several times each, and record every verdict.

    python3 experiments/sample.py --repeats 4          # make the calls (live, uses Claude)
    python3 experiments/sample.py --summarize          # rescore saved calls, no Claude calls

Writes experiments/sampling/calls.jsonl (every reply, verbatim) and summary.json.
Hand labels must exist for the 5 postings before any call is made.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from experiments import harness, scoring  # noqa: E402
from jobwatch import transports  # noqa: E402

OUT = harness.ROOT / "experiments" / "sampling"
PROMPT = "judge_v1"


def summarize(ids):
    resume, postings = harness.persona(), harness.baseline_postings()
    calls = harness.read_calls(OUT / "calls.jsonl")
    summary = scoring.score(calls, scoring.load_hand_labels(harness.HAND_LABELS, ids),
                            harness.rule_verdicts(resume, postings, ids))
    summary.update(prompt=PROMPT, posting_ids=ids, titles={i: postings[i].title for i in ids})
    harness.write_json(OUT / "summary.json", summary)
    print(f"{summary['calls']} calls, {summary['valid']} valid, {summary['passed']} match the hand label")
    for posting_id, entry in summary["per_posting"].items():
        print(f"  {posting_id}: hand {entry['hand_label']}, rule {entry['rule_verdict']}, Claude {entry['verdicts']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--judge", choices=transports.CHOICES, default=transports.DEFAULT)
    parser.add_argument("--model", default=transports.DEFAULT_MODEL)
    parser.add_argument("--summarize", action="store_true", help="only rescore saved calls")
    args = parser.parse_args()

    ids = harness.selection()["sampling"]
    scoring.load_hand_labels(harness.HAND_LABELS, ids)  # labels first, or stop here
    if not args.summarize:
        if (OUT / "calls.jsonl").exists():
            sys.exit(f"{OUT / 'calls.jsonl'} already exists; refusing to mix two sampling sessions")
        postings = harness.baseline_postings()
        jobs = [(postings[i], PROMPT, k) for k in range(1, args.repeats + 1) for i in ids]
        OUT.mkdir(parents=True, exist_ok=True)
        harness.write_json(OUT / "session.json", {"started_at": harness.now(), "judge": args.judge, "model": args.model,
                                                    "prompt": PROMPT, "repeats": args.repeats, "posting_ids": ids,
                                                    "git": harness.git_state()})
        harness.run_calls(jobs, judge_name=args.judge, model=args.model, workers=args.workers, out_path=OUT / "calls.jsonl")
    summarize(ids)


if __name__ == "__main__":
    main()
