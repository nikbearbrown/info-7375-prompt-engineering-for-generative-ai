"""FILTER.md §7 A3: the experience wall as a number, not a spelling."""

from __future__ import annotations

import pytest

from jobfilter import evidence, pipeline, score as scorer


def test_what_a3_established_and_later_amendments_did_not_touch(decisions):
    """Current versions live in tests/test_versions.py."""
    assert pipeline.summary(decisions)["scored"] == 24


@pytest.mark.parametrize("span,years", [
    ("- 5+ years of backend engineering experience", 5),
    ("- 3+ years in a similar role", 3),
    ("- A minimum of 5 years of industry experience", 5),
    ("- Minimum of 3 years building software", 3),
    ("at least 7 years of relevant work", 7),
    ("- 5 years of industry experience required", 5),
])
def test_every_phrasing_a3_named_is_read(span, years):
    hit = scorer._experience_wall(span)
    assert hit is not None, span
    assert hit.points == -6


@pytest.mark.parametrize("span", [
    "- 2+ years of experience",            # below MIN_WALL_YEARS
    "we have been building for 10 years",  # not an experience requirement shape
    "a 5 year plan",
])
def test_things_that_are_not_an_experience_wall(span):
    assert scorer._experience_wall(span) is None


def test_the_numbers_gap_as_well_as_the_phrasing_gap(decisions):
    """3+ years was never in the old literal list. Two postings turned on it."""
    by_word = {}
    for d in decisions:
        if d.score is None:
            continue
        for h in d.score.hits:
            if h.signal == "S6_experience_wall":
                by_word.setdefault(h.word.lower().strip(), []).append(d.posting.title)
    assert any(w.startswith("3+") for w in by_word), by_word.keys()
    assert any("minimum of" in w for w in by_word), by_word.keys()


def test_the_top_entry_of_the_old_shortlist_is_gone(decisions):
    ml = next(d for d in decisions
              if d.posting.title.strip() == "Machine Learning Engineer"
              and d.posting.board == "ashby:ramp")
    assert ml.score.total == 2
    assert ml.bucket == pipeline.BELOW_THRESHOLD
    wall = next(h for h in ml.score.hits if h.signal == "S6_experience_wall")
    assert "minimum of 5 years" in wall.word.lower()


def test_the_evidence_rules_now_contradict_where_they_used_to_abstain(decisions):
    ml = next(d for d in decisions
              if d.posting.title.strip() == "Machine Learning Engineer"
              and d.posting.board == "ashby:ramp")
    claim = next(c for c in evidence.claims_for(ml) if c.kind == "OPEN_TO_NEW_GRADS")
    assert claim.label == evidence.CONTRADICTED
    assert claim.detail["years_in_span"] == 5


def test_contradicted_now_fires_on_ten_of_the_scored_postings(decisions):
    n = sum(
        1 for d in decisions if d.score is not None
        for c in evidence.claims_for(d)
        if c.kind == "OPEN_TO_NEW_GRADS" and c.label == evidence.CONTRADICTED
    )
    assert n == 10


def test_the_scorer_and_the_evidence_rules_agree_about_every_body(postings):
    """One rule, two call sites: they must never disagree about a sentence."""
    for p in postings:
        if not p.has_body:
            continue
        wall = scorer._experience_wall(p.body)
        years = evidence._min_years(p.body)
        if wall is not None:
            assert years is not None and years >= scorer.MIN_WALL_YEARS, p.identity
