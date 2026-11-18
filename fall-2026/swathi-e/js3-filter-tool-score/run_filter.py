"""Apply the filter to every posting of one saved collection run (offline).

    python3 run_filter.py runs/<run id>

For each board in the run's trace.json, it takes the raw response of that
board's successful request, checks its sha256 against the trace, parses it with
descriptions, and evaluates every posting. Boards that failed in the run are
listed as failed, with no postings. The results are written once (never
overwritten) to runs/filter-<run id>/results.json, with a reference to the run,
each raw file and its sha256, and the sha256 of FILTER.md, job_filter.py,
descriptions.py and parsers.py, so the results can be recomputed.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import job_filter
import parsers
import policy as policy_module

HERE = Path(__file__).resolve().parent
VERDICTS = ("shortlisted", "not shortlisted", "rejected", "I cannot tell")


class EvidenceError(Exception):
    pass


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def filter_run(run_dir, pol):
    run_dir = pol.check_read(run_dir)
    trace = json.loads(pol.check_read(run_dir / "trace.json").read_text(encoding="utf-8"))
    boards, results = {}, []
    for name, board in trace["boards"].items():
        if board["status"] != "ok":
            boards[name] = {"status": board["status"], "reason": board["reason"], "raw_file": None, "postings": 0}
            continue
        obs = [o for o in trace["trace"] if o["board"] == name and o["action"] in ("request", "retry")
               and o.get("status") == 200 and o.get("raw_file")][-1]
        raw = pol.check_read(obs["raw_file"])
        if sha256(raw) != obs["sha256"]:
            raise EvidenceError(f"{obs['raw_file']}: sha256 does not match the trace")
        postings, unlisted = parsers.PARSERS[board["system"]](raw.read_bytes(), include_description=True)
        boards[name] = {"status": "ok", "raw_file": obs["raw_file"], "raw_sha256": obs["sha256"],
                        "postings": len(postings), "unlisted_skipped": unlisted}
        for p in postings:
            res = job_filter.evaluate(p)
            results.append({"board": name, "posting_id": p["id"], "title": p["title"], "location": p["location"],
                            "url": p["url"], "verdict": res["verdict"], "score": res["score"], "reason": res["reason"],
                            "points": res["points"], "rules": res["rules"], "claims": res["claims"],
                            "raw_file": obs["raw_file"]})
    counts = {name: dict(Counter(r["verdict"] for r in results if r["board"] == name)) for name in boards}
    shortlist = [{"board": e["board"], "posting_id": e["posting_id"], "title": e["title"], "score": e["score"]}
                 for e in job_filter.order_shortlist([{**r, "id": r["posting_id"]} for r in results])]
    return {
        "label": f"record: filter v1 applied offline to the saved LIVE collection run {trace['run_id']}",
        "source_run": {"run_id": trace["run_id"], "trace": (run_dir / "trace.json").relative_to(pol.root).as_posix(),
                       "trace_sha256": sha256(run_dir / "trace.json"), "exit": trace["exit"]},
        "code": {f: sha256(HERE / f) for f in ("FILTER.md", "job_filter.py", "descriptions.py", "parsers.py")},
        "boards": boards,
        "verdict_counts": {"per_board": counts, "overall": dict(Counter(r["verdict"] for r in results))},
        "shortlist": shortlist,
        "results": results,
    }


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    pol = policy_module.Policy(HERE)
    run_dir = Path(argv[0])
    out = filter_run(run_dir, pol)
    path = pol.write_evidence(Path("runs") / f"filter-{run_dir.name}" / "results.json",
                              json.dumps(out, indent=2, ensure_ascii=False).encode("utf-8"))
    print(out["label"])
    for name, b in out["boards"].items():
        print(f"- {name}: {b['status']}, {b['postings']} postings, verdicts {out['verdict_counts']['per_board'][name]}")
    print("overall:", out["verdict_counts"]["overall"])
    print("results:", path.relative_to(pol.root).as_posix())


if __name__ == "__main__":
    main()
