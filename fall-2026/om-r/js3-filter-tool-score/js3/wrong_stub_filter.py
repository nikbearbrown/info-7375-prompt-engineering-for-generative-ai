"""DELIBERATELY WRONG - FILTER.md wrong version 1. Not used by the agent.

Plausible-looking filter that applies the skill-word rule to whatever text a
posting has. An empty-content posting simply has no skill words, so it lands
in "rejected" as "not relevant" - the quiet-empty-looks-like-nothing-here
mistake JS2's FINISHED-WRONG-ANSWER.md documented. It also lands in the
reject audit's sampling pool, where nobody could hand-judge it.

Exists only so tests/test_wrong_versions.py can be shown to catch it.
"""
import html
import re

SKILLS = ["Python", "RAG", "LLM", "PyTorch", "LangChain", "vector databases"]


def _text(raw):
    t = html.unescape(raw or "")
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


def classify(posting):
    text = _text(posting.get("title")) + " " + _text(posting.get("content"))
    found = [s for s in SKILLS
             if re.search(r"(?<!\w)" + r"\s+".join(map(re.escape, s.split())) + r"(?!\w)", text, re.I)]
    bucket = "relevant" if len(found) >= 2 else "rejected"   # WRONG: no insufficient_data case
    return {"board": posting.get("board"), "id": posting["id"], "title": posting.get("title"),
            "bucket": bucket, "reasons": [f"{len(found)} of 6 skill words"]}


def run_filter(postings):
    results = [classify(p) for p in postings]
    out = {"results": results, "relevant": [], "rejected": [], "insufficient_data": []}
    for r in results:
        out[r["bucket"]].append(r)
    return out


def reject_sampling_pool(filter_output):
    return list(filter_output["rejected"])
