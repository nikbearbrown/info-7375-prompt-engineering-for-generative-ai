"""Sampling Report (Chapter 1): repeated, independent judge-v1 calls.

Each call is a separate stateless Messages API request: same system prompt,
same resume.json, same posting text, same pinned model. No conversation
history is carried between calls, so any difference comes from the model's
own generation randomness. Every call, including failed ones, is saved to
logs/sampling_raw/<posting_id>_<call_n>.json. Existing files are never
overwritten: re-running adds calls with the next free numbers.

    python3 scripts/sample_judge.py            # 4 calls per posting
    python3 scripts/sample_judge.py --calls 5
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import judge  # noqa: E402

BASELINE = ROOT / "evidence" / "gitlab_jobs_20261030T201528Z.json"
RAW_DIR = ROOT / "logs" / "sampling_raw"
SAMPLE_IDS = [8860219002, 8716143002, 8860273002, 8783485002, 8918216002]
COMPARE_IDS = {9999999002, 8704363002, 8883003002, 8565469002,
               8621733002, 8738179002, 8646544002}


def next_call_number(posting_id):
    taken = [int(p.stem.split("_")[1]) for p in RAW_DIR.glob(f"{posting_id}_*.json")]
    return max(taken, default=0) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls", type=int, default=4)
    args = ap.parse_args()
    assert not COMPARE_IDS & set(SAMPLE_IDS), "sample overlaps the compare set"

    try:
        client = judge.get_client()
    except judge.MissingAPIKey as e:
        print(f"STOPPED: {e}", file=sys.stderr)
        return 2

    resume = json.loads((ROOT / "resume.json").read_text())
    jobs = {j["id"]: j for j in json.loads(BASELINE.read_bytes())["jobs"]}
    postings = [jobs[i] for i in SAMPLE_IDS]
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Round-robin over postings, so a posting's calls aren't back to back.
    for _ in range(args.calls):
        for p in postings:
            n = next_call_number(p["id"])
            r = judge.judge(p, resume, client)
            r.update(call_n=n, posting_title=p["title"].strip(),
                     system_prompt=judge.SYSTEM_PROMPT,
                     user_message=judge.build_user_message(p, resume))
            path = RAW_DIR / f"{p['id']}_{n}.json"
            path.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
            print(f"{path.relative_to(ROOT)}: {r['status']} {r['verdict']} ({r['served_model']})")
    print("\nnext: python3 scripts/summarize_sampling.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
