"""Aravind's own test: a non-full-time posting should be rejected under R1."""

import unittest

from job_agent import filter as flt


class MyRuleTest(unittest.TestCase):

    def test_rejects_internship_posting(self):
        posting = {
            "id": "mine-1",
            "title": "Software Engineer Intern",
            "employmentType": "Intern",
            "location": "San Francisco",
            "address": {
                "postalAddress": {
                    "addressCountry": "United States",
                    "addressRegion": "California",
                    "addressLocality": "San Francisco",
                }
            },
            "secondaryLocations": [],
            "descriptionPlain": "This is a software engineering internship.",
            "publishedAt": "2026-11-20T00:00:00+00:00",
            "jobUrl": "https://example.com/mine-1",
        }

        record = flt.judge(posting, flt.load_profile(), flt.load_rules())

        self.assertEqual(record["fate"], "rejected")
        self.assertEqual(record["deciding_rule"], "R1")


if __name__ == "__main__":
    unittest.main()
