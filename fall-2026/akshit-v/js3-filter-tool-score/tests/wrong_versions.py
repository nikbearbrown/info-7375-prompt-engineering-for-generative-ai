"""The four plausible-but-wrong versions from FILTER.md section 4. Never used by the agent.

Each one runs and produces well-formed output. The tests in test_wrong_versions.py must
pass on the real code and fail on each of these.
"""
from agent3 import claims, filter as flt

# WV1: the employer's own name counts as Jack's skill (the inherited JS1 behaviour).
WV1_CFG = {**flt.V1_0, "version": "WV1", "skip_employer_skill": False}

# WV4: keep at score > 6 instead of >= 6.
WV4_CFG = {**flt.V1_0, "version": "WV4", "keep_op": ">"}


def wv2_label_claim(claim: dict, posting: dict, meaning_check) -> dict:
    """WV2: a verbatim quote is taken as support; the meaning check is never asked."""
    if claims.quote_in_posting(claim.get("quote", ""), posting):
        return {**claim, "label": "supported", "why": "quote found verbatim"}
    return {**claim, "label": "insufficient", "why": "quote not found verbatim"}


def wv3_answer(posting: dict | None, board_failed: bool = False, cfg=flt.V1_0) -> str:
    """WV3: missing data is reported as a negative answer."""
    if board_failed or posting is None:
        return "not_relevant"
    r = flt.apply(posting, cfg)
    return "not_relevant" if r["verdict"] == "cannot_tell" else ("relevant" if r["verdict"] == "keep" else "not_relevant")
