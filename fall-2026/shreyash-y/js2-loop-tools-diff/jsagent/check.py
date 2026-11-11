"""The independent check. It reads only the files a run saved (summary, trace, raw responses,
state) and recounts from the raw bytes with its own few lines of parsing. It imports nothing
from the agent, so a bug in the loop or the parsers cannot also hide in the check.

  python3 jsagent/check.py runs/<run_id>      (exit 1 when there are findings)"""
import hashlib
import json
import pathlib
import sys


def count_raw(ats, data):
    if ats == "lever":
        return len(data) if isinstance(data, list) else None
    return len(data["jobs"]) if isinstance(data, dict) and isinstance(data.get("jobs"), list) else None


def raw_ids(ats, data):
    jobs = data if ats == "lever" else (data.get("jobs") if isinstance(data, dict) else None)
    if not isinstance(jobs, list) or not all(isinstance(j, dict) and "id" in j for j in jobs):
        return None
    return {str(j["id"]) for j in jobs}


def check_trace(run_dir, s, project_dir):
    """The trace is appended line by line as the run goes; the summary is written at the end. The
    check compares them, so a summary edited afterwards (or a board left out of it) shows up.
    Added 2026-11-10 after the second regrade found the check trusted the summary."""
    findings = []
    path = run_dir / "trace.jsonl"
    if not path.exists():
        return [f"no trace.jsonl next to the summary"]
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    # Each raw file must still hold the bytes the trace recorded when it was saved (added 2026-11-10
    # after the third regrade: a raw file and summary rewritten together used to pass).
    for e in events:
        if e["event"] == "response" and e.get("raw_file") and e.get("sha256"):
            raw = project_dir / e["raw_file"]
            if not raw.exists():
                findings.append(f"{e.get('board')}: the trace recorded {e['raw_file']} but the file is missing")
            elif hashlib.sha256(raw.read_bytes()).hexdigest() != e["sha256"]:
                findings.append(f"{e.get('board')}: {e['raw_file']} no longer matches the sha256 the trace recorded")
    start = next((e for e in events if e["event"] == "start"), None)
    end = [e for e in events if e["event"] == "exit"]
    in_summary = [b["name"] for b in s["boards"]]
    if start is None:
        findings.append("the trace has no start line")
    elif start.get("boards") != in_summary:
        missing = [n for n in start.get("boards", []) if n not in in_summary]
        findings.append(f"the trace started with boards {start.get('boards')} but the summary lists {in_summary}"
                        + (f" (missing: {', '.join(missing)})" if missing else ""))
    if not end:
        findings.append("the trace has no exit line: the run did not end with one of its exits")
    elif end[-1].get("exit") != s["exit"]:
        findings.append(f"the summary says exit {s['exit']} but the trace says {end[-1].get('exit')}")
    return findings


def check_run(run_dir, project_dir):
    run_dir, project_dir = pathlib.Path(run_dir), pathlib.Path(project_dir)
    s = json.loads((run_dir / "summary.json").read_text())
    findings = check_trace(run_dir, s, project_dir)
    states = {}
    for f in (run_dir.parent / "state").glob("state-*.json"):
        st = json.loads(f.read_text())
        states[st["sequence"]] = st
    previous = states.get(s["state_sequence"] - 1, {}).get("last_counts", {})
    seen_before = states.get(s["state_sequence"] - 1, {}).get("boards", {})
    for b in s["boards"]:
        name = b["name"]
        if b["status"] == "failed" and (b["fetched"] is not None or b["new"] is not None):
            findings.append(f"{name}: a failed board reports counts (fetched={b['fetched']}, new={b['new']})")
        if b["status"] not in ("ok", "empty"):
            continue
        if not b["raw_files"]:
            findings.append(f"{name}: status {b['status']} but no raw response was saved")
            continue
        data = json.loads((project_dir / b["raw_files"][-1]).read_bytes())
        n = count_raw(b["ats"], data)
        if n != b["fetched"]:
            findings.append(f"{name}: summary says fetched {b['fetched']} but the saved response holds {n}")
        if n == 0 and b["status"] != "empty":
            findings.append(f"{name}: the saved response is empty but the board is reported as {b['status']}")
        total = data.get("meta", {}).get("total") if isinstance(data, dict) and isinstance(data.get("meta"), dict) else None
        if total is not None and n is not None and total != n:
            findings.append(f"{name}: the response lists {n} jobs but its own meta.total says {total}")
        ids, key = raw_ids(b["ats"], data), f"{b['ats']}:{b['token']}"
        if b["status"] == "ok" and ids is not None:
            # A board first seen in this run is a baseline (0 new); otherwise new = ids not seen before.
            expected = len(ids - set(seen_before[key])) if key in seen_before else 0
            if b["new"] != expected:
                findings.append(f"{name}: summary says new {b['new']} but the raw ids against the previous state give {expected}")
        before = previous.get(key)
        if before and n is not None and n < before / 2:
            findings.append(f"{name}: {before - n} of {before} postings disappeared since the previous run "
                            f"(more than half in one run is not believable without a second look)")
    bad = [b["name"] for b in s["boards"] if b["status"] in ("failed", "empty", "skipped-budget", "not-run")]
    if s["exit"] == "finished" and bad:
        findings.append(f"run says finished but these boards were not fully checked: {', '.join(bad)}")
    if s["exit"] == "finished" and not any(b["status"] == "ok" for b in s["boards"]):
        findings.append("run says finished but no board was checked")  # added 2026-11-10 after the regrade
    return findings


if __name__ == "__main__":
    run_dir = pathlib.Path(sys.argv[1]).resolve()
    # The project folder is the nearest parent holding GATE.md (runs can be nested, e.g.
    # runs/seeded-finished-wrong/<id>). Fixed 2026-11-09: the first version assumed runs/<id>.
    project = next(p for p in run_dir.parents if (p / "GATE.md").exists())
    found = check_run(run_dir, project)
    print("\n".join(found) if found else "no findings")
    sys.exit(1 if found else 0)
