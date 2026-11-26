"""JS3 Step 3: draw the reject-audit sample from runs/filter-v1.2/results.jsonl and write audit/audit.csv for Ethan to judge.

Three groups, drawn with a fixed seed before anyone looks at them:
- random_reject: 30 rejects drawn uniformly at random from ALL rejects (most will be easy; that is what "random" shows)
- closest_call: every posting the filter marks as a closest call (FILTER.md section 1), rejected or kept
- kept: up to 10 kept postings drawn at random (all of them if fewer)

    python3 scripts/make_audit_sheet.py
"""
import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "runs" / "filter-v1.2" / "results.jsonl"
AUDIT = ROOT / "audit" / "audit.csv"
SEED, N_RANDOM, N_KEPT = 7375, 30, 10
FIELDS = ["n", "group", "board", "posting_id", "title", "location", "filter_bucket", "filter_reason", "filter_evidence",
          "ethan_verdict", "ethan_note"]


def reason(r):
    bad = [(k, v) for k, v in r["rules"].items() if v["result"] != "pass"]
    if not bad:
        return f"kept, score {r['score']}", "; ".join(r["topic_words"])
    return "; ".join(f"{k} {v['result']}: {v['why']}" for k, v in bad), " | ".join(v["span"] for _, v in bad if v["span"])


def main():
    if AUDIT.exists():
        sys.exit(f"refused: {AUDIT.relative_to(ROOT)} already exists; audit verdicts are never overwritten")
    results = [json.loads(line) for line in RESULTS.open()]
    rng = random.Random(SEED)
    rejects = sorted((r for r in results if r["bucket"] == "rejected"), key=lambda r: (r["board"], r["id"]))
    kept = sorted((r for r in results if r["bucket"] == "kept"), key=lambda r: (r["board"], r["id"]))
    close = sorted((r for r in results if r["closest_call"]), key=lambda r: (r["board"], r["id"]))
    rows = [("random_reject", r) for r in rng.sample(rejects, min(N_RANDOM, len(rejects)))]
    rows += [("closest_call", r) for r in close]
    rows += [("kept", r) for r in rng.sample(kept, min(N_KEPT, len(kept)))]
    AUDIT.parent.mkdir(exist_ok=True)
    with AUDIT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for i, (group, r) in enumerate(rows, 1):
            why, ev = reason(r)
            w.writerow({"n": i, "group": group, "board": r["board"], "posting_id": r["id"], "title": r["title"],
                        "location": r["location"], "filter_bucket": r["bucket"], "filter_reason": why, "filter_evidence": ev,
                        "ethan_verdict": "", "ethan_note": ""})
    counts = {g: sum(1 for x, _ in rows if x == g) for g in ("random_reject", "closest_call", "kept")}
    print(f"wrote {AUDIT.relative_to(ROOT)}: {counts} (of {len(rejects)} rejects, {len(close)} closest calls, {len(kept)} kept)")


if __name__ == "__main__":
    main()
