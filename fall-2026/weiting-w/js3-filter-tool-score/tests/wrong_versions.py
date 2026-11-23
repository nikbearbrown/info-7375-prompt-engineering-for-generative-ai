"""The four wrong versions of FILTER.md §4, as real code.

Each one is a filter or scorer somebody could plausibly write, and each is
wrong in a way that would not announce itself. The contract tests import these
and assert they fail where the real implementation passes; a wrong version that
no test catches is a hole in the tests, not a spare part.
"""

from __future__ import annotations

import json
import re

from jobfilter import pipeline, score as scorer
from jobfilter.corpus import Posting


# --- W1 -----------------------------------------------------------------------

def missing_body_scores_zero(posting: Posting, persona: dict):
    """W1 — a posting with no body is scored 0 and rejected.

    Plausible because `sum([])` is 0 and the arithmetic never complains: a
    posting with nothing in it got nothing, so it falls below the threshold
    like any other weak posting. It puts all 157 Greenhouse postings in the
    reject pile on the strength of a field their board never sends.
    """
    from inherited import rule as inherited_rule

    from jobfilter import gates

    verdict = inherited_rule.judge(posting.for_rule(), persona)
    if verdict["verdict"] != "relevant" and verdict["gate_failed"] != "G3_job_family":
        return pipeline.Decision(
            posting=posting, bucket=pipeline.GATED,
            gate_failed=verdict["gate_failed"], gate_evidence=verdict["justification"],
        )
    if gates.f3_rejects(posting.job_family) is not None:
        return pipeline.Decision(
            posting=posting, bucket=pipeline.GATED, gate_failed="F3_job_family",
        )
    result = scorer.score(posting.body) or scorer.Score(total=0)   # <-- the bug
    return pipeline.Decision(
        posting=posting,
        bucket=pipeline.SHORTLISTED if result.shortlisted else pipeline.BELOW_THRESHOLD,
        score=result,
    )


# --- W2 -----------------------------------------------------------------------

def substring_topic_match(body: str | None, word: str) -> bool:
    """W2 — signal words matched as substrings.

    Plausible because `in` is the obvious operator and reads as *more*
    permissive in a harmless way. It makes `go` fire on "ongoing", "category"
    and "Chicago", and lets `c#` and `c++` match punctuation runs.
    """
    if not body:
        return False
    return word.lower() in body.lower()


# --- W3 -----------------------------------------------------------------------

def score_from_the_whole_record(posting: Posting):
    """W3 — score the JSON record instead of the plain-text body.

    Plausible because `json.dumps(record)` is one line and obviously contains
    everything the posting knows. It also contains markup, `href` targets, the
    apply URL and the board's own field names, so a signal word inside a link
    scores exactly as much as one inside a sentence.
    """
    return scorer.score(json.dumps(posting.raw, ensure_ascii=False))


# --- W4 -----------------------------------------------------------------------

def relevance_implies_support(claim: str, hits: list) -> str:
    """W4 — label a claim `supported` whenever the signal that produced it fired.

    The most tempting of the four, because it makes every shortlist entry look
    well-evidenced and costs nothing to write. It is the relevance-is-not-
    entailment error from FILTER.md §2 E2: a posting containing "python"
    supports "this posting mentions Python" and nothing more.
    """
    return "supported" if hits else "insufficient"


#: Used by the W2 test: words whose only occurrences in the corpus are inside
#: longer words. `go` is the one that matters and the one A2 cut.
SUBSTRING_TRAPS = ("go", "api", "java")

_WORD = re.compile(r"\w")
