"""An independent check of one finished run folder. It does not trust the loop's report.

    python3 independent_check.py runs/<run-id>

It imports nothing from jobloop. It reads the saved raw responses, recounts postings with its
own minimal counting, re-hashes every raw file, replays the trace, and compares all of that
with what report.json claims. Exit 0: no violations. Exit 1: violations found. Exit 2: the
folder could not be read.

What it can catch: a run that says FINISHED or "0 new" about a board whose saved evidence is
empty, missing, non-200 or a different size; attempts missing from the budget; a retry that
was not after a transient failure; a state write after an unfinished run; a seeded run
labeled LIVE. What it cannot catch: a wrong rule verdict, or a raw file that is itself wrong
(for example a server that really returned a stale board).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXIT = {"finished": 0, "incomplete": 1, "budget-exhausted": 2, "error": 3}
RETRYABLE_STATUS = {500, 502, 503, 504}
RETRYABLE_NO_RESPONSE = {"timeout", "connection-reset"}


def count_postings(provider: str, body: bytes):
    """Own count, independent of jobloop.providers. None if the body is not a listing."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if provider in ("greenhouse", "ashby"):
        return len(data["jobs"]) if isinstance(data, dict) and isinstance(data.get("jobs"), list) else None
    if provider == "lever":
        return len(data) if isinstance(data, list) else None
    return None


def check(run_dir: Path, project_root: Path) -> list:
    findings = []

    def bad(code: str, board, message: str):
        findings.append({"invariant": code, "board": board, "message": message})

    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    trace = [json.loads(line) for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines() if line]
    run, boards = report["run"], report["boards"]
    start = next(e for e in trace if e["event"] == "start")

    # C1: every configured board appears in the report, once.
    cfg_path = project_root / start["config"]
    if cfg_path.exists():
        configured = [f"{b['provider']}/{b['board']}" for b in json.loads(cfg_path.read_text())["boards"]]
        reported = [f"{b['provider']}/{b['board']}" for b in boards]
        if sorted(configured) != sorted(reported) and run["status"] != "error":
            bad("C1", None, f"configured boards {configured} but the report lists {reported}")

    # C7: the budget counts every attempt in the trace.
    attempt_events = [e for e in trace if e["event"] == "attempt"]
    if run["attempts_used"] != len(attempt_events):
        bad("C7", None, f"report says {run['attempts_used']} attempts used; the trace shows {len(attempt_events)}")
    if len(attempt_events) > run["budget"]["max_attempts"]:
        bad("C7", None, f"{len(attempt_events)} attempts exceed the budget of {run['budget']['max_attempts']}")

    # C8: exit code matches status.
    if EXIT.get(run["status"]) != run["exit_code"]:
        bad("C8", None, f"status {run['status']!r} with exit code {run['exit_code']}")

    # C9: state written only after a finished run.
    if run["state_update"] == "updated" and run["status"] != "finished":
        bad("C9", None, f"state was updated although the run was {run['status']}")

    # C10: a replay must be labeled as one.
    seeded = run.get("replay_source") or any(
        str(a.get("source_note", "")).startswith("SEEDED") for b in boards for a in b["attempts"])
    md = (run_dir / "report.md").read_text(encoding="utf-8")
    if seeded and (run["mode"] != "SEEDED REPLAY" or "SEEDED REPLAY" not in md):
        bad("C10", None, f"responses were replayed from saved files but the run is labeled {run['mode']!r}")

    all_observed_with_evidence = True
    for b in boards:
        name = f"{b['provider']}/{b['board']}"
        attempts = b["attempts"]
        traced = [e for e in attempt_events if e["board"] == name]
        if len(traced) != len(attempts):
            bad("C2", name, f"report lists {len(attempts)} attempts; the trace shows {len(traced)}")
        if len(attempts) > 1 + run["budget"]["max_retries_per_board"]:
            bad("C7", name, f"{len(attempts)} attempts on one board exceed one retry")
        for prev in attempts[:-1]:
            if not (prev.get("status") in RETRYABLE_STATUS or prev.get("failure") in RETRYABLE_NO_RESPONSE):
                bad("C7", name, f"retried after attempt {prev['attempt']} (HTTP {prev.get('status')}), "
                                "which is not a transient failure")
        count, final_status = None, None
        for a in attempts:
            if a.get("raw_file"):
                raw_path = project_root / a["raw_file"]
                if not raw_path.exists():
                    bad("C3", name, f"raw file {a['raw_file']} is missing")
                    continue
                body = raw_path.read_bytes()
                if hashlib.sha256(body).hexdigest() != a["sha256"]:
                    bad("C3", name, f"raw file {a['raw_file']} does not match its recorded sha256")
                if a is attempts[-1]:
                    count, final_status = count_postings(b["provider"], body), a.get("status")
        evidence_ok = final_status == 200 and isinstance(count, int) and count >= 1
        if b["outcome"] == "observed":
            if not evidence_ok:
                bad("C4", name, f"reported as observed, but the saved evidence is HTTP {final_status} with "
                                f"{count if count is not None else 'no readable'} postings")
            elif b["postings_observed"] != count:
                bad("C4", name, f"report says {b['postings_observed']} postings; the raw file has {count}")
            if b["new"] == [] and not evidence_ok:
                bad("C6", name, "reported as 0 new postings ('no new jobs') without a nonempty raw listing")
        if not (b["outcome"] == "observed" and evidence_ok):
            all_observed_with_evidence = False
        if b["purpose"] == "deliberate-failure" and b["outcome"] == "observed" and evidence_ok:
            bad("C11", name, "the deliberate-failure board returned a nonempty listing; the demonstration was not achieved")

    # C5: FINISHED needs every board observed with nonempty, matching raw evidence.
    if run["status"] == "finished" and not all_observed_with_evidence:
        bad("C5", None, "the run says FINISHED, but at least one board lacks a nonempty HTTP 200 raw listing")
    return findings


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    project_root = Path(__file__).resolve().parent
    run_dir = (project_root / argv[0]).resolve() if not Path(argv[0]).is_absolute() else Path(argv[0])
    try:
        findings = check(run_dir, project_root)
    except (OSError, KeyError, StopIteration, json.JSONDecodeError) as exc:
        print(f"INDEPENDENT CHECK could not read {argv[0]}: {type(exc).__name__}: {exc}")
        return 2
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))["run"]
    print(f"INDEPENDENT CHECK of {argv[0]} (the run reported {report['mode']}, status {report['status']}, "
          f"exit {report['exit_code']})")
    if not findings:
        print("PASS: no invariant violations found. This does not prove the rule verdicts are right.")
        return 0
    print(f"FAIL: {len(findings)} violation(s); the run's own report is not trustworthy:")
    for f in findings:
        print(f"  [{f['invariant']}] {f['board'] or 'run'}: {f['message']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
