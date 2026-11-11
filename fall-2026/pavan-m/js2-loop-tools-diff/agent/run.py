"""One full run: validate résumé, watch the board, judge each new posting by rule and by Claude, write a report."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from agent.judge import PERMITTED_RESUME_FIELDS, judge_claude, make_call_model
from agent.resume import load_resume
from agent.rule import judge_rule
from agent.watch import run_watch

REPORTS_DIR = Path(__file__).parent.parent / "reports"
DEFAULT_MODEL = "claude-sonnet-5-5"


def _write_report(report: dict, stamp: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"run_{stamp}.json"
    suffix = 1
    # Never overwrite a report from an earlier run in the same second.
    while True:
        try:
            with open(path, "x", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                f.write("\n")
            return path
        except FileExistsError:
            path = REPORTS_DIR / f"run_{stamp}_{suffix}.json"
            suffix += 1


def _invalid_judgment(posting_id, error: str) -> dict:
    return {
        "posting_id": posting_id,
        "source": "judgment",
        "verdict": "invalid",
        "justification": None,
        "resume_fields": [],
        "posting_fields": [],
        "attempts": 0,
        "error": error,
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="python -m agent.run")
    parser.add_argument("--resume", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--seeded")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args(argv)

    stamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")

    # Validate the fictional identity before any network request.
    resume = load_resume(args.resume)
    watch = run_watch(args.state, args.evidence, seeded_file=args.seeded)

    jobs = json.loads(Path(watch["evidence_file"]).read_text(encoding="utf-8"))["jobs"]
    by_id = {job["id"]: job for job in jobs if isinstance(job, dict) and "id" in job}
    new_postings = [by_id[i] for i in watch["new_ids"]]

    call_model, setup_error = None, None
    if new_postings:
        try:
            call_model = make_call_model(args.model)
        except Exception as e:  # e.g. no API key: rule verdicts still go in the report
            setup_error = f"judge setup failed: {type(e).__name__}: {e}"

    results = []
    for posting in new_postings:
        record = judge_rule(posting, resume)
        if call_model is None:
            judgment = _invalid_judgment(posting["id"], setup_error)
        else:
            try:
                judgment = judge_claude(posting, resume, call_model)
            except Exception as e:  # a Claude failure must not stop the run
                judgment = _invalid_judgment(posting["id"], f"judge failed: {type(e).__name__}: {e}")
        results.append({
            "posting_id": posting["id"],
            "title": posting.get("title"),
            "record": record,
            "judgment": judgment,
        })

    sent_to_claude = call_model is not None and bool(results)
    report = {
        "run_timestamp": stamp,
        "mode": watch["mode"],
        "watch": watch,
        "data_transfer": {
            "sent_to_anthropic": sent_to_claude,
            "host": "api.anthropic.com" if sent_to_claude else None,
            "model": args.model if sent_to_claude else None,
            "resume_fields_sent": [f for f in PERMITTED_RESUME_FIELDS if f in resume] if sent_to_claude else [],
            "posting_fields_sent": ["id", "title", "location.name", "content (cleaned)"] if sent_to_claude else [],
            "note": (
                "The fictional résumé fields and posting data listed here were sent to api.anthropic.com "
                "for each new posting. name, email and phone were not sent."
                if sent_to_claude
                else "No data was sent to api.anthropic.com in this run."
            ),
        },
        "postings": results,
    }

    path = _write_report(report, stamp)
    print(json.dumps({"report": str(path), "mode": watch["mode"], "new_ids": watch["new_ids"]}, indent=2))


if __name__ == "__main__":
    main()
