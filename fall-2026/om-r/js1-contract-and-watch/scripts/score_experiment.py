"""Score saved Prompt Experiment calls against the saved hand labels.
Reads files only; makes no API calls.

    python3 scripts/score_experiment.py --set dev --prompt judge-dev-v0

Pass = a valid judgment whose verdict equals the hand label. An unavailable
judgment (invalid or errored) counts as a miss and is listed separately.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from agent import judge  # noqa: E402
from experiment_common import RAW_ROOT, read_labels, split_ids  # noqa: E402


def cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["dev", "heldout"], required=True)
    ap.add_argument("--prompt", choices=sorted(judge.PROMPTS), required=True)
    args = ap.parse_args()

    labels = read_labels(args.set)
    raw_dir = RAW_ROOT / args.prompt / args.set
    rows, missing = [], []
    for pid in split_ids(args.set):
        path = raw_dir / f"{pid}.json"
        if not path.exists():
            missing.append(pid)
            continue
        rows.append((pid, json.loads(path.read_text()), *labels[pid]))
    if missing:
        print(f"NOT SCORED: no saved call for {missing} in {raw_dir.relative_to(ROOT)}", file=sys.stderr)
        return 2

    passes = [r for r in rows if r[1]["status"] == "ok" and r[1]["verdict"] == r[2]]
    unavailable = [r for r in rows if r[1]["status"] != "ok"]
    disagree = [r for r in rows if r[1]["status"] == "ok" and r[1]["verdict"] != r[2]]
    shas = {r[1].get("system_prompt_sha256") for r in rows}

    lines = [f"# Prompt Experiment results: {args.prompt} on the {args.set.upper()} set", "",
             f"- pass rate: **{len(passes)} / {len(rows)}** (judgment verdict equals the hand label)",
             f"- disagreements: {len(disagree)}; unavailable judgments: {len(unavailable)}",
             f"- hand labels: {sum(v == 'relevant' for _, _, v, _ in rows)} relevant, "
             f"{sum(v == 'not relevant' for _, _, v, _ in rows)} not relevant",
             f"- model(s) served: {', '.join(sorted({r[1]['served_model'] or 'n/a' for r in rows}))}",
             f"- system prompt sha256: {', '.join(sorted(s or 'n/a' for s in shas))}"
             + ("" if len(shas) == 1 else "  **(MORE THAN ONE PROMPT - not comparable)**"), "",
             "| posting | title | hand label | judgment | match |", "|---|---|---|---|---|"]
    for pid, r, label, _ in rows:
        j = r["verdict"] or f"UNAVAILABLE ({r['status']})"
        lines.append(f"| {pid} | {cell(r['posting_title'])} | {label} | {j} | "
                     f"{'yes' if r in [x[1] for x in passes] else 'NO'} |")
    for title, group in (("Disagreements", disagree), ("Unavailable", unavailable)):
        if not group:
            continue
        lines += ["", f"## {title}", ""]
        for pid, r, label, reason in group:
            lines += [f"### {pid}: {r['posting_title']}", "",
                      "| | verdict | stated reason |", "|---|---|---|",
                      f"| Om (hand label) | {label} | {cell(reason)} |",
                      f"| Claude (JUDGMENT, {args.prompt}) | {r['verdict'] or 'UNAVAILABLE'} | "
                      f"{cell(r['justification'] or r['error'])} |", ""]
    out = ROOT / "logs" / f"experiment_results_{args.prompt}_{args.set}.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nsaved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
