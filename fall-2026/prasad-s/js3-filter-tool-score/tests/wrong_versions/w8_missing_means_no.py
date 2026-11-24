"""DELIBERATELY WRONG — FILTER.md §4 W8 (missing means no). NEVER USED BY THE AGENT.

Treats a missing field as a failed condition, CONTRACT §4's old rule, so a
posting with no location fails C2 outright and there is never a cannot_tell.
It breaks F7. Everything else is agent.filter's own code.

Interface: judge(posting, persona) -> record, as agent.filter.judge.
"""

from agent import filter as correct


def judge(posting, persona):
    record = correct.judge(posting, persona)
    statuses = {condition: correct.FAIL if record[condition] == correct.MISSING else record[condition]
                for condition in correct.CONDITIONS}  # WRONG: missing counts as a fail
    record.update(statuses)
    record["missing"] = []
    record["verdict"] = correct.verdict_of(statuses)
    record["closest_call"] = correct.is_closest_call(statuses, record["score"] if record["score"] is not None else 0)
    return record
