#!/usr/bin/env python3
"""run_claude.py — ask Claude (fresh conversation per call) about a fixed set of postings
and append every reply, accepted or REJECTED, to a JSONL file. Nothing is repaired.

    python3 experiments/run_claude.py --set sampling --prompt baseline --repeats 4 --out experiments/results/sampling.jsonl
    python3 experiments/run_claude.py --set dev      --prompt baseline --repeats 1 --out experiments/results/dev-baseline.jsonl
    python3 experiments/run_claude.py --set held_out --prompt revision --repeats 1 --out experiments/results/heldout-revision.jsonl

Sets come from experiments/selection.json. Then: python3 experiments/score.py
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
import claude_judge  # noqa: E402

SETS = {"sampling": "sampling_5", "dev": "dev", "held_out": "held_out"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--set", choices=SETS, required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--model", default=claude_judge.DEFAULT_MODEL)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--out", required=True)
    a = p.parse_args()

    with open(os.path.join(HERE, "selection.json"), encoding="utf-8") as f:
        sel = json.load(f)
    root = os.path.join(HERE, "..")
    with open(os.path.join(root, sel["raw_file"]), encoding="utf-8") as f:
        jobs = {j["id"]: j for j in json.load(f)["jobs"]}
    with open(os.path.join(root, "persona", "aarav-patel.resume.json"), encoding="utf-8") as f:
        resume = json.load(f)

    tasks = [(pid, r) for pid in sel[SETS[a.set]] for r in range(1, a.repeats + 1)]

    def one(task):
        pid, rep = task
        try:
            rec = claude_judge.judge(jobs[pid], resume, a.prompt, a.model)
        except Exception as e:  # a failed call is data too
            rec = {"posting_id": pid, "status": "CALL_FAILED", "verdict": None, "error": str(e)[:300]}
        rec.update(set=a.set, repeat=rep, asked_at=dt.datetime.now().astimezone().isoformat(timespec="seconds"))
        return rec

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with cf.ThreadPoolExecutor(a.workers) as ex, open(a.out, "a", encoding="utf-8") as out:
        for rec in ex.map(one, tasks):
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"{rec['posting_id']} r{rec['repeat']} {rec['status']:<9} {rec.get('verdict')}")


if __name__ == "__main__":
    main()
