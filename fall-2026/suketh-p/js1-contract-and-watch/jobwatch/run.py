"""One run of the watch (CONTRACT.md 'The watch').

Order: validate the résumé, load the state, fetch, save the raw response, validate it,
find the new ids, judge each new posting twice, save complete results, and only then
replace the state file. Any error before that last step leaves the state as it was."""

import hashlib
import json
from pathlib import Path

from jobwatch import board, judge, report, rule, state
from jobwatch.errors import AgentError
from jobwatch.resume import validate_resume

MODES = ("live", "seeded")


def assess_one(posting, resume, send):
    record = rule.rule_verdict(resume, posting)
    model = judge.judge_posting(resume, judge.posting_input(posting), send)
    return {
        "board": state.BOARD,
        "posting_id": posting.id,
        "title": posting.title,
        "location": posting.location_name,
        "rule_verdict": record,
        "claude_verdict": model,
        "verdicts_agree": record["verdict"] == model["verdict"],
    }


def assess_new(postings, resume, send):
    return [assess_one(posting, resume, send) for posting in postings]


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _new_run_dir(out_dir, retrieved_at, mode):
    stamp = retrieved_at.replace("-", "").replace(":", "")
    run_dir, n = out_dir / f"{stamp}-{mode}", 1
    while run_dir.exists():
        n += 1
        run_dir = out_dir / f"{stamp}-{mode}-{n}"
    run_dir.mkdir(parents=True)
    return run_dir


def _save_raw(run_dir, fetched, mode, source):
    (run_dir / "raw_response.json").write_bytes(fetched.body)
    _write_json(run_dir / "retrieval.json", {
        "mode": mode,
        "source": source,
        "method": "GET",
        "url": fetched.url,
        "status": fetched.status,
        "content_type": fetched.content_type,
        "retrieved_at": fetched.retrieved_at,
        "bytes": len(fetched.body),
        "sha256": hashlib.sha256(fetched.body).hexdigest(),
        "note": "raw_response.json is the response body exactly as received, saved before parsing.",
    })


def run_once(*, fetch, resume, state_path, out_dir, send, mode, source):
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    validate_resume(resume)
    previous = state.load_state(state_path)
    fetched = fetch()
    run_dir = _new_run_dir(Path(out_dir), fetched.retrieved_at, mode)
    _save_raw(run_dir, fetched, mode, source)
    try:
        postings = board.parse_board(fetched.body)
        current_ids = [p.id for p in postings]
        baseline = previous is None
        seen = set() if baseline else set(previous["seen_ids"])
        new = [] if baseline else state.new_ids(current_ids, seen)
        new_postings = sorted((p for p in postings if p.id in set(new)), key=lambda p: p.id)
        assessments = assess_new(new_postings, resume, send)
        for assessment in assessments:
            reply_file = f"claude/{assessment['posting_id']}.txt"
            (run_dir / "claude").mkdir(exist_ok=True)
            (run_dir / reply_file).write_text(assessment["claude_verdict"].pop("raw_reply"), encoding="utf-8")
            assessment["claude_verdict"]["reply_file"] = reply_file
        results = {
            "run_id": run_dir.name,
            "board": state.BOARD,
            "endpoint": fetched.url,
            "mode": mode,
            "source": source,
            "retrieved_at": fetched.retrieved_at,
            "raw_sha256": hashlib.sha256(fetched.body).hexdigest(),
            "baseline": baseline,
            "posting_count": len(postings),
            "previously_seen_count": len(seen),
            "new_ids": new,
            "postings": assessments,
        }
        _write_json(run_dir / "results.json", results)
        (run_dir / "results.md").write_text(report.render(results), encoding="utf-8")
        history = (previous["runs"] if previous else []) + [{
            "run_id": run_dir.name, "mode": mode, "retrieved_at": fetched.retrieved_at,
            "posting_count": len(postings), "new_ids": new, "raw_sha256": results["raw_sha256"],
        }]
        next_state = state.new_state(seen | set(current_ids), history)
        state.save_state(state_path, next_state)
        _write_json(run_dir / "state_after.json", next_state)
    except AgentError as error:
        _write_json(run_dir / "error.json", {
            "error_type": type(error).__name__,
            "error": str(error),
            "reply": getattr(error, "reply", None),
            "state_changed": False,
        })
        raise
    return {"run_id": run_dir.name, "run_dir": str(run_dir), "baseline": baseline, "mode": mode,
            "posting_count": len(postings), "new_ids": new, "assessments": assessments}
