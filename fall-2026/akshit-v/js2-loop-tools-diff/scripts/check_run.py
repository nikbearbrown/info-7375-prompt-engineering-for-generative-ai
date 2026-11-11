"""Independent check of a finished run. It does not trust the agent's report.

It reads the run record's raw evidence files and its state snapshot from before the run,
recounts jobs with its own minimal JSON reading (it imports nothing from agent2), and fails
if the report disagrees with the evidence.

    python -I scripts/check_run.py out/runs/<run_id>.json
Exit code 0 = PASS, 1 = FAIL.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {"boards-api.greenhouse.io", "api.lever.co", "api.ashbyhq.com"}   # copied from GATE.md §6


def job_ids(ats: str, data):
    """Native ids from a raw response, or None if it is not a job list."""
    jobs = data if ats == "lever" else (data.get("jobs") if isinstance(data, dict) else None)
    if not isinstance(jobs, list):
        return None
    if ats == "ashby":
        jobs = [j for j in jobs if j.get("isListed", True)]
    return [f"{ats}:{{board}}:{j.get('id')}" for j in jobs]


def check(record: dict) -> list[str]:
    problems = []
    requests = [e for e in record["trace"] if e["event"] == "request"]
    before = record["state_before"]["boards"]

    for e in requests:
        host = e["url"].split("/")[2]
        if host not in ALLOWED or not e["url"].startswith("https://"):
            problems.append(f"request to non-allowed URL: {e['url']}")
    if len(requests) > record["budget"]["max_requests"]:
        problems.append(f"{len(requests)} requests exceed the budget of {record['budget']['max_requests']}")

    last_try = {}
    for e in requests:
        last_try[e["board"]] = e
    for key, e in last_try.items():
        ats, board = key.split(":", 1)
        reported = record["boards"].get(key, {}).get("outcome")
        if not e.get("raw"):
            if reported == "ok":
                problems.append(f"{key}: reported ok, but no raw response was saved")
            continue
        try:
            data = json.loads((ROOT / e["raw"]).read_text(encoding="utf-8"))
        except ValueError:
            data = None
        ids = job_ids(ats, data) if data is not None else None
        ids = [i.replace("{board}", board) for i in ids] if ids is not None else None
        prev = before.get(key)
        if reported == "ok":
            if ids is None:
                problems.append(f"{key}: reported ok, but the raw response is not a job list")
            elif not ids and prev and prev.get("last_count"):
                problems.append(f"{key}: reported ok with 0 jobs, but the board had {prev['last_count']} before. "
                                "An empty board is not 'no new jobs'.")
            elif prev is not None:
                expected_new = sorted(set(ids) - set(prev["seen_ids"]))
                got_new = sorted(p["id"] for p in (record["new"].get(key) or []))
                if expected_new != got_new:
                    problems.append(f"{key}: reported {len(got_new)} new, evidence shows {len(expected_new)}")

    outcomes = {k: v["outcome"] for k, v in record["boards"].items() if not k.endswith("#repeat")}
    if record["exit"] == "finished" and (record["not_attempted"] or any(o != "ok" for o in outcomes.values())):
        problems.append("exit 'finished', but not every planned board succeeded")
    if record["exit"] == "finished" and problems:
        problems.append("the run ended cleanly ('finished') and is wrong")
    return problems


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = Path(sys.argv[1])
    record = json.loads(path.read_text(encoding="utf-8"))
    problems = check(record)
    print(f"independent check of {path.as_posix()} (agent said: {record['exit']}):")
    print("  PASS: report agrees with the saved evidence" if not problems else
          "\n".join(f"  FAIL: {p}" for p in problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
