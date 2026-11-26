"""Optional rule keys added after the v1 audit (FILTER.md Revisions). Absent keys = v1 behaviour."""
import unittest

from jsagent3.filter import decide, load_rules

BODY = "About us\nWe use Java and SQL everywhere.\nRequirements\n- 5+ years\n- AWS\n- distributed systems\n"


def P(body=BODY, location="Seattle, WA"):
    return {"id": "t", "title": "Software Engineer", "body": body, "location": location}


class Options(unittest.TestCase):
    def setUp(self):
        self.v1 = load_rules("v1")

    def test_v1_unchanged_by_missing_keys(self):
        self.assertTrue(decide(P(), self.v1)["keep"])
        self.assertTrue(decide(P(location="Dublin"), self.v1)["keep"])

    def test_us_required(self):
        r = dict(self.v1, us_required=True)
        self.assertFalse(decide(P(location="Dublin"), r)["keep"])
        self.assertEqual(decide(P(location="N/A"), r)["reason"], "location unknown")

    def test_max_years(self):
        r = dict(self.v1, max_required_years=2)
        self.assertFalse(decide(P(), r)["keep"])
        self.assertTrue(decide(P(BODY.replace("5+", "0-2")), r)["keep"])

    def test_topic_in_required_only(self):
        r = dict(self.v1, topic_in_required_only=True)
        self.assertEqual(sorted(decide(P(), r)["topics"]), ["T6", "T8"])


if __name__ == "__main__":
    unittest.main()
