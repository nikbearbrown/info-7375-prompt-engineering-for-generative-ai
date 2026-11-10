"""Sampling report (Chapter 1): ask Claude the same prompt contract about each
posting several times, each in a fresh session, and tabulate every verdict next
to the hand label. Repeated verdicts show repeatability, not correctness.

    python3 -m tools.sample --ids 111 222 333 444 555 --times 4
"""
import argparse
import collections
import csv
import json
from pathlib import Path

from agent import claude_judge, resume

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "runs" / "2026-10-30T063746Z" / "raw.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="+", required=True)
    ap.add_argument("--times", type=int, default=4)
    ap.add_argument("--prompt", default=str(ROOT / "prompts" / "baseline.txt"))
    args = ap.parse_args()

    jobs = {str(j["id"]): j for j in json.loads(RAW.read_text())["jobs"]}
    labels = {r["posting_id"]: r["my_label"] for r in csv.DictReader(open(ROOT / "labels" / "sheet.csv"))}
    r = resume.load(ROOT / "examples" / "rohan-desai.resume.example.json")
    log = ROOT / "logs" / "sampling.jsonl"

    rows = []
    for pid in args.ids:
        for i in range(1, args.times + 1):
            e = claude_judge.judge(jobs[pid], r, args.prompt, log, tag=f"sample {pid} #{i}")
            print(f"{pid} #{i}: {e['verdict'] if e['valid'] else 'INVALID: ' + e['rejected_because']}")
            rows.append(e)

    out = ["| posting | title | my label | Claude verdicts (fresh calls) | agree with me |",
           "|---|---|---|---|---|"]
    for pid in args.ids:
        vs = [e["verdict"] if e["valid"] else "invalid" for e in rows if str(e["posting_id"]) == pid]
        c = collections.Counter(vs)
        mine = labels.get(pid) or "(unlabeled)"
        out.append(f"| {pid} | {jobs[pid]['title'].strip()} | {mine} | "
                   f"{', '.join(vs)} ({', '.join(f'{k}: {n}' for k, n in c.items())}) | {sum(v == mine for v in vs)}/{len(vs)} |")
    table = "\n".join(out)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "sampling_table.md").write_text(table + "\n")
    print("\n" + table)


if __name__ == "__main__":
    main()
