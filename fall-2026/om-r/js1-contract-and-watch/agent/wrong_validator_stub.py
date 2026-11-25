"""DELIBERATELY WRONG judgment validator - kept only as test evidence.

It "guess-fixes" instead of rejecting: strips markdown fences and surrounding
prose, lowercases the verdict, drops extra keys, and never checks that the
justification cites anything. Never import this from the agent.
"""
import json
import re


class JudgmentInvalid(ValueError):
    pass


def validate(raw, posting, resume):
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        raise JudgmentInvalid("no JSON object found")
    obj = json.loads(m.group(0))
    return {"verdict": str(obj.get("verdict", "")).lower(),
            "justification": str(obj.get("justification", ""))}
