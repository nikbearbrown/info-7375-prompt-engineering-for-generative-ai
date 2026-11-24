"""FILTER.md §7 A1: what the denylist was predicted to move, and what it moved.

A1 predicted, before the code changed, that the 24 postings carrying a body
which died at the inherited F3 would move from `gated` to being scored, and
that nothing would move the other way.

The prediction was right about those 24 and **incomplete**: two more postings
left `gated` that it did not mention. Both are Greenhouse postings whose
`job_family` is null. A1's own text says an absent family passes F3 because
absence is not denial (E3) — the rule was written, and the prediction's
arithmetic missed it. That miss is pinned here rather than quietly absorbed,
and FRICTIONAL.md records it.
"""

from __future__ import annotations

from inherited import rule as inherited_rule

from jobfilter import pipeline


def _was_gated_under_inherited_f3(posting, persona) -> str | None:
    v = inherited_rule.judge(posting.for_rule(), persona)
    return None if v["verdict"] == "relevant" else v["gate_failed"]


def test_exactly_26_postings_left_the_gated_bucket(decisions, persona):
    moved = [
        d for d in decisions
        if _was_gated_under_inherited_f3(d.posting, persona) and d.bucket != pipeline.GATED
    ]
    assert len(moved) == 26, [d.posting.identity for d in moved]


def test_24_of_them_reached_the_scorer_and_2_could_not_be_scored(decisions, persona):
    moved = [
        d for d in decisions
        if _was_gated_under_inherited_f3(d.posting, persona) and d.bucket != pipeline.GATED
    ]
    scored = [d for d in moved if d.score is not None]
    unscorable = [d for d in moved if d.score is None]
    assert len(scored) == 24
    assert len(unscorable) == 2


def test_the_two_unpredicted_movers_are_null_family_greenhouse_postings(
    decisions, persona
):
    """The part A1 got wrong, named so it cannot be forgotten."""
    moved = [
        d for d in decisions
        if _was_gated_under_inherited_f3(d.posting, persona) and d.bucket != pipeline.GATED
    ]
    unscorable = [d for d in moved if d.score is None]
    for d in unscorable:
        assert d.posting.board == "greenhouse:reddit"
        assert d.posting.job_family is None
        assert d.bucket == pipeline.CANNOT_SCORE
        assert _was_gated_under_inherited_f3(d.posting, persona) == "G3_job_family"


def test_nothing_moved_the_other_way(decisions, persona):
    """A denylist sharing no vocabulary with the allowlist can only admit more."""
    backwards = [
        d for d in decisions
        if _was_gated_under_inherited_f3(d.posting, persona) is None
        and d.bucket == pipeline.GATED
    ]
    assert backwards == []


def test_f1_f2_and_f4_still_do_the_rejecting(decisions):
    breakdown = pipeline.summary(decisions)["gate_breakdown"]
    assert breakdown["G1_title_block"] == 302
    assert breakdown["G2_discipline"] == 113
    assert breakdown["G4_location"] == 2
