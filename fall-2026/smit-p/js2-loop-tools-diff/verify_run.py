"""Independent check of one run. Imports nothing from agent/.

    python3 verify_run.py <run-id>

It trusts only the saved raw responses. For the run being checked it recounts every board
from its raw file with its own minimal parsing, then compares the agent's summary with that
recount and with the same board's raw file from the most recent earlier run. It never reads
the agent's state files, because those are the agent's own claims.

Exit code 0 when every check passes, 1 when any fails.
"""

import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(BASE, "jobs", "runs")
HOSTS = {"boards-api.greenhouse.io", "api.lever.co", "api.ashbyhq.com"}  # own copy, on purpose


def recount(ats, raw_bytes):
    """Count distinct listed posting ids, or raise ValueError if the body has no postings list."""
    body = json.loads(raw_bytes)
    if ats == "lever":
        jobs = body
    else:
        jobs = body["jobs"]
    if not isinstance(jobs, list):
        raise ValueError("no postings list")
    if ats == "ashby":
        jobs = [j for j in jobs if j.get("isListed") is not False]
    return len({str(j["id"]) for j in jobs})


def last_raw(run_dir, board):
    raw_dir = os.path.join(run_dir, "raw")
    if not os.path.isdir(raw_dir):
        return None
    attempts = sorted((f for f in os.listdir(raw_dir) if f.rsplit("-", 1)[0] == board),
                      key=lambda f: int(f.rsplit("-", 1)[1].split(".")[0]))
    return os.path.join(raw_dir, attempts[-1]) if attempts else None


def earlier_count(run_id, board, ats):
    """Recount of this board from the newest earlier run that has a valid raw file for it."""
    others = sorted(r for r in os.listdir(RUNS) if r < run_id and _same_kind(r, run_id))
    for r in reversed(others):
        path = last_raw(os.path.join(RUNS, r), board)
        if path:
            try:
                return r, recount(ats, open(path, "rb").read())
            except (ValueError, KeyError, TypeError):
                continue
    return None, None


def _same_kind(a, b):
    """Seeded runs compare with seeded runs of the same scenario family, live with live."""
    if b.startswith("seeded-"):
        return a.startswith(b.rsplit("-", 1)[0] + "-")
    return not a.startswith("seeded-")


def verify(run_id):
    run_dir = os.path.join(RUNS, run_id)
    summary = json.load(open(os.path.join(run_dir, "summary.json")))
    trace = [json.loads(l) for l in open(os.path.join(run_dir, "trace.jsonl"))]
    checks = []

    def check(name, ok, detail):
        checks.append((name, ok, detail))

    requests = [t for t in trace if t["event"] == "request"]
    bad_hosts = [t["url"] for t in requests if t["url"].split("/")[2].lower() not in HOSTS]
    check("hosts", not bad_hosts, f"{len(requests)} requests, off-list: {bad_hosts or 'none'}")
    check("request count", len(requests) == summary["requests"],
          f"trace has {len(requests)}, summary says {summary['requests']}")

    responses = [t for t in trace if t["event"] == "response"]
    if any(t.get("seeded") for t in responses):
        check("seeded label", summary["seeded"] is True, "replayed responses must be labeled")

    problems_found = False
    for b in summary["boards"]:
        name, ats = b["name"], b["ats"]
        if b["status"] != "ok":
            check(f"{name}: failure has no invented value", b["count"] is None,
                  f"status {b['status']}, count {b['count']}")
            problems_found = True
            continue
        raw = last_raw(run_dir, name)
        try:
            n = recount(ats, open(raw, "rb").read())
        except (ValueError, KeyError, TypeError, OSError) as e:
            check(f"{name}: recount from raw", False, f"cannot recount {raw}: {e}")
            problems_found = True
            continue
        check(f"{name}: recount from raw", n == b["count"], f"agent {b['count']}, recount {n}")
        if ats == "greenhouse":
            meta = json.load(open(raw, "rb")).get("meta", {}).get("total")
            check(f"{name}: greenhouse meta.total", meta == n, f"meta.total {meta}, jobs {n}")
        prev_run, prev = earlier_count(run_id, name, ats)
        if prev is None:
            check(f"{name}: compared with earlier raw", True, "no earlier raw; first observation")
        elif n == 0 and prev > 0:
            check(f"{name}: empty after non-empty", False,
                  f"{prev} postings in {prev_run}, 0 now, yet reported as status ok")
            problems_found = True
        else:
            check(f"{name}: compared with earlier raw", True, f"{prev} in {prev_run}, {n} now")

    if summary["exit"] == "finished":
        check("exit status earned", not problems_found,
              "finished requires every board ok and nothing suspicious"
              if problems_found else "every board ok, nothing suspicious")

    width = max(len(c[0]) for c in checks)
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
    failed = [c for c in checks if not c[1]]
    print(f"verify {run_id}: agent said '{summary['exit']}'; independent check "
          f"{'FAILED (' + str(len(failed)) + ')' if failed else 'passed'}")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(verify(sys.argv[1]))
