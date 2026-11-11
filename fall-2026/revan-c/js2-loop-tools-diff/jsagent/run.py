"""One run of the watch: fetch or load, diff against seen ids, judge new postings."""
import json
import pathlib
from datetime import datetime, timezone

from .authorization import E_VERIFY_UNKNOWN, authorization_flag
from .fetch import board_url, fetch_board
from .resume import load_resume
from .rule import judge_postings
from .state import load_seen, save_seen

JUDGMENT_LABEL = "JUDGMENT — model output, not a fact"


class RunError(Exception):
    """The run stopped; state was not advanced."""


def parse_board(raw):
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RunError(f"board response is not JSON: {exc}") from None
    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, list):
        raise RunError("board response has no 'jobs' array")
    seen = set()
    for i, job in enumerate(jobs):
        location = job.get("location") if isinstance(job, dict) else None
        if not (
            isinstance(job, dict)
            and isinstance(job.get("id"), int)
            and isinstance(job.get("title"), str)
            and isinstance(location, dict)
            and isinstance(location.get("name"), str)
            and isinstance(job.get("content"), str)
        ):
            raise RunError(f"jobs[{i}] is missing id, title, location.name, or content")
        if job["id"] in seen:
            raise RunError(f"duplicate posting id {job['id']} in one response")
        seen.add(job["id"])
    return jobs


def _unique_path(directory, stem):
    path = directory / f"{stem}.json"
    n = 1
    while path.exists():
        path = directory / f"{stem}-{n}.json"
        n += 1
    return path


def _claude_part(claude_judge, resume, posting):
    if claude_judge is None:
        result = {"claude_verdict": "unavailable", "claude_justification": [],
                  "claude_reason": "Claude judge disabled for this run (--no-claude)"}
    else:
        result = claude_judge(resume, posting)
    # Only claude_* keys are taken, so the model can never write into a rule field.
    part = {k: v for k, v in result.items() if k.startswith("claude_")}
    part["claude_label"] = JUDGMENT_LABEL
    return part


def run_once(board, resume_path, *, state_path, runs_dir, evidence_dir,
             seeded_response=None, claude_judge=None, fetcher=fetch_board, now=None):
    url = board_url(board)
    resume = load_resume(resume_path)
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    runs_dir, evidence_dir = pathlib.Path(runs_dir), pathlib.Path(evidence_dir)

    if seeded_response is not None:
        mode, source = "seeded", str(seeded_response)
        raw = pathlib.Path(seeded_response).read_bytes()
    else:
        mode = "live"
        raw = fetcher(url)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        evidence = _unique_path(evidence_dir, f"{board}_{stamp}")
        evidence.write_bytes(raw)  # saved before parsing, exactly as received
        source = str(evidence)

    postings = parse_board(raw)
    seen = load_seen(state_path)
    baseline = seen is None
    new = [] if baseline else [p for p in postings if p["id"] not in seen]
    rule_results = judge_postings(resume, new)

    records = []
    for posting in new:
        rule = rule_results[posting["id"]]
        records.append({
            "posting_id": posting["id"],
            "title": posting["title"],
            "location": posting["location"]["name"],
            "absolute_url": posting.get("absolute_url"),
            "rule_verdict": rule["rule_verdict"],
            "rule_justification": rule["rule_justification"],
            "authorization_flag": authorization_flag(resume),
            "e_verify": E_VERIFY_UNKNOWN,
            **_claude_part(claude_judge, resume, posting),
        })

    run_record = {
        "run_at": now.isoformat(timespec="seconds"),
        "mode": mode,
        "source": source,
        "board": board,
        "endpoint": url,
        "resume": str(resume_path),
        "baseline": baseline,
        "postings_in_response": len(postings),
        "new_count": len(records),
        "new_postings": records,
    }
    try:
        runs_dir.mkdir(parents=True, exist_ok=True)
        run_file = _unique_path(runs_dir, f"{stamp}_{mode}")
        run_file.write_text(json.dumps(run_record, indent=2, ensure_ascii=False) + "\n")
    except OSError as exc:
        raise RunError(f"could not write run output: {exc}") from None

    # State advances last: any failure above leaves the previous state untouched.
    try:
        save_seen(state_path, (seen or set()) | {p["id"] for p in postings},
                  run_record["run_at"], source)
    except OSError as exc:
        raise RunError(f"could not write state (run file {run_file} was written): {exc}") from None
    run_record["run_file"] = str(run_file)
    return run_record
