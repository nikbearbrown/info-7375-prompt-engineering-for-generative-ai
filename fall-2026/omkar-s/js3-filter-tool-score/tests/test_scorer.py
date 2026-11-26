"""The filter (FILTER.md section 1) on CONSTRUCTED postings. Each wrong version WV1-WV7 must fail >= 1 test here."""
import unittest

from js3 import scorer
from js3 import textutil as tu
from tests.helpers import cfg, persona, posting

REQ = "<h3>Requirements</h3><ul><li>{}</li></ul>"


def ev(p, version=None):
    return scorer.evaluate(p, persona(), cfg(version))


class WholeWord(unittest.TestCase):  # WV1
    def test_java_does_not_match_javascript(self):
        r = ev(posting(body="Requirements: 2+ years of experience. We use JavaScript and PostgreSQL daily."))
        self.assertNotIn("Java", r["skills_found"])
        self.assertIn("PostgreSQL", r["skills_found"])
        self.assertNotIn("SQL", r["skills_found"])

    def test_skill_with_punctuation(self):
        self.assertIn("Node.js", ev(posting(body="We write Node.js services."))["skills_found"])


class GatesAndRanking(unittest.TestCase):  # WV2
    def test_staff_with_many_skills_is_rejected_entry_with_three_is_kept(self):
        many = "Python, Java, SQL, TypeScript, Kafka, Redis, AWS, Kubernetes, Docker, Jenkins"
        staff = ev(posting(title="Staff Software Engineer", body=f"Requirements: {many}."))
        entry = ev(posting(title="Software Engineer I", body="Requirements: 1+ years of experience with Python, SQL and AWS."))
        self.assertEqual(staff["verdict"], "reject")
        self.assertFalse(staff["gates"]["G2"]["pass"])
        self.assertEqual(entry["verdict"], "keep")

    def test_skill_points_are_capped_at_8(self):
        many = "Python, Java, SQL, TypeScript, Kafka, Redis, AWS, Kubernetes, Docker, Jenkins"
        r = ev(posting(body=f"Requirements: {many}."))
        self.assertEqual(sum(1 for l in r["lines"] if l["rule"] == "K1"), 8)

    def test_lines_sum_to_the_score(self):
        r = ev(posting(title="Senior Software Engineer", body="Requirements: 2+ years of experience. Python, Rust, AWS."))
        self.assertAlmostEqual(sum(l["points"] for l in r["lines"]), r["score"])
        self.assertEqual(r["score"], 3 - 2 + 2 + 0.25 + 1)

    def test_threshold_is_inclusive(self):
        r = ev(posting(title="Software Engineer", body="Requirements: Python and AWS."))  # 3 + 2 = 5.0
        self.assertEqual(r["score"], 5.0)
        self.assertEqual(r["verdict"], "keep")
        self.assertTrue(r["close_call"])

    def test_below_threshold_rejected_with_reason(self):
        r = ev(posting(title="Software Engineer", body="Requirements: Python."))
        self.assertEqual(r["verdict"], "reject")
        self.assertIn("score 4.0 < threshold 5.0", r["reasons"])


class Years(unittest.TestCase):  # WV4
    def test_company_age_is_not_a_requirement(self):
        r = ev(posting(body="For over 10 years, Fixture has served restaurants. Requirements: 2+ years of experience with Python and AWS."))
        self.assertEqual(r["gates"]["G3"]["min_years"], 2)
        self.assertTrue(r["gates"]["G3"]["pass"])

    def test_more_than_three_years_rejects(self):
        r = ev(posting(body="You have 5+ years of professional experience with Python, Java, AWS and SQL."))
        self.assertFalse(r["gates"]["G3"]["pass"])
        self.assertEqual(r["verdict"], "reject")

    def test_smallest_minimum_wins(self):
        my, st = tu.min_years("5+ years of experience in industry, or 2+ years of experience with an MS")
        self.assertEqual(my, 2)

    def test_range_takes_its_minimum(self):
        self.assertEqual(tu.min_years("2-5 years of experience building products")[0], 2)

    def test_number_words_are_not_read(self):  # the documented gap
        self.assertIsNone(tu.min_years("at least three years of experience")[0])


