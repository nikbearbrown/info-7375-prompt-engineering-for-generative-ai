"""DELIBERATELY WRONG - a no-op rule 4. Not used by the agent.

Has the right interface but never fires and never flags, so adding it to
the filter would change nothing. Exists only so tests/test_rule4.py can be
shown failing before js3/rule4.py exists.
"""


def check(posting):
    return {"fires": False, "reasons": [], "year_minimums": [], "seniority_title_word": None,
            "management_phrase": None, "eligibility_flags": []}
