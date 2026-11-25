"""FILTER.md v2 rule 4: experience ceilings (A) and the largest years number, brackets included (B2).

Each case is a real JD sentence from the 2026-11-25 audit (audit/AUDIT.md), where Isaac's hand label
disagreed with v1. v1 kept all of them; these tests pin that v2 cuts them for the right reason and
still keeps a posting within Aarav's reach (2 years + 2 stretch = 4).
"""

import pytest

from job_agent.common.posting import Posting
from job_agent.judges import rule
from job_agent.judges import words

# Names a résumé skill so rule 3 passes and rule 4 is the one that decides.
SKILL = "<p>You will build backend services in Java.</p>"


def _judge(criteria, sentence):
    r = rule.judge(Posting(1, "Software Engineer", "US", SKILL + f"<p>{sentence}</p>"), criteria)
    return r.verdict["verdict"], r.failed_check, r.verdict["justification"][4]["result"]


@pytest.mark.parametrize("sentence, ceiling", [
    ("0-1 years of experience in software engineering or a relevant field", "1"),          # S20
    ("New grad candidates should have no more than 18 months of professional experience", "1.5"),  # S01
])
def test_a_ceiling_below_aarav_cuts(criteria, sentence, ceiling):
    verdict, failed, result = _judge(criteria, sentence)
    assert (verdict, failed) == ("not_relevant", "4")
    assert result == f"ceiling {ceiling} years < 2 (too experienced)"


def test_a_range_reaching_aarav_is_not_a_ceiling_cut(criteria):
    # S30 "2–12+ years": the upper end is above Aarav, so A must not cut it; the requirement is 2.
    assert _judge(criteria, "2–12+ years of professional software development experience")[:2] == ("relevant", None)


def test_b2_reads_a_number_in_brackets():
    # S16: v1 read no years at all here.
    assert words.years_in("plus six (6) years of software development experience") == [6]


@pytest.mark.parametrize("sentence, largest", [
    ("Have 5+ years of experience in engineering, including 3+ years of experience in infrastructure", 5),
    ("plus six (6) years of software development experience. Must also have four (4) years of Java", 6),  # S16
])
def test_b2_the_largest_number_decides(criteria, sentence, largest):
    verdict, failed, result = _judge(criteria, sentence)
    assert (verdict, failed, result) == ("not_relevant", "4", f"max {largest} years > 4")


def test_b2_keeps_a_posting_within_reach(criteria):
    assert _judge(criteria, "3+ years of backend experience, 4 years preferred") == ("relevant", None, "max 4 years ≤ 4")


def test_no_years_still_passes(criteria):
    # FILTER §2 / D3 is unchanged by v2: missing information is a pass.
    assert _judge(criteria, "We value curiosity.")[2] == "skipped: no years in posting"


def test_year_ceilings_reads_months_and_ranges():
    # Looked up at call time so this file still loads against v1 code (for the red run).
    assert words.year_ceilings("no more than 18 months") == [1.5]
    assert words.year_ceilings("0-1 years") == [1.0]


def test_v2_1_export_license_sentence_is_not_a_visa_refusal(criteria):
    # H01 (held-out): Cloudflare's export-control boilerplate cut all 8 of its rule-5 postings under
    # "without sponsorship". It is about an export license, not a work visa.
    sentence = ("Please note that any offer of employment may be conditioned on your authorization to receive "
                "software or technology controlled under these U.S. export laws without sponsorship for an export license.")
    assert _judge(criteria, sentence)[0] == "relevant"


@pytest.mark.parametrize("sentence", ["Candidates must be authorized to work without sponsorship.",
                                      "These positions are filled without visa sponsorship."])
def test_v2_1_real_visa_refusals_still_cut(criteria, sentence):
    assert _judge(criteria, sentence)[:2] == ("not_relevant", "5")
