"""DELIBERATELY WRONG — CONTRACT.md §5 W2 (justification that cites nothing,
or cites what is not there). NEVER USED BY THE AGENT.

Every function returns the correct verdict from the real agent.rule.judge
and a wrong justification. Interface: same as judge(posting, persona) ->
(rule_verdict, rule_justification).
"""

from agent.rule import judge


def judge_empty_justification(posting, persona):
    """(a) Right label, justification that cites nothing."""
    verdict, _ = judge(posting, persona)
    return verdict, {"resume_fields": [], "posting_fields": [], "conditions": {}}


def judge_cites_skill_not_in_resume(posting, persona):
    """(b) Right label, but resume_fields also cites a skill the résumé does not list."""
    verdict, justification = judge(posting, persona)
    justification["resume_fields"].append({"field": "skills", "value": "Java"})  # WRONG: not a résumé skill
    return verdict, justification


def judge_first_failing_condition_only(posting, persona):
    """(c) Right label, but a not_relevant record cites only its first failing condition."""
    verdict, justification = judge(posting, persona)
    if verdict == "not_relevant":
        first = justification["failing_conditions"][0]
        justification["conditions"] = {first: justification["conditions"][first]}  # WRONG: stops at the first
        justification["failing_conditions"] = [first]
    return verdict, justification


VARIANTS = {
    "W2 (a) empty justification": judge_empty_justification,
    "W2 (b) cites a skill not in the résumé": judge_cites_skill_not_in_resume,
    "W2 (c) not_relevant cites only the first failing condition": judge_first_failing_condition_only,
}
