"""Review-packet regression test, written before the Lever remote-location patch.

The postings below are constructed fixtures, not live board results. The live
Patch My PC response that motivated the test is recorded in REVIEW_PACKET.md.
"""
import pytest

from jsagent.resume import load_resume
from jsagent.rule import judge_posting
from jsloop.providers import parse_lever
from js2_support import RESUME, lever_body, lever_posting


@pytest.mark.parametrize(
    ("workplace_type", "expected_verdict", "location_passes"),
    [
        ("remote", "relevant", True),
        ("onsite", "not_relevant", False),
    ],
)
def test_lever_workplace_type_controls_remote_location(
    workplace_type, expected_verdict, location_passes
):
    item = lever_posting(
        "constructed-backend-role",
        text="Software Engineer, Backend",
        location="United States",
        description="<p>Python and PostgreSQL services.</p>",
    )
    item["workplaceType"] = workplace_type
    posting = parse_lever(lever_body(item))[0]
    result = judge_posting(load_resume(RESUME), posting)
    location = next(
        evidence for evidence in result["rule_justification"]
        if evidence["condition"] == "location"
    )

    assert location["passed"] is location_passes
    assert result["rule_verdict"] == expected_verdict
