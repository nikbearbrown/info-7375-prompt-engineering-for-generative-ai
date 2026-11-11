"""The independent check. It reads only the files a run saved (summary, trace, raw responses,
state) and recounts from the raw bytes with its own few lines of parsing. It imports nothing
from the agent, so a bug in the loop or the parsers cannot also hide in the check.

  python3 jsagent/check.py runs/<run_id>      (exit 1 when there are findings)"""
import json
import pathlib
import sys


def count_raw(ats, data):
    if ats == "lever":
        return len(data) if isinstance(data, list) else None
    return len(data["jobs"]) if isinstance(data, dict) and isinstance(data.get("jobs"), list) else None


def check_run(run_dir, project_dir):
    run_dir, project_dir = pathlib.Path(run_dir), pathlib.Path(project_dir)
    s = json.loads((run_dir / "summary.json").read_text())
    findings = []
    states = {}
    for f in (run_dir.parent / "state").glob("state-*.json"):
        st = json.loads(f.read_text())
        states[st["sequence"]] = st
    previous = states.get(s["state_sequence"] - 1, {}).get("last_counts", {})
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
        before = previous.get(f"{b['ats']}:{b['token']}")
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
