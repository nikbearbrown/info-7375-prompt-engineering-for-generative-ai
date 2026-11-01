"""Turn saved Claude calls + Hemanth's hand labels into the numbers in the reports.

    python scripts/analyze.py sampling
    python scripts/analyze.py experiment dev        # or heldout
Nothing here calls Claude; it only reads saved files.
"""
import csv
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from jsagent import claude_judge, resume as resume_mod  # noqa: E402

labels = {int(r["id"]): r for r in csv.DictReader(open(ROOT / "experiment" / "labels.csv"))}
jobs = {j["id"]: j for j in json.loads(gzip.decompress((ROOT / "runs/2026-10-31T144337/raw.json.gz").read_bytes()))["jobs"]}
resume = resume_mod.load(ROOT / "persona" / "priya-nair.resume.json")


def load(path):
    return [json.loads(line) for line in open(ROOT / path)]


def grounded(r):
    """Recompute the quote check with the prompt Claude saw (see FRICTIONAL: the first check had false alarms)."""
    prompt = claude_judge.build_prompt(r["prompt_version"], jobs[r["posting_id"]], resume)
    return claude_judge.ungrounded_quotes(r["judgment"]["justification"], jobs[r["posting_id"]], resume, prompt)


def sampling():
    rows = load("experiment/sampling/calls.jsonl")
    by = {}
    for r in rows:
        by.setdefault(r["posting_id"], []).append(r)
    print("| id | title | hand label | rule (record) | Claude verdicts, 4 fresh calls (confidence) | agreement with modal | modal = hand label? |")
    print("|---|---|---|---|---|---|---|")
    for pid, rs in by.items():
        rs.sort(key=lambda r: r["attempt"])
        verdicts = [r["judgment"]["verdict"] if r["valid"] else "INVALID" for r in rs]
        modal, n = Counter(verdicts).most_common(1)[0]
        hand = labels[pid]["hand_label"] or "(not labeled)"
        cells = ", ".join(f"{v} ({r['judgment']['confidence']})" if r["valid"] else v for v, r in zip(verdicts, rs))
        print(f"| {pid} | {rs[0]['title']} | {hand} | {rs[0]['rule_verdict']} | {cells} | {n}/{len(rs)} | {'yes' if modal == hand else 'no'} |")
    ung = [(r["posting_id"], r["attempt"], grounded(r)) for r in rows if r["valid"] and grounded(r)]
    print(f"\nvalid answers: {sum(r['valid'] for r in rows)}/{len(rows)}; models: {sorted({m for r in rows for m in r['models_used']})}; "
          f"calls started {min(r['started_at'] for r in rows)} to {max(r['started_at'] for r in rows)}; ungrounded quotes: {ung or 'none'}")


def experiment(set_name):
    rows = load(f"experiment/results_{set_name}.jsonl")
    ids = [pid for pid, l in labels.items() if l["set"] == set_name]
    missing = [pid for pid in ids if not labels[pid]["hand_label"]]
    if missing:
        sys.exit(f"hand labels missing for {missing}")
    print(f"| id | title | hand label | rule (record) | " + " | ".join(f"Claude {v}" for v in ("v1", "v2")) + " |")
    print("|---|---|---|---|---|---|")
    res = {(r["posting_id"], r["prompt_version"]): r for r in rows}
    score = Counter()
    rule_agree = 0
    for pid in ids:
        hand = labels[pid]["hand_label"]
        cells = []
        for v in ("v1", "v2"):
            r = res[(pid, v)]
            verdict = r["judgment"]["verdict"] if r["valid"] else "INVALID"
            ok = verdict == hand
            score[v] += ok
            cells.append(f"{verdict} ({r['judgment']['confidence']}) {'✓' if ok else '✗'}" if r["valid"] else "INVALID ✗")
        rv = rows[0] and next(r["rule_verdict"] for r in rows if r["posting_id"] == pid)
        rule_agree += rv == hand
        print(f"| {pid} | {labels[pid]['title']} | {hand} | {rv} {'✓' if rv == hand else '✗'} | " + " | ".join(cells) + " |")
    n = len(ids)
    print(f"\npass rate vs hand label: v1 {score['v1']}/{n}, v2 {score['v2']}/{n}; rule code vs hand label {rule_agree}/{n}")
    print(f"valid answers {sum(r['valid'] for r in rows)}/{len(rows)}; models {sorted({m for r in rows for m in r['models_used']})}; "
          f"calls started {min(r['started_at'] for r in rows)} to {max(r['started_at'] for r in rows)}")
    ung = [(r["posting_id"], r["prompt_version"], grounded(r)) for r in rows if r["valid"] and grounded(r)]
    print(f"ungrounded quotes: {ung or 'none'}")


if __name__ == "__main__":
    sampling() if sys.argv[1] == "sampling" else experiment(sys.argv[2])
