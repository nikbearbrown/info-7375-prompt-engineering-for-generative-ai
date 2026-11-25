"""Prompt experiment (Chapter 2): run one prompt over one labeled set, once per
posting, and score it against the hand labels in labels/sheet.csv.

    python3 -m tools.experiment --prompt prompts/baseline.txt --set dev
    python3 -m tools.experiment --prompt prompts/revision.txt --set dev
    # only at the very end, once per prompt:
    python3 -m tools.experiment --prompt prompts/baseline.txt --set held-out --final
"""
import argparse
import csv
import json
from pathlib import Path

from agent import claude_judge, resume

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "runs" / "2026-10-30T063746Z" / "raw.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--set", choices=["dev", "held-out"], required=True)
    ap.add_argument("--final", action="store_true", help="required for the held-out set")
    args = ap.parse_args()
    if args.set == "held-out" and not args.final:
        raise SystemExit("held-out is run once, at the end: add --final when you are done with dev")

    rows = [r for r in csv.DictReader(open(ROOT / "labels" / "sheet.csv")) if r["set"] == args.set]
    missing = [r["posting_id"] for r in rows if r["my_label"] not in {"relevant", "not relevant"}]
    if missing:
        raise SystemExit(f"hand labels missing or invalid for: {missing}")

    jobs = {str(j["id"]): j for j in json.loads(RAW.read_text())["jobs"]}
    r = resume.load(ROOT / "examples" / "rohan-desai.resume.example.json")
    name = Path(args.prompt).stem
    log = ROOT / "logs" / f"experiment_{name}_{args.set}.jsonl"

    results = []
    for row in rows:
        e = claude_judge.judge(jobs[row["posting_id"]], r, args.prompt, log, tag=f"experiment {name} {args.set}")
        ok = e["valid"] and e["verdict"] == row["my_label"]
        results.append({"posting_id": row["posting_id"], "title": row["title"], "my_label": row["my_label"],
                        "claude": e["verdict"] if e["valid"] else "invalid", "pass": ok})
        print(f"{'PASS' if ok else 'FAIL'} {row['posting_id']} mine={row['my_label']} claude={results[-1]['claude']}")

    passed = sum(x["pass"] for x in results)
    summary = {"prompt": Path(args.prompt).name, "set": args.set, "passed": passed, "total": len(results),
               "model": claude_judge.MODEL, "results": results}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / f"experiment_{name}_{args.set}.json").write_text(json.dumps(summary, indent=2))
    print(f"\n{name} on {args.set}: {passed}/{len(results)} match my labels")


if __name__ == "__main__":
    main()
