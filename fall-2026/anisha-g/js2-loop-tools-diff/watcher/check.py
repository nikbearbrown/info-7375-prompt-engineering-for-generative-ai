"""Independent check. It does NOT trust the agent's verdicts.
1. Offline: for every board the agent marked 'ok', it re-reads the saved raw response and recounts the jobs with its own parser.
2. Live (--live): it asks each board again through a SEPARATE code path (curl, not the agent's fetch) and compares the count.
   This is what catches a run whose saved files agree with themselves but are wrong (e.g. an empty answer for a board with jobs).
Usage: python3 watch.py check reports/job-watch/runs/<run-id> [--live]"""
import json, subprocess, sys
from pathlib import Path

def _count(ats, body):
    data = json.loads(body)
    if ats == "greenhouse": return len(data["jobs"])
    if ats == "lever": return len(data)
    raise ValueError(ats)

LIVE_URLS = {"greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
             "lever": "https://api.lever.co/v0/postings/{slug}?mode=json"}

def curl_count(board):
    """A second, independent way to ask the board: curl + this file's own parser. Read-only GET to the same two allowed hosts."""
    ats, slug = board.split(":", 1)
    p = subprocess.run(["curl", "-sS", "-m", "30", "-o", "-", "-w", "\n%{http_code}", LIVE_URLS[ats].format(slug=slug)],
                       capture_output=True, timeout=40)
    body, _, code = p.stdout.rpartition(b"\n")
    status = int(code or 0)
    return status, (_count(ats, body) if status == 200 else None)

def check_run(run_dir, live=None):
    run_dir = Path(run_dir); trace = json.loads((run_dir / "trace.json").read_text()); problems = []
    if not trace.get("boards"):
        return [f"trace says exit={trace.get('exit')} but has no board records: nothing to check it against"]
    for b in trace["boards"]:
        if live and b["status"] in ("ok", "failed") and ":" in b["board"]:
            try:
                status, n = live(b["board"])
            except Exception as e:
                problems.append(f"{b['board']}: live recount could not run ({e})"); status = None
            if status is not None:
                if b["status"] == "ok" and n is not None and n != b["jobs"]:
                    problems.append(f"{b['board']}: reported {b['jobs']} jobs, but a live recount now finds {n} (the board may also have changed since the run)")
                if b["status"] == "ok" and status != 200:
                    problems.append(f"{b['board']}: reported ok, but a live request now gets HTTP {status}")
        if b["status"] != "ok": continue
        k = b["board"]; ats = k.split(":")[0]
        if not b["attempts"] or "raw_file" not in b["attempts"][-1]:
            problems.append(f"{k}: reported ok but no raw evidence saved"); continue
        raw = run_dir / b["attempts"][-1]["raw_file"]; st = raw.with_name(raw.name + ".status")
        if not raw.exists() or not st.exists():
            problems.append(f"{k}: reported ok but raw evidence {raw.name} is missing"); continue
        status, body = int(st.read_text()), raw.read_bytes()
        if status != 200:
            problems.append(f"{k}: reported ok with {b['jobs']} jobs, but the raw response was HTTP {status}"); continue
        if not body.strip():
            problems.append(f"{k}: reported ok with {b['jobs']} jobs, but the raw response body was blank"); continue
        try: n = _count(ats, body)
        except Exception as e:
            problems.append(f"{k}: reported ok, but the raw response is unreadable ({e})"); continue
        if n != b["jobs"]:
            problems.append(f"{k}: reported {b['jobs']} jobs, but the raw response contains {n}")
    return problems

if __name__ == "__main__":
    p = check_run(sys.argv[1], live=curl_count if "--live" in sys.argv else None)
    print("INDEPENDENT CHECK:", "PASS - every 'ok' board matches its raw response" if not p else f"FAIL - {len(p)} problem(s)")
    for x in p: print("  -", x)
    sys.exit(1 if p else 0)
