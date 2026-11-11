"""CONTRACT Wrong version 6 — the visa check using plain word matching.

Plain matching would still fail a JD that really says "no sponsorship", so the bug looks correct;
it only shows on a JD that has both words apart ("No degree required. Visa sponsorship is available.").
These are the contract's postings A and B, plus proof that plain matching *would* have failed A.
"""

import pytest

from job_agent.common.posting import Posting
from job_agent.judges import rule
from job_agent.judges.words import has_all_words, has_phrase, words

A = "<p>Java. No degree required. Visa sponsorship is available.</p>"
B = "<p>Java. Candidates must be authorized to work without sponsorship.</p>"


def _judge(criteria, content):
    return rule.judge(Posting(1, "Backend Engineer", "US", content), criteria)


def test_posting_a_passes_check_5(criteria):
    assert criteria.profile["needs_sponsorship"] is True
    r = _judge(criteria, A)
    assert r.verdict["verdict"] == "relevant"
    assert r.verdict["justification"][5]["result"] == "no phrase found"


def test_posting_b_fails_at_check_5(criteria):
    r = _judge(criteria, B)
    assert (r.verdict["verdict"], r.failed_check) == ("not_relevant", "5")
    assert r.verdict["justification"][-1]["result"] == "found: without sponsorship"


def test_plain_word_matching_would_have_wrongly_failed_a():
    # Why the whole-phrase matcher exists: both words are in A, just not together.
    assert has_all_words("no sponsorship", set(words(A))) is True
    assert has_phrase("no sponsorship", words(A)) is False


@pytest.mark.parametrize("jd", ["No  Sponsorship offered", "no-sponsorship", "NO SPONSORSHIP."])
def test_phrase_survives_case_and_spacing(jd):
    assert has_phrase("no sponsorship", words(jd))


def test_check_5_is_skipped_when_sponsorship_not_needed(criteria):
    no_visa = type(criteria)(criteria.resume_keywords, {**criteria.profile, "needs_sponsorship": False},
                             criteria.aliases, criteria.phrases)
    r = _judge(no_visa, B)
    assert r.verdict["verdict"] == "relevant"
    assert r.verdict["justification"][5]["result"] == "skipped: profile.needs_sponsorship is false"
