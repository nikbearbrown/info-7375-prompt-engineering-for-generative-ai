"""The three plausible-but-wrong versions in FILTER.md section 5, as real code.

The agent never uses them. tests/test_filter_wrong_versions.py runs the same checks on the real code and on each of
these, and must catch all three.
"""
import re

from . import evidence
from . import filter as filt


def substring_words(text, words):
    """Wrong version 1: a word counts if it appears inside another word ("Java" in "JavaScript", "US" in "focus")."""
    return [w for w in words if w.lower() in text.lower()]


def decide_substring(job, board, resume, spec):
    return filt.decide(job, board, resume, spec, words=substring_words)


def rank_by_skill_count(decisions, size=10):
    """Wrong version 2: the shortlist is every posting sorted by how many résumé skills it names, gates ignored."""
    return sorted(decisions, key=lambda d: -len((d.get("parts") or {}).get("S2 skills", {}).get("skills", [])))[:size]


def label_keyword(claim, job, spec, skills):
    """Wrong version 3: a claim is "supported" if any of its longer words appears anywhere in the posting."""
    text = evidence.norm(evidence.posting_text(job))
    words = re.findall(r"[A-Za-z][A-Za-z+#.-]{3,}", claim.get("claim", ""))
    if any(w.lower() in text for w in words):
        return evidence.SUPPORTED, "a word of the claim is in the posting", False
    return evidence.INSUFFICIENT, "no word of the claim is in the posting", False
