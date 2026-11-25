"""FILTER.md Wrong version W2 — cutting a posting because a field is missing.

"Only keep what we're sure of" sounds safe, but it cuts postings for what the board left out:
2 of the 5 relevant Stripe postings on 2026-10-29 had location `na` (CONTRACT Examples). FILTER.md
§2 (D3) also says missing information is a pass plus an *insufficient* claim, never a cut. These
tests pin that every rule that reads an optional field passes and says it skipped.
"""

import pytest

from job_agent.common.posting import Posting
from job_agent.judges import rule

# Names a résumé skill (rule 3 needs one) and nothing else: no years, no visa line, no salary.
JD = "<p>You will build backend services in Java.</p>"


def _judge(criteria, location):
    return rule.judge(Posting(1, "Backend Engineer", location, JD), criteria)


@pytest.mark.parametrize("location", ["", "N/A", "na", "Remote"])
def test_missing_location_is_not_a_cut(criteria, location):
    r = _judge(criteria, location)
    assert r.verdict["verdict"] == "relevant"
    assert r.verdict["justification"][2]["result"] == "skipped: no location in posting"


def test_missing_years_visa_salary_are_not_cuts(criteria):
    lines = _judge(criteria, "US").verdict["justification"]
    assert lines[4]["result"] == "skipped: no years in posting"
    assert lines[5]["result"] == "no phrase found"
    assert lines[6]["result"] == "skipped: no salary in posting"


def test_a_written_location_outside_the_us_is_still_cut(criteria):
    # The leniency is only for missing fields; a field that says no still cuts.
    r = _judge(criteria, "London, United Kingdom")
    assert (r.verdict["verdict"], r.failed_check) == ("not_relevant", "2")
