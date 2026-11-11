"""Independent check. It does NOT trust the agent's verdicts: for every board the agent marked 'ok', it re-reads the saved
raw response and recounts the jobs with its own parser. Usage: python3 -m watcher.check reports/job-watch/runs/<run-id>"""
import json, sys
from pathlib import Path

def _count(ats, body):
    data = json.loads(body)
    if ats == "greenhouse": return len(data["jobs"])
    if ats == "lever": return len(data)
    raise ValueError(ats)

def check_run(run_dir):
    run_dir = Path(run_dir); trace = json.loads((run_dir / "trace.json").read_text()); problems = []
    for b in trace["boards"]:
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
    p = check_run(sys.argv[1])
    print("INDEPENDENT CHECK:", "PASS - every 'ok' board matches its raw response" if not p else f"FAIL - {len(p)} problem(s)")
    for x in p: print("  -", x)
    sys.exit(1 if p else 0)
