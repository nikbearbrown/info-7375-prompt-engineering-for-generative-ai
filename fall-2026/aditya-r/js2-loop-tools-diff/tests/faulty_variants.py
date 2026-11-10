"""DELIBERATELY WRONG implementations from CONTRACT.md §5. Used only by tests to show the checks catch them."""
import json

from agent.validate import TOP_KEYS


def join_by_position(postings, response_texts, resume):
    """Wrong version 1: pairs responses with postings by list position."""
    rows = []
    for p, text in zip(postings, response_texts):
        j = json.loads(text)
        rows.append({"posting_id": p["id"], "JUDGMENT": {"evidence": dict(j, posting_id=p["id"]),
                                                         "verdict": j["verdict"]}})
    return rows


def shallow_validate(text, posting, resume):
    """Wrong version 2: accepts any JSON object with the required keys."""
    try:
        d = json.loads(text)
    except ValueError as e:
        return False, [str(e)], None
    ok = isinstance(d, dict) and set(d) == TOP_KEYS and d.get("verdict") in ("relevant", "not_relevant")
    return ok, [] if ok else ["keys"], d
