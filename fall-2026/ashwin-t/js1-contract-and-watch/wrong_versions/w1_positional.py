"""Wrong version 1 (CONTRACT.md): verdicts attached by list position after a reorder.

Each posting is classified correctly, then the list is sorted by title for display and
the verdicts are zipped back on by position, so a verdict can land on the wrong posting id.
"""
from jobwatch import rule


def classify_all(postings, resume):
    postings = list(postings)
    verdicts = [rule.classify(p, resume) for p in postings]
    shown = sorted(postings, key=lambda p: p["title"])
    return {rule.posting_id(p): v for p, v in zip(shown, verdicts)}
