"""EXPECTATION WRITTEN BY SHREYASH, CODE BY CLAUDE CODE (2026-11-10).

Shreyash's expectation, word for word:
  Posting: Oscar — Physician Reviewer
  What must happen: Condition 3 should pass because the job posting explicitly requires the
  applicant to reside in the United States. The location requirement should be treated as
  satisfied. If the current implementation marks Condition 3 as failed, the test should expose
  that as a known expected failure rather than changing the expected result to make the test
  pass. The final relevance verdict must still follow the remaining conditions, so passing
  Condition 3 alone does not automatically make the posting Relevant.
  Why, from the ad: The posting explicitly says "reside in the United States." This is
  sufficient evidence that the location requirement is met. The agent should recognize the
  stated requirement instead of incorrectly rejecting it because of its wording.

The posting is REAL (tests/fixtures/physician_reviewer.json, copied from live run 1). Rule v2
rev 3 trusts the office tag "Remote (Arizona)" and fails condition 3, so the condition-3 test is
marked expectedFailure: it is reported on every run as an expected failure, and it starts
reporting "unexpected success" the day the rule is fixed."""
import json
import pathlib
import unittest

from jsagent import persona, posting, rule
from tests import helpers

FX = json.loads((pathlib.Path(__file__).parent / "fixtures" / "physician_reviewer.json").read_text())
P = posting.normalize(FX["job"], "oscar")
REC = rule.judge(P, persona.public_view(helpers.load_persona()))


class PhysicianReviewer(unittest.TestCase):
    def test_the_ad_says_reside_in_the_united_states(self):
        self.assertIn("reside in the United States", P["content"])

    @unittest.expectedFailure
    def test_condition_3_passes_because_the_ad_allows_anywhere_in_the_us(self):
        self.assertNotIn(3, REC["failed_conditions"])

    def test_verdict_still_follows_the_other_conditions(self):
        others = [n for n in REC["failed_conditions"] if n != 3]
        self.assertTrue(others, "some condition other than 3 fails")
        self.assertEqual(REC["verdict"], "Not Relevant")


if __name__ == "__main__":
    unittest.main()
