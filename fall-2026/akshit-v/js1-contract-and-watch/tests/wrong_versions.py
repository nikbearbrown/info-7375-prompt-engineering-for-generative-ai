"""Deliberately wrong implementations from CONTRACT.md (Wrong versions).

These exist only so the tests can show they catch them. The agent never imports this file.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent import claude_judge, rule


def w1_rule_judge_all(postings, resume):
    """W1: judges postings in title order, then pairs results back by position."""
    ordered = sorted(postings, key=lambda p: p["title"])
    verdicts = [rule.judge(p, resume) for p in ordered]
    # Relabels each result with the posting it was zipped to, so the mismatch is invisible downstream.
    return {p["id"]: {**v, "id": p["id"]} for p, v in zip(postings, verdicts)}


def w1_claude_judge_all(postings, resume, template, caller, workers=4):
    """W1: collects Claude replies in completion order, then zips them with the postings."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(claude_judge.judge, p, resume, template, caller) for p in postings]
        replies = [f.result() for f in as_completed(futures)]
    return {p["id"]: {**r, "asked_id": p["id"]} for p, r in zip(postings, replies)}


def w2_judge(posting, resume):
    """W2: rule.judge with one change: skills are matched as substrings ("sql" in "postgresql")."""
    result = rule.judge(posting, resume)
    if result["branch"] == "disqualified":
        return result
    content = posting["content_text"].lower()
    skills_found = [s for s in resume["skills"] if s.lower() in content]  # the bug
    n = len(skills_found)
    titled = bool(result["title_matches"])
    relevant = (titled and n >= rule.TITLE_MATCH_MIN_SKILLS) or (not titled and n >= rule.STRONG_MIN_SKILLS)
    return {**result, "skills_found": skills_found, "verdict": "relevant" if relevant else "not_relevant"}
