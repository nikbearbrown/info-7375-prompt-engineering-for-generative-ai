"""FILTER.md Wrong version W1 — rule 3 matching résumé words as substrings.

A substring check (`"java" in jd.lower()`) still passes every JD that really asks for Java, so it
looks right; it only shows on a JD where a résumé word hides inside another word. On the saved
2,046 postings that turned 937 rule-3 cuts into passes (reports/filter_v1_measure.py): "AWS" in
"laws", "Rust" in "trusted", "Java" in "JavaScript". These tests pin the word matcher and show the
substring version would have passed each JD.
"""

import pytest

from job_agent.common.posting import Posting
from job_agent.judges import rule
from job_agent.judges.words import strip_html

# Each JD names no résumé skill as a word; each hides one inside another word.
HIDDEN = [
    ("<p>Our front end is built in JavaScript.</p>", "Java"),
    ("<p>We comply with all applicable laws.</p>", "AWS"),
    ("<p>You will be a trusted partner to our users.</p>", "Rust"),
]


def _judge(criteria, content):
    return rule.judge(Posting(1, "Backend Engineer", "US", content), criteria)


@pytest.mark.parametrize("jd, hidden", HIDDEN)
def test_rule_3_finds_no_skill_hidden_inside_a_word(criteria, jd, hidden):
    r = _judge(criteria, jd)
    assert (r.verdict["verdict"], r.failed_check) == ("not_relevant", "3")
    assert r.verdict["justification"][-1]["result"] == "0 found"


@pytest.mark.parametrize("jd, hidden", HIDDEN)
def test_substring_version_would_have_passed(criteria, jd, hidden):
    # Why word matching exists: the wrong version finds the résumé word in every JD above.
    assert hidden in criteria.resume_keywords
    assert hidden.lower() in strip_html(jd).lower()


def test_real_skill_still_passes(criteria):
    # The fix must not lose the JDs that really ask for the skill.
    r = _judge(criteria, "<p>Experience with Java and AWS.</p>")
    assert r.verdict["verdict"] == "relevant"
    assert r.verdict["justification"][3]["result"] == "2 found: Java, AWS"
