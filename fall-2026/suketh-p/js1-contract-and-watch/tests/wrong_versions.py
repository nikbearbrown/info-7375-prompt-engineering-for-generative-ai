"""The two plausible-but-wrong implementations named in CONTRACT.md, written out as code
so the test suite can prove it catches them (see test_wrong_versions_caught.py).

These live under tests/ only. The agent never imports them.
"""

import json

from jobwatch import judge, run
from jobwatch.errors import JudgeError

_real_judge_posting = judge.judge_posting


def assess_new_misattached(postings, resume, send):
    """W1: classifies postings in title order, then attaches the results to ids in
    arrival order. Every individual verdict is computed correctly."""
    assessed = [run.assess_one(p, resume, send) for p in sorted(postings, key=lambda p: p.title)]
    for posting, assessment in zip(postings, assessed):
        assessment.update(posting_id=posting.id, title=posting.title, location=posting.location_name)
    return assessed


def validate_response_lenient(text, resume, posting):
    """W2a: checks the five keys and the verdict, but never checks the citations,
    the quotes, or the posting id."""
    data = json.loads(text)
    keys = {"posting_id", "verdict", "justification", "resume_evidence", "posting_evidence"}
    if not isinstance(data, dict) or set(data) != keys or data["verdict"] not in ("relevant", "not_relevant"):
        raise JudgeError("format")
    return data


def judge_posting_fail_open(resume, posting, send):
    """W2b: validates correctly, but turns a rejected reply into a not_relevant verdict
    instead of an error."""
    try:
        return _real_judge_posting(resume, posting, send)
    except JudgeError as error:
        return {
            "kind": "model_judgment",
            "verdict": "not_relevant",
            "justification": f"Reply rejected: {error}",
            "resume_evidence": [],
            "posting_evidence": [],
            "raw_reply": "",
        }
