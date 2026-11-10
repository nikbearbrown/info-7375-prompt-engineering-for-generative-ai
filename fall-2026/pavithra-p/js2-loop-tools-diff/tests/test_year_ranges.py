"""My year-range test for the review packet (REVIEW-PACKET.md), written on 2026-11-10 before the fix.

The four phrases and the expected answers are mine (Rohan has about 2 years). Claude Code typed them as code.
a and b are real lines from saved postings (Stripe 6176758, Twilio 7661919); c and d are CONSTRUCTED.
"""
import unittest

from agent import config, resume, rule

PERSONA = resume.load(config.RESUME)


def experience_met(text):
    job = {"id": 1, "title": "Software Engineer", "location": {"name": "Remote, US"},
           "content": f"<p>{text}. Python and AWS.</p>"}
    return rule.judge(job, PERSONA).checks["experience"]


class YearRangeTests(unittest.TestCase):
    def test_a_range_2_to_12_plus_passes(self):
        self.assertTrue(experience_met("2–12+ years of industry software engineering experience"))

    def test_b_minimum_2_to_3_plus_passes(self):
        self.assertTrue(experience_met("Minimum 2-3+ years of hands-on experience"))

    def test_c_range_3_to_5_fails(self):
        self.assertFalse(experience_met("3-5 years in backend"))

    def test_d_5_plus_fails(self):
        self.assertFalse(experience_met("5+ years of experience"))


if __name__ == "__main__":
    unittest.main()