class Location(unittest.TestCase):  # WV6
    def test_bare_or_foreign_remote_fails(self):
        for loc in ("Remote", "Remote - EMEA", "Remote (Canada)"):
            self.assertFalse(ev(posting(location=loc))["gates"]["G1"]["pass"], loc)

    def test_us_remote_passes(self):
        for loc in ("Remote, US", "Remote US", "Remote (United States)"):
            self.assertTrue(ev(posting(location=loc))["gates"]["G1"]["pass"], loc)

    def test_city_state_usa_passes_from_v1_1(self):
        p = posting(location="New York, New York, USA")
        self.assertFalse(ev(p, "1.0")["gates"]["G1"]["pass"])
        self.assertTrue(ev(p, "1.1")["gates"]["G1"]["pass"])
        self.assertTrue(ev(p)["gates"]["G1"]["pass"])

    def test_two_letter_suffix_needs_a_us_office(self):
        self.assertFalse(ev(posting(location="Munich, DE"))["gates"]["G1"]["pass"])
        self.assertTrue(ev(posting(location="Austin, TX", offices=["Austin, Texas, United States"]))["gates"]["G1"]["pass"])


class Abstention(unittest.TestCase):  # WV5
    def test_short_content_is_cannot_tell_not_reject(self):
        p = posting(body="")
        p["content"] = p["html"] = "Apply now."
        r = ev(p)
        self.assertEqual(r["verdict"], "cannot_tell")
        self.assertTrue(r["reasons"][0].startswith("AB1"))

    def test_empty_title_is_cannot_tell(self):
        self.assertEqual(ev(posting(title=""))["verdict"], "cannot_tell")


class TitleRules(unittest.TestCase):
    def test_presales_and_developer_advocate_get_no_t2_from_v1_2(self):
        for t in ("Lead PreSales Engineer", "Developer Advocate"):
            self.assertTrue(any(l["rule"] == "T2" for l in ev(posting(title=t), "1.1")["lines"]), t)
            self.assertFalse(any(l["rule"] == "T2" for l in ev(posting(title=t))["lines"]), t)

    def test_sales_engineer_gets_no_title_points(self):
        r = ev(posting(title="Sales Engineer"))
        self.assertFalse(any(l["rule"] in ("T1", "T2") for l in r["lines"]))

    def test_lead_is_a_penalty_not_a_gate(self):
        r = ev(posting(title="Lead Engineer, Applied AI", body="Requirements: Python, AWS, Kafka, Redis, SQL."))
        self.assertTrue(r["gates"]["G2"]["pass"])
        self.assertIn(-2.0, [l["points"] for l in r["lines"]])


if __name__ == "__main__":
    unittest.main()


class YearsV15V16(unittest.TestCase):
    def test_plus_years_without_experience_word_from_v1_5(self):
        body = "Requirements: Solid engineering experience. 5+ years building and shipping software. Python, AWS, Java."
        self.assertTrue(ev(posting(body=body), "1.4")["gates"]["G3"]["pass"])
        self.assertFalse(ev(posting(body=body), "1.5")["gates"]["G3"]["pass"])

    def test_sub_requirement_does_not_set_the_minimum_from_v1_6(self):
        body = "Requirements: 5+ years of engineering experience, with 2+ years building ML systems. Python, AWS, Java."
        self.assertEqual(ev(posting(body=body), "1.5")["gates"]["G3"]["min_years"], 2)
        self.assertEqual(ev(posting(body=body), "1.6")["gates"]["G3"]["min_years"], 5)

    def test_and_is_not_a_sub_requirement(self):
        body = "Requirements: a BS and 2+ years of experience, or 5+ years of experience. Python, AWS."
        self.assertEqual(ev(posting(body=body))["gates"]["G3"]["min_years"], 2)

    def test_only_sub_requirements_still_count(self):
        body = "Requirements: experience with distributed systems, with 4+ years of experience in Go. Python, AWS."
        self.assertEqual(ev(posting(body=body))["gates"]["G3"]["min_years"], 4)
