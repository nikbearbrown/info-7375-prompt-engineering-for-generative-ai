"""Measure the pre-registered threshold change 5 -> 6 on the held-out sample (offline).

    python3 measure_heldout.py

Follows HELDOUT-PLAN.md (commit 4cbb88c), run after my labels were committed
(heldout/HELDOUT.csv, commit b09f9ce). For each of the 20 held-out postings it
takes the saved 2026-11-19 raw response (sha256 checked against the trace),
applies filter v1.1 (job_filter.evaluate, unchanged) once, and records the
verdict, score and points. Threshold 6 is applied here, in analysis, to the same
recorded scores: a posting with a score is shortlisted when it has a role match
and score >= threshold. Rejected and "I cannot tell" verdicts have no score and
do not depend on the threshold. Only after the filter has run does it open
heldout/selection.json for the A/B groups. Counts are per group, never pooled.
The result is written once (never overwritten) to runs/heldout-v1.1-threshold-<run id>/measurement.json.
"""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys

import job_filter
import parsers
import policy as policy_module

HERE = Path(__file__).resolve().parent
RUN = Path("runs/2026-11-19T17-31-47-142253-0500")
SHEET = Path("heldout/HELDOUT.csv")
SELECTION = Path("heldout/selection.json")
OUT = Path("runs/heldout-v1.1-threshold-2026-11-19T17-31-47-142253-0500/measurement.json")
THRESHOLDS = (5, 6)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_postings(pol):
    """{(board, posting id): (posting, raw file)} from the saved run, each raw file checked against the trace."""
    trace = json.loads(pol.check_read(RUN / "trace.json").read_text(encoding="utf-8"))
    out = {}
    for name, board in trace["boards"].items():
        if board["status"] != "ok":
            continue
        obs = [o for o in trace["trace"] if o["board"] == name and o["action"] in ("request", "retry")
               and o.get("status") == 200 and o.get("raw_file")][-1]
        raw = pol.check_read(obs["raw_file"])
        assert sha256(raw) == obs["sha256"], obs["raw_file"]
        for p in parsers.PARSERS[board["system"]](raw.read_bytes(), include_description=True)[0]:
            out[(name, str(p["id"]))] = (p, obs["raw_file"])
    return out


def verdict_at(res, threshold):
    if res["score"] is None:
        return res["verdict"]
    role = res["points"]["role"] > 0
    return "shortlisted" if role and res["score"] >= threshold else "not shortlisted"


def counts(rows, threshold):
    k = f"t{threshold}"
    return {
        "shortlisted and relevant": sum(r[k] == "shortlisted" and r["my_verdict"] == "relevant" for r in rows),
        "shortlisted and not relevant": sum(r[k] == "shortlisted" and r["my_verdict"] == "not relevant" for r in rows),
        "relevant but not shortlisted": sum(r[k] != "shortlisted" and r["my_verdict"] == "relevant" for r in rows),
        "filter verdicts": dict(Counter(r[k] for r in rows)),
    }


def main():
    pol = policy_module.Policy(HERE)
    sheet = list(csv.DictReader(pol.check_read(SHEET).read_text(encoding="utf-8").splitlines()))
    assert len(sheet) == 20
    postings = load_postings(pol)

    # 1. the filter, once per held-out posting (selection.json not yet read)
    rows = []
    for s in sheet:
        p, raw_file = postings[(s["board"], s["posting_id"])]
        res = job_filter.evaluate(p)
        rows.append({"row": int(s["row"]), "board": s["board"], "posting_id": s["posting_id"], "title": s["title"],
                     "my_verdict": s["my_verdict"], "verdict_v1.1": res["verdict"], "score": res["score"],
                     "points": res["points"], "reason": res["reason"],
                     "rules": {r: v["result"] for r, v in res["rules"].items()}, "raw_file": raw_file,
                     **{f"t{t}": verdict_at(res, t) for t in THRESHOLDS}})
        assert rows[-1]["t5"] == res["verdict"], "threshold 5 in analysis must equal the committed filter"

    # 2. only now, the group assignment
    selection = json.loads(pol.check_read(SELECTION).read_text(encoding="utf-8"))
    group = {(g["board"], g["posting_id"]): name for name, gs in selection["groups"].items() for g in gs}
    for r in rows:
        r["group"] = group[(r["board"], r["posting_id"])]

    out = {
        "label": "record: filter v1.1 applied offline to the 20 held-out postings; threshold 6 applied in analysis",
        "plan": "HELDOUT-PLAN.md (commit 4cbb88c)",
        "labels": {"file": SHEET.as_posix(), "commit": "b09f9ce", "sha256": sha256(HERE / SHEET)},
        "source_run": {"run": RUN.as_posix(), "trace_sha256": sha256(HERE / RUN / "trace.json")},
        "code": {f: sha256(HERE / f) for f in ("FILTER.md", "job_filter.py", "descriptions.py", "parsers.py",
                                               "measure_heldout.py")},
        "filter": {"version": job_filter.VERSION, "weights": job_filter.WEIGHTS, "topic_max": job_filter.TOPIC_MAX,
                   "committed_threshold": job_filter.THRESHOLD},
        "thresholds": list(THRESHOLDS),
        "per_group": {g: {f"threshold {t}": counts([r for r in rows if r["group"] == g], t) for t in THRESHOLDS}
                      for g in ("A", "B")},
        "changed_only_by_threshold": [{k: r[k] for k in ("group", "row", "board", "posting_id", "score", "t5", "t6")}
                                      for r in rows if r["t5"] != r["t6"]],
        "my_cant_tell": [r["row"] for r in rows if r["my_verdict"] == "can't tell"],
        "filter_cannot_tell": [r["row"] for r in rows if r["verdict_v1.1"] == "I cannot tell"],
        "rows": sorted(rows, key=lambda r: (r["group"], r["row"])),
    }
    pol.write_evidence(OUT, json.dumps(out, indent=2, ensure_ascii=False).encode("utf-8"))

    for g in ("A", "B"):
        print(f"Group {g}:")
        for r in out["rows"]:
            if r["group"] == g:
                print(f"  row {r['row']:>2} {r['board']}/{r['posting_id']} score={r['score']} points={r['points']} "
                      f"t5={r['t5']} t6={r['t6']} mine={r['my_verdict']} | {r['reason']} | {r['title']}")
        for t in THRESHOLDS:
            print(f"  threshold {t}:", out["per_group"][g][f"threshold {t}"])
    print("changed only by threshold:", out["changed_only_by_threshold"])
    print("my can't tell:", out["my_cant_tell"], "| filter I cannot tell rows:", out["filter_cannot_tell"])
    print("written:", OUT.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
