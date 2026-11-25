"""DELIBERATELY WRONG - FILTER.md wrong version 2. Not used by the agent.

Returns a well-formed labeled-claim list, but the label step is hard-coded:
every claim is "supported" and no claim is ever checked against the
posting's text. The output has the right shape, so a shortlist built on it
would look grounded while citing nothing.

Exists only so tests/test_wrong_versions.py can be shown to catch it.
"""


def label_claims(posting, claims):
    return [{"claim": c["claim"], "quote": c.get("quote"), "label": "supported",  # WRONG: never checked
             "field": "content"} for c in claims]
