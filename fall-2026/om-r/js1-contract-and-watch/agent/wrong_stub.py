"""DELIBERATELY WRONG implementation - kept only as test evidence.

It computes each verdict correctly but commits both of CONTRACT.md's
"wrong versions":
  1. it sorts the verdicts (relevant first) and zips them back against the
     postings in their original order, so labels land on the wrong ids;
  2. its justification is generic prose that cites no resume/posting value.

Never import this from the agent. It exists so the tests can be shown to fail.
"""
import re

_SKILLS = ["Python", "RAG", "LLM", "PyTorch", "LangChain", "vector databases"]


def verdict(posting):
    text = f"{posting.get('title', '')} {posting.get('content', '')}"
    hits = [s for s in _SKILLS if re.search(rf"\b{re.escape(s)}\b", text, re.I)]
    return "relevant" if len(hits) >= 2 else "not relevant"


def evaluate(postings, resume):
    verdicts = sorted((verdict(p) for p in postings), key=lambda v: v != "relevant")
    return [
        {"id": p["id"], "verdict": v, "justification": "Seems like a good fit."}
        for p, v in zip(postings, verdicts)
    ]
