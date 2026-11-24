"""DELIBERATELY WRONG — FILTER.md §4 W6 (role words anywhere). NEVER USED BY THE AGENT.

Matches the target_titles anywhere in the posting, title or body text,
instead of in the title alone, so it breaks F3. Everything else is
agent.filter's own code: F1's cleanup, F2's matching, F7's verdict, the score
and the closest-call rule are unchanged.

Interface: judge(posting, persona) -> record, as agent.filter.judge.
"""

from agent import filter as correct
from agent import rule


def judge(posting, persona):
    record = correct.judge(posting, persona)
    text = correct.cleaned_fields(posting)["text"]
    in_text = [term for term in persona["target_titles"] if rule.find_term(term, text) is not None]
    if in_text and record["C1"] != correct.PASS:
        # WRONG: a target title in the body passes C1, whatever the title says.
        record["C1"] = correct.PASS
        record["title_match"] = in_text
        record["missing"] = [name for name in record["missing"] if name != "title"]
        statuses = {condition: record[condition] for condition in correct.CONDITIONS}
        record["verdict"] = correct.verdict_of(statuses)
        record["closest_call"] = correct.is_closest_call(statuses, record["score"])
    return record
