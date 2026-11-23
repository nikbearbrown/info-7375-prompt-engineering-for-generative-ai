"""Gates, then score, then three buckets — never two.

FILTER.md §3: a posting whose board sent no description is **not** rejected and
**not** scored zero. It goes to `cannot_score`, which is reported with its own
count wherever a count appears. Collapsing it into `rejected` is wrong version
W1 and is the same failure JS2's wrong-answer report is about: a true-sounding
number produced by treating "I did not look" as "I looked and found nothing".

Order matters and is the inherited one. The gates run first, so a posting that
is not takeable never reaches the scorer — including when it has no body. A
Greenhouse posting for a Director of Sales is `rejected` at F1, not
`cannot_score`: the gates read the title and location, which Greenhouse does
send, and the absence of a *description* has no bearing on whether the title
says "Director".
"""

from __future__ import annotations

from dataclasses import dataclass, field

from inherited import rule as inherited_rule

from . import score as scorer
from .corpus import Posting

FILTER_VERSION = "F-v1"

SHORTLISTED = "shortlisted"
BELOW_THRESHOLD = "below_threshold"
GATED = "gated"
CANNOT_SCORE = "cannot_score"


@dataclass
class Decision:
    posting: Posting
    bucket: str
    gate_failed: str | None = None
    gate_evidence: list[dict] = field(default_factory=list)
    score: scorer.Score | None = None
    note: str = ""

    @property
    def total(self) -> int | None:
        return None if self.score is None else self.score.total

    def as_dict(self) -> dict:
        row = {
            "identity": self.posting.identity,
            "board": self.posting.board,
            "title": self.posting.title,
            "location": self.posting.location,
            "job_family": self.posting.job_family,
            "url": self.posting.url,
            "filter_version": FILTER_VERSION,
            "bucket": self.bucket,
            "gate_failed": self.gate_failed,
            "gate_evidence": self.gate_evidence,
            "has_body": self.posting.has_body,
            "body_fields": list(self.posting.body_fields),
            "score": None if self.score is None else self.score.as_dict(),
        }
        if self.note:
            row["note"] = self.note
        return row


def decide(posting: Posting, persona: dict) -> Decision:
    """One posting through F-v1: four inherited gates, then S-v1."""
    verdict = inherited_rule.judge(posting.for_rule(), persona)
    if verdict["verdict"] != "relevant":
        return Decision(
            posting=posting,
            bucket=GATED,
            gate_failed=verdict["gate_failed"],
            gate_evidence=verdict["justification"],
        )

    if not posting.has_body:
        return Decision(
            posting=posting,
            bucket=CANNOT_SCORE,
            note=(
                f"{posting.board} does not return a description on the endpoint "
                "JS2 called; S1-S7 are undefined for this posting. Not a zero "
                "and not a rejection (FILTER.md section 3)."
            ),
        )

    result = scorer.score(posting.body)
    assert result is not None, "has_body was true but the scorer saw no body"
    return Decision(
        posting=posting,
        bucket=SHORTLISTED if result.shortlisted else BELOW_THRESHOLD,
        score=result,
    )


def run(postings: list[Posting], persona: dict) -> list[Decision]:
    return [decide(p, persona) for p in postings]


def buckets(decisions: list[Decision]) -> dict[str, list[Decision]]:
    out: dict[str, list[Decision]] = {
        SHORTLISTED: [], BELOW_THRESHOLD: [], GATED: [], CANNOT_SCORE: [],
    }
    for d in decisions:
        out[d.bucket].append(d)
    return out


def summary(decisions: list[Decision]) -> dict:
    """Counts that must add up, because a count that does not is a lie."""
    by = buckets(decisions)
    counts = {name: len(rows) for name, rows in by.items()}
    total = sum(counts.values())
    assert total == len(decisions), "buckets lost a posting"

    gate_breakdown: dict[str, int] = {}
    for d in by[GATED]:
        key = d.gate_failed or "unknown"
        gate_breakdown[key] = gate_breakdown.get(key, 0) + 1

    scored = [d for d in decisions if d.score is not None]
    return {
        "filter_version": FILTER_VERSION,
        "scorer_version": scorer.SCORER_VERSION,
        "threshold": scorer.THRESHOLD,
        "total": total,
        "counts": counts,
        "gate_breakdown": gate_breakdown,
        "scored": len(scored),
        "score_range": (
            [min(d.total for d in scored), max(d.total for d in scored)]
            if scored else None
        ),
    }
