"""Ask Claude (fresh `claude -p` conversation per call) about labeled postings; save every reply.

    python3 -m experiments.run_claude --prompt v1_baseline.md --set sampling --repeats 4 --out experiments/results/sampling.jsonl
    python3 -m experiments.run_claude --prompt v1_baseline.md --set dev --out experiments/results/v1_dev.jsonl
"""

import argparse
import csv
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from jsagent import claude_judge

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "snapshots" / "databricks-2026-10-31T233230Z-live.json"


def load_rows(which):
    rows = list(csv.DictReader(open(ROOT / "labels" / "hand_labels.csv")))
    if which == "sampling":
        return [r for r in rows if r["sampling"] == "True"]
    return [r for r in rows if r["set"] == which]


def one_call(args):
    row, posting, resume, prompt, model, attempt = args
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        v, raw, err = claude_judge.judge(posting, resume, prompt, model)
    except Exception as e:  # a failed call is recorded, never retried silently
        v, raw, err = None, "", f"call failed: {e}"
    return {"called_at": started, "model": model, "prompt": prompt, "n": int(row["n"]), "id": posting["id"],
            "attempt": attempt, "hand_label": row["label"], "verdict": v["verdict"] if v else None,
            "rejected": err, "agrees": bool(v) and v["verdict"] == row["label"],
            "justification": v["justification"] if v else None, "session_id": v["session_id"] if v else None,
            "raw_reply": raw}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--set", required=True, choices=["sampling", "dev", "heldout"])
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--model", default=claude_judge.MODEL)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    jobs = {j["id"]: j for j in json.loads(SNAPSHOT.read_text())["jobs"]}
    resume = json.loads((ROOT / "persona" / "arya-sahni.json").read_text())
    rows = load_rows(a.set)
    tasks = [(r, jobs[int(r["id"])], resume, a.prompt, a.model, k + 1) for r in rows for k in range(a.repeats)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(one_call, tasks))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256((claude_judge.PROMPTS / a.prompt).read_bytes()).hexdigest()[:12]
    with out.open("w") as f:
        for r in results:
            f.write(json.dumps({**r, "prompt_sha256_12": sha}, ensure_ascii=False) + "\n")
    agree = sum(r["agrees"] for r in results)
    rejected = sum(r["verdict"] is None for r in results)
    print(f"{a.prompt} on {a.set}: {agree}/{len(results)} agree with hand labels, {rejected} rejected by validator")
    for r in results:
        print(f"  #{r['n']:>2} try {r['attempt']}: claude={r['verdict'] or 'REJECTED'} hand={r['hand_label']}")


if __name__ == "__main__":
    main()
