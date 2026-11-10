"""Deliberately WRONG versions of the rule, from CONTRACT.md.

These exist only so tests can prove check_verdicts() catches them. Never
import them from agent/.
"""

from agent import rule


def misaligned_labels(postings, resume, target):
    """WRONG 1: verdicts computed in reverse order, zipped against postings.

    Each verdict is relabeled with the posting_id it is zipped against, so the
    id looks right; only the cited evidence gives the bug away.
    """
    verdicts = [rule.evaluate(p, resume, target) for p in reversed(postings)]
    return [dict(v, posting_id=p["id"]) for p, v in zip(postings, verdicts)]


def empty_justification(postings, resume, target):
    """WRONG 2: correct verdict label, but a justification citing nothing."""
    out = []
    for posting in postings:
        real = rule.evaluate(posting, resume, target)
        out.append({
            "posting_id": posting["id"],
            "verdict": real["verdict"],
            "failed_condition": real["failed_condition"],
            "citations": [],
            "justification": ["Strong ML fit."],
        })
    return out
