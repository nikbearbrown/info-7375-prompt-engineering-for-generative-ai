"""Score the prompt experiment with EXPERIMENT-PLAN.md's measures (no Claude, no network).

    python3 experiments/score_experiment.py --set development

A: the reply was accepted and its verdict equals my label.
B: for 8760167002, authorization_found is a quote that is not the Compliance
   paragraph and mentions citizenship or clearance; for every other posting it
   is exactly "none stated".
A rejected, failed, missing or duplicated reply counts as wrong on both.
"""
import argparse
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REAL_REQUIREMENT = 8760167002
COMPLIANCE_START = "If access to export-controlled technology"
PROMPTS = ("baseline", "revision")


def measure_b(posting_id, quote):
    if posting_id == REAL_REQUIREMENT:
        return (quote != "none stated" and not quote.startswith(COMPLIANCE_START)
                and any(word in quote.lower() for word in ("citizenship", "clearance")))
    return quote == "none stated"


def score(set_name):
    selection = json.loads((ROOT / "labels" / "selection.json").read_text(encoding="utf-8"))
    with (ROOT / "labels" / "LABELS.csv").open(encoding="utf-8-sig", newline="") as f:
        labels = {int(r["posting_id"]): r["my_label"].replace(" ", "_") for r in csv.DictReader(f)}
    results = {}
    for name in PROMPTS:
        records = [json.loads(p.read_text(encoding="utf-8"))
                   for p in sorted((ROOT / "runs" / "experiment" / set_name / name).glob("*.json"))]
        rows = []
        for posting_id in selection[set_name]:
            mine = [r for r in records if r["posting_id"] == posting_id]
            output = mine[0].get("judge_output") if len(mine) == 1 and mine[0]["status"] == "accepted" else None
            rows.append({"posting_id": posting_id, "my_label": labels[posting_id], "records": len(mine),
                         "status": mine[0]["status"] if len(mine) == 1 else f"{len(mine)} records",
                         "verdict": output and output["verdict"],
                         "authorization_found": output and output["authorization_found"],
                         "A": bool(output) and output["verdict"] == labels[posting_id],
                         "B": bool(output) and measure_b(posting_id, output["authorization_found"])})
        results[name] = {"A": sum(r["A"] for r in rows), "B": sum(r["B"] for r in rows), "n": len(rows), "rows": rows}
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", required=True, choices=("development", "held_out"))
    args = parser.parse_args(argv)
    results = score(args.set)
    (HERE / f"results_{args.set}.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                                                   encoding="utf-8")
    for name, res in results.items():
        print(f"\n{name}: A {res['A']}/{res['n']}  B {res['B']}/{res['n']}")
        print("| posting | my label | status | verdict | A | authorization_found | B |")
        print("|---|---|---|---|---|---|---|")
        for r in res["rows"]:
            quote = r["authorization_found"] or ""
            quote = "Compliance paragraph" if quote.startswith(COMPLIANCE_START) else (quote[:70] + ("…" if len(quote) > 70 else ""))
            print(f"| {r['posting_id']} | {r['my_label']} | {r['status']} | {r['verdict']} | "
                  f"{'yes' if r['A'] else 'no'} | {quote} | {'yes' if r['B'] else 'no'} |")


if __name__ == "__main__":
    main()
