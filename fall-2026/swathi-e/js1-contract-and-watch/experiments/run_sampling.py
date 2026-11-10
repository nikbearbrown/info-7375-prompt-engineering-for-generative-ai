"""EXPERIMENT-PLAN.md section 1: the sampling report's 20 judge calls.

    python3 experiments/run_sampling.py          # OFFLINE: list the planned calls, call nothing
    python3 experiments/run_sampling.py --live   # 5 postings x 4 fresh claude -p conversations

Baseline prompt, pinned model, the 12:40 ET Oct 26 saved descriptions. Every
reply is saved to runs/sampling/, accepted or rejected, and never repaired.
"""
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import judge  # noqa: E402
import persona  # noqa: E402

POSTINGS = (8546367002, 8760167002, 8735590002, 8199399002, 8692962002)
CALLS_PER_POSTING = 4
SNAPSHOT = "2026-10-26T12-4"
OUT_DIR = ROOT / "runs" / "sampling"


def saved_posting(posting_id):
    [raw] = sorted((ROOT / "runs" / "postings").glob(f"databricks_job_{posting_id}_{SNAPSHOT}*-0400.json"))
    return judge.load_posting(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--live", action="store_true", help="actually call Claude")
    args = parser.parse_args(argv)
    _, targets = persona.load_persona()
    for posting_id in POSTINGS:
        posting = saved_posting(posting_id)
        for call in range(1, CALLS_PER_POSTING + 1):
            if not args.live:
                print(f"OFFLINE plan: {posting_id} call {call} from {posting['raw_file']}")
                continue
            record = judge.judge_posting(posting, targets, live=True)
            record.update(experiment="sampling report (EXPERIMENT-PLAN.md section 1)", sampling_call=call)
            path = judge.save_record(record, OUT_DIR)
            verdict = (record.get("judge_output") or {}).get("verdict")
            print(f"{posting_id} call {call}: {record['status']} {verdict} -> {path.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
