"""FILTER.md §7 A2: the predicted table, pinned.

A2 cut three false friends and predicted the effect in memory before the code
changed (`reports/a2-predicted-effect.txt`). This holds the implementation to
that table, and holds the claim that S5 cannot fire on this corpus.
"""

from __future__ import annotations

import pytest

from jobfilter import pipeline, score as scorer


def test_the_scorer_is_s_v2():
    assert scorer.SCORER_VERSION == "S-v2"


@pytest.mark.parametrize("word,signal", [
    ("infrastructure", "S1_core"),
    ("go", "S2_language"),
    ("0-2 years", "S5_newgrad"),
    ("1-2 years", "S5_newgrad"),
])
def test_the_three_false_friends_are_gone(word, signal):
    assert word not in scorer.SIGNALS[signal][0]


def test_the_predicted_counts_are_what_happened(decisions):
    s = pipeline.summary(decisions)
    assert s["scored"] == 24
    assert s["counts"]["shortlisted"] == 7
    assert s["counts"]["below_threshold"] == 17
    assert s["score_range"] == [-2, 8]


def test_s5_cannot_fire_on_this_corpus(postings):
    """The finding, not a bug.

    None of S5's remaining phrases occurs in any of the 295 postings that carry
    a body: none of these four boards said in words that a posting was open to
    new graduates. If a board ever does, this test fails and A2's reasoning has
    to be revisited -- which is the point of pinning it.
    """
    words, _, _ = scorer.SIGNALS["S5_newgrad"]
    fired = [
        (p.identity, w)
        for p in postings if p.has_body
        for w in words if scorer._pattern(w).search(p.body)
    ]
    assert fired == [], f"S5 fired after all: {fired[:5]}"


def test_infrastructure_would_have_fired_on_every_ramp_posting(postings):
    """The measurement A2 rests on, kept runnable."""
    pattern = scorer._pattern("infrastructure")
    ramp = [p for p in postings if p.board == "ashby:ramp" and p.has_body]
    assert len(ramp) == 177
    assert all(pattern.search(p.body) for p in ramp)
    early = [p for p in ramp if pattern.search(p.body).start() < 300]
    assert len(early) == 177, "it is boilerplate, not a statement about the job"
