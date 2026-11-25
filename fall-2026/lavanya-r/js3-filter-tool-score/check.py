"""The independent check: does a run report say what its saved evidence says?

It imports NOTHING from agent/. It re-reads the saved raw response bytes,
recounts the jobs with its own few lines of JSON reading, and compares that to
the report's claims. The agent's report is a claim; this is the check.

    python3 -B check.py runs/<run>/report.json            # a JS2 run
    python3 -B check.py --js1 <report.json> --raw <raw.json.gz> --previous-count N

Exit 0 if every check passes, 1 if any fails.
"""

import argparse
import gzip
import json
import pathlib
import sys


def recount(raw_bytes):
    """Count postings in a raw body: a JSON list (Lever) or an object with a
    'jobs' list (Greenhouse, Ashby). None if it is neither."""
    try:
        data = json.loads(raw_bytes)
    except ValueError:
        return None
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and isinstance(data.get("jobs"), list):
        return len(data["jobs"])
    return None


def read_raw(path):
    b = pathlib.Path(path).read_bytes()
    return gzip.decompress(b) if str(path).endswith(".gz") else b


def check_js2(report_path):
    report_path = pathlib.Path(report_path).resolve()
    root = report_path.parents[2]                 # .../js2/runs/<run>/report.json
    r = json.loads(report_path.read_text())
    trace = [json.loads(l) for l in
             (report_path.parent / "trace.jsonl").read_text().splitlines()]
    out = []

    def finding(ok, name, detail):
        out.append(("PASS" if ok else "FAIL", name, detail))

    ok_sum = 0
    for b in r["boards"]:
        tag = f"{b['ats']}/{b['board']}"
        counts = []
        for raw in b["raw"]:
            n = recount(read_raw(root / raw)) if "-http200" in raw else None
            counts.append(n)
        last = counts[-1] if counts else None
        if b["status"] in ("ok", "suspicious_empty"):
            finding(last == b["jobs"], f"{tag} recount",
                    f"report says {b['jobs']} jobs, raw bytes say {last}")
        if last == 0:
            finding(b["status"] != "ok" and b["new_count"] is None,
                    f"{tag} empty board",
                    "raw has 0 jobs; report must flag it, not say "
                    f"'no new jobs' (status={b['status']}, "
                    f"new={b['new_count']})")
        if b["status"] not in ("ok", "suspicious_empty"):
            finding(b["jobs"] is None and b["new_count"] is None,
                    f"{tag} failed board has no invented count",
                    f"status={b['status']}, jobs={b['jobs']}, "
                    f"new={b['new_count']}")
        if b["status"] == "not_found":
            finding(b["attempts"] == 1, f"{tag} 404 not retried",
                    f"attempts={b['attempts']}")
        if b["status"] == "ok" and last is not None:
            ok_sum += last
        # decided from the raw bytes, not from the report's own status
        b["_really_ok"] = bool(last) and b["state_written"] is not False

    finding(ok_sum == r["jobs_total_ok_boards"], "total",
            f"report total {r['jobs_total_ok_boards']}, recount of ok boards "
            f"{ok_sum}")
    bad = [b for b in r["boards"]
           if b["status"] != "skipped_repeat" and not b["_really_ok"]]
    finding(not (r["exit"] == "finished" and bad), "exit honesty",
            f"exit={r['exit']} with {len(bad)} board(s) not fully ok")
    n_req = sum(1 for e in trace if e["event"] == "request")
    finding(n_req <= r["limits"]["requests"]
            and n_req == r["budget_used"]["requests"],
            "request budget",
            f"{n_req} requests in trace, report says "
            f"{r['budget_used']['requests']}, limit {r['limits']['requests']}")
    return out


def check_js1(report_path, raw_path, previous_count):
    """For a JS1 watch report (one board)."""
    r = json.loads(pathlib.Path(report_path).read_text())
    n = recount(read_raw(raw_path))
    out = []
    claimed_new = len(r["new"])
    out.append(("PASS" if n == r["run"]["posting_count"] else "FAIL",
                "recount", f"report {r['run']['posting_count']}, raw {n}"))
    quiet_claim = (not r["run"]["baseline"]) and claimed_new == 0
    out.append(("FAIL" if (n == 0 and quiet_claim) else "PASS",
                "empty board reported as 'no new jobs'",
                f"raw has {n} jobs; report claims {claimed_new} new (a quiet "
                f"day); the previous run saw {previous_count}"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--js1", action="store_true")
    ap.add_argument("--raw")
    ap.add_argument("--previous-count", type=int)
    a = ap.parse_args(argv)
    findings = (check_js1(a.report, a.raw, a.previous_count) if a.js1
                else check_js2(a.report))
    for status, name, detail in findings:
        print(f"{status}  {name}: {detail}")
    failed = sum(1 for f in findings if f[0] == "FAIL")
    print(f"\n{len(findings) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
