"""Run the Claude judge many times, each call a fresh conversation, and save every call.

    # sampling report: 5 postings x 4 fresh calls, prompt v1
    python scripts/claude_batch.py sample experiment/sampling/calls.jsonl 5436697008 4935314008 ...
    # prompt experiment: every posting in one set, once per prompt version
    python scripts/claude_batch.py experiment experiment/results_dev.jsonl --set dev --versions v1 v2

Postings come from the live baseline raw response; the résumé is the persona. Calls run
4 at a time; each is a separate `claude -p` process with no session saved.
"""
import argparse
import csv
import gzip
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from jsagent import claude_judge, resume as resume_mod, rule  # noqa: E402

RAW = ROOT / "runs" / "2026-10-31T144337" / "raw.json.gz"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["sample", "experiment"])
    p.add_argument("out")
    p.add_argument("ids", nargs="*", type=int)
    p.add_argument("--repeats", type=int, default=4)
    p.add_argument("--set", dest="set_name")
    p.add_argument("--versions", nargs="+", default=["v1"])
    a = p.parse_args()

    jobs = {j["id"]: j for j in json.loads(gzip.decompress(RAW.read_bytes()))["jobs"]}
    resume = resume_mod.load(ROOT / "persona" / "priya-nair.resume.json")
    if a.mode == "sample":
        tasks = [(pid, "v1", k + 1) for pid in a.ids for k in range(a.repeats)]
    else:
        with open(ROOT / "experiment" / "labels.csv") as f:
            ids = [int(r["id"]) for r in csv.DictReader(f) if r["set"] == a.set_name]
        tasks = [(pid, v, 1) for v in a.versions for pid in ids]

    def one(task):
        pid, version, attempt = task
        rec = claude_judge.judge(jobs[pid], resume, version=version)
        rec.update(attempt=attempt, title=jobs[pid]["title"].strip(), rule_verdict=rule.judge(jobs[pid], resume)["verdict"])
        return rec

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool, open(out, "x") as f:   # "x": never overwrite
        for rec in pool.map(one, tasks):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            j = rec["judgment"] or {}
            print(rec["posting_id"], rec["prompt_version"], rec["attempt"], rec["valid"], j.get("verdict"), j.get("confidence"), flush=True)


if __name__ == "__main__":
    main()
