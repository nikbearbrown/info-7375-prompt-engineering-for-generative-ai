"""EXPERIMENT-PLAN.md section 2: baseline vs revision, one call per posting per prompt.

    python3 experiments/run_prompt_experiment.py --set development          # OFFLINE plan
    python3 experiments/run_prompt_experiment.py --set development --live   # 20 live calls

Each call is a fresh claude -p conversation on the 12:40 ET Oct 26 saved
description. Every reply is saved to runs/experiment/<set>/, accepted or
rejected, and never repaired. The held-out set must be named explicitly.
"""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import judge  # noqa: E402
import persona  # noqa: E402
from run_sampling import saved_posting  # noqa: E402

PROMPTS = {"baseline": ROOT / "prompts" / "judge-baseline.txt",
           "revision": ROOT / "prompts" / "judge-revision.txt"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", required=True, choices=("development", "held_out"))
    parser.add_argument("--live", action="store_true", help="actually call Claude")
    args = parser.parse_args(argv)
    selection = json.loads((ROOT / "labels" / "selection.json").read_text(encoding="utf-8"))
    _, targets = persona.load_persona()
    out_dir = ROOT / "runs" / "experiment" / args.set
    for posting_id in selection[args.set]:
        posting = saved_posting(posting_id)
        for name, prompt_path in PROMPTS.items():
            if not args.live:
                print(f"OFFLINE plan: {args.set} {posting_id} {name}")
                continue
            record = judge.judge_posting(posting, targets, live=True, prompt_path=prompt_path)
            record.update(experiment=f"prompt experiment (EXPERIMENT-PLAN.md section 2), {args.set}",
                          prompt_name=name)
            path = judge.save_record(record, out_dir / name)
            verdict = (record.get("judge_output") or {}).get("verdict")
            print(f"{posting_id} {name}: {record['status']} {verdict} -> {path.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
