"""FILTER.md §7 A2: the predicted table, pinned.

A2 cut three false friends and predicted the effect in memory before the code
changed (`reports/a2-predicted-effect.txt`). This holds the implementation to
that table, and holds the claim that S5 cannot fire on this corpus.
"""

from __future__ import annotations

import pytest

from jobfilter import pipeline, score as scorer


def test_what_remains_of_a2_after_a3_a4_and_a5():
    """A2's own prediction (shortlist 14 -> 7, range [-2, 8]) held when it was
    made and is recorded in reports/a2-predicted-effect.txt. Three amendments
    have moved those counts since, so they are not asserted here, and the
    current versions live in tests/test_versions.py.

    One of A2's three cuts was undone: A5 reinstated `infrastructure` once A4
    could tell a company blurb from a job description. What survives of A2 is
    the two cuts that were genuinely bad words, and the finding that S5 cannot
    fire at all -- both tested below.
    """
    assert "infrastructure" in scorer.SIGNALS["S1_core"][0], "reinstated by A5"


@pytest.mark.parametrize("word,signal", [
    ("go", "S2_language"),
    ("0-2 years", "S5_newgrad"),
    ("1-2 years", "S5_newgrad"),
])
def test_the_two_cuts_that_were_genuinely_bad_words_stay_cut(word, signal):
    """`infrastructure` is not here: A5 put it back. See test_amendment_a5."""
    assert word not in scorer.SIGNALS[signal][0]


def test_the_part_of_a2_that_a3_did_not_touch(decisions):
    """A2 moved nothing in or out of the scorer's reach; only scores moved."""
    s = pipeline.summary(decisions)
    assert s["scored"] == 24


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
