"""FILTER.md v1: JS2's rule (F1-F6, exactly as agent/rule.py runs it) plus F7 and F8.

Plain functions, no I/O. Nothing in rule.py is copied: C1, C2 and C3 pass or
fail as rule.judge says, with the terms it matched, and F1's cleanup is
rule.posting_field. This module adds only what FILTER.md v1 adds:

- F7, missing fields: a field is missing when it is absent, null (or not
  text: rule.posting_field reads it as None), or empty after F1's cleanup.
  A text that is only whitespace after cleanup is empty (decision
  2026-11-17: rule.py's step 4 leaves one space and does not trim).
- the score (F5) and the verdict under F7;
- closest calls (FILTER.md §1);
- F8, the ranking.

A posting with no missing field gets rule.py's verdict, by construction;
tools/filter_run.py checks that on every posting it judges.
"""

from . import rule

PASS, FAIL, MISSING = "pass", "fail", "missing"
RELEVANT, NOT_RELEVANT, CANNOT_TELL = "relevant", "not_relevant", "cannot_tell"
CONDITIONS = ("C1", "C2", "C3")
# (condition, F7's name for the field, rule.py's name for it)
FIELDS = (("C1", "title", "title"), ("C2", "location", "location.name"), ("C3", "text", "content"))
THRESHOLD = rule.SKILLS_NEEDED  # F6: a score of 2 or more


def cleaned_fields(posting):
    """{"title", "location", "text"}: F1's cleaned value, or None when F7 calls the field missing."""
    fields = {}
    for _, name, rule_name in FIELDS:
        value = rule.posting_field(posting, rule_name)
        fields[name] = value if value is not None and value.strip() else None
    return fields


def verdict_of(statuses):
    """F7: not_relevant if any present condition fails; else cannot_tell if any is missing; else relevant."""
    values = [statuses[condition] for condition in CONDITIONS]
    if FAIL in values:
        return NOT_RELEVANT
    if MISSING in values:
        return CANNOT_TELL
    return RELEVANT


def is_closest_call(statuses, score):
    """FILTER.md §1: one step from flipping. Never when a condition is missing."""
    if MISSING in (statuses[condition] for condition in CONDITIONS):
        return False
    gates = (statuses["C1"], statuses["C2"])
    if gates == (PASS, PASS):
        return score in (1, 2)  # one skill short of the threshold, or exactly on it
    return score >= THRESHOLD and sorted(gates) == [FAIL, PASS]  # exactly one gate fails, the other passes


def judge(posting, persona):
    """One posting under F1-F8. Returns its record (a dict); the caller adds "board_key" before rank().

    The record holds the cleaned title and location but never the text.
    title_match, location_match and skills_found are the résumé terms rule.py
    matched, in persona order; score is None when the text is missing.
    """
    _, justification = rule.judge(posting, persona)
    conditions = justification["conditions"]
    fields = cleaned_fields(posting)
    statuses = {}
    for condition, name, _ in FIELDS:
        if fields[name] is None:
            statuses[condition] = MISSING
        else:
            statuses[condition] = PASS if conditions[condition]["result"] else FAIL
    present = {condition: statuses[condition] != MISSING for condition in CONDITIONS}
    score = conditions["C3"]["distinct_skills_found"] if present["C3"] else None
    return {
        "posting_id": posting.get("posting_id"),
        "title": fields["title"],
        "location": fields["location"],
        "verdict": verdict_of(statuses),
        "C1": statuses["C1"],
        "C2": statuses["C2"],
        "C3": statuses["C3"],
        "score": score,
        "title_match": list(conditions["C1"]["matched_resume_values"]) if present["C1"] else [],
        "location_match": list(conditions["C2"]["matched_resume_values"]) if present["C2"] else [],
        "skills_found": list(conditions["C3"]["matched_resume_values"]) if present["C3"] else [],
        "missing": [name for condition, name, _ in FIELDS if statuses[condition] == MISSING],
        "closest_call": is_closest_call(statuses, score),
    }


def rank(records):
    """F8: the relevant records only, by score high to low, then board key, then posting id.

    Board keys and ids are compared as strings (GATE §3), so "10" comes before
    "9". No date is read: §4's rule never uses posting date (W7).
    """
    relevant = [record for record in records if record["verdict"] == RELEVANT]
    return sorted(relevant, key=lambda r: (-r["score"], str(r["board_key"]), str(r["posting_id"])))
