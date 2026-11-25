"""JS3 Step 3: the filter (FILTER.md v1.2 section 1) and the evidence labels (section 2), tested on made-up postings only.

Each test_Wn_ is one wrong version from FILTER.md section 4: it passes on the filter as written and fails on that wrong version.
Written before jsagent/filter.py and jsagent/shortlist.py existed.
"""
import unittest

from jsagent import filter as flt
from jsagent import shortlist

GOOD = ("Requirements: 3+ years of experience building pipelines. You have strong Python and SQL, and experience with Airflow, "
        "dbt and Snowflake.")


def P(title="Data Engineer", loc="Boston, MA", content=GOOD, board="t", pid="1"):
    return {"board": board, "id": pid, "title": title, "location": {"name": loc}, "content": content,
            "absolute_url": "https://example.test/" + pid}


class WrongVersions(unittest.TestCase):
    def test_W1_role_needs_whole_phrase(self):
        for title in ("Data Center Technician", "Compliance Analyst", "Software Engineer, Data Engineering"):
            r = flt.evaluate(P(title=title))
            self.assertEqual(r["rules"]["F1"]["result"], "fail", title)
            self.assertEqual(r["bucket"], "rejected", title)
        for title in ("Senior Data Engineer", "Analytics Engineer II", "Software Engineer - Data Platform", "BI Engineer",
                      "Business Intelligence Developer", "data analyst"):
            self.assertEqual(flt.evaluate(P(title=title))["rules"]["F1"]["result"], "pass", title)

    def test_W2_topic_words_case_sensitive_whole_word(self):
        r = flt.evaluate(P(content="3 years of experience. Ideas that spark joy in scalable systems, using SQL and Python."))
        self.assertEqual(r["topic_words"], ["Python", "SQL"])
        r = flt.evaluate(P(content="3 years of experience. Spark, Scala, PowerBI, GitHub, Flink, Kubernetes."))
        self.assertEqual(r["topic_words"], ["Scala", "Spark"])  # PowerBI, GitHub (not Git), Flink, Kubernetes don't count

    def test_W3_repeats_count_once(self):
        many = flt.evaluate(P(content="3 years of experience. " + "SQL " * 15))
        five = flt.evaluate(P(content="3 years of experience. SQL, Python, Airflow, dbt, Snowflake."))
        self.assertEqual(many["topic_words"], ["SQL"])
        self.assertGreater(five["score"], many["score"] or 0)

    def test_W4_missing_description_is_cannot_tell(self):
        for content in ("", "   "):
            r = flt.evaluate(P(content=content))
            self.assertEqual(r["bucket"], "cannot_tell")
            self.assertIn("description", r["missing"])

    def test_W5_years_from_first_experience_phrase(self):
        r = flt.evaluate(P(content="3+ years of experience with Python and SQL. Senior folks have 8+ years of experience."))
        self.assertEqual(r["years"], 3)
        r = flt.evaluate(P(content="We were founded 12 years ago. Python and SQL."))
        self.assertIsNone(r["years"])
        self.assertEqual(r["bucket"], "kept")

    def test_W6_a_mention_is_not_support(self):
        r = flt.evaluate(P(content="3 years of experience. Must have SQL and Airflow. Python a plus."))
        claims = {c["claim"]: c for c in shortlist.claims(r)}
        self.assertEqual(claims["requires Python"]["label"], "insufficient")
        self.assertEqual(claims["requires SQL"]["label"], "supported")

    def test_W7_bare_remote_is_cannot_tell(self):
        r = flt.evaluate(P(loc="Remote"))
        self.assertEqual(r["rules"]["F3"]["result"], "cannot_tell")
        self.assertEqual(r["bucket"], "cannot_tell")
        self.assertEqual(flt.evaluate(P(loc="Remote - US"))["location_kind"], "remote_us")

    def test_W9_sponsor_word_is_not_an_offer(self):
        for text in ("We are unable to sponsor visas for this role.", "We do not offer visa sponsorship.",
                     "We run event sponsorship programs."):
            r = flt.evaluate(P(content=GOOD + " " + text))
            self.assertEqual(r["score_parts"]["visa"], 0, text)
        r = flt.evaluate(P(content=GOOD + " Visa sponsorship is available for this position."))
        self.assertEqual(r["score_parts"]["visa"], 10)
        self.assertEqual(r["visa"], "offered")

    def test_W10_one_location_bonus(self):
        r = flt.evaluate(P(loc="Boston, MA; Remote - US"))
        self.assertEqual(r["score_parts"]["location"], 10)


class FilterRules(unittest.TestCase):
    def test_kept_and_score_parts(self):
        r = flt.evaluate(P())
        self.assertEqual(r["bucket"], "kept")
        self.assertEqual(r["topic_words"], ["Airflow", "Python", "SQL", "Snowflake", "dbt"])
        self.assertEqual(r["score_parts"], {"topics": 40, "years": 16, "location": 10, "visa": 0})
        self.assertEqual(r["score"], 66)

    def test_max_score_is_100(self):
        content = ("2 years of experience. Python SQL Scala Bash Spark Airflow dbt Kafka Databricks Pandas Snowflake AWS. "
                   "Visa sponsorship is available.")
        self.assertEqual(flt.evaluate(P(content=content))["score"], 100)

    def test_seniority(self):
        for title in ("Staff Data Engineer", "Lead Analytics Engineer", "Data Engineering Manager, Data Platform",
                      "Data Analyst Intern", "Data Platform Architect"):
            self.assertEqual(flt.evaluate(P(title=title))["rules"]["F2"]["result"], "fail", title)
        self.assertEqual(flt.evaluate(P(title="Senior Data Engineer"))["rules"]["F2"]["result"], "pass")

    def test_location(self):
        cases = {"Boston, MA": ("pass", "boston"), "Remote - US": ("pass", "remote_us"), "New York, NY": ("pass", "us"),
                 "London, United Kingdom": ("fail", None), "Remote - Canada": ("fail", None), "London": ("cannot_tell", None),
                 "": ("cannot_tell", None), "New York, NY; London, United Kingdom": ("pass", "us")}
        for loc, (result, kind) in cases.items():
            r = flt.evaluate(P(loc=loc))
            self.assertEqual((r["rules"]["F3"]["result"], r["location_kind"]), (result, kind), loc)

    def test_years_limit_and_bonus(self):
        for n, bucket, bonus in ((3, "kept", 16), (4, "kept", 0), (5, "kept", 0), (6, "rejected", None)):
            r = flt.evaluate(P(content=f"{n}+ years of experience with Python and SQL."))
            self.assertEqual(r["bucket"], bucket, n)
            if bonus is not None:
                self.assertEqual(r["score_parts"]["years"], bonus, n)

    def test_threshold_two_topic_words(self):
        r = flt.evaluate(P(content="3 years of experience with Python."))
        self.assertEqual((r["bucket"], r["rules"]["T3"]["result"]), ("rejected", "fail"))
        self.assertTrue(r["closest_call"])

    def test_reject_on_evidence_beats_cannot_tell(self):
        r = flt.evaluate(P(title="Staff Data Engineer", content=""))
        self.assertEqual(r["bucket"], "rejected")

    def test_html_entities_do_not_create_matches(self):
        r = flt.evaluate(P(content="3 years of experience. Python &amp; SQL"))
        self.assertEqual(r["topic_words"], ["Python", "SQL"])


class Claims(unittest.TestCase):
    def test_years_claim_and_abstention(self):
        c = {x["claim"]: x for x in shortlist.claims(flt.evaluate(P()))}
        self.assertEqual(c["requires at most 5 years"]["label"], "supported")
        self.assertIn("3+ years", c["requires at most 5 years"]["span"])
        c = {x["claim"]: x for x in shortlist.claims(flt.evaluate(P(content="Python and SQL every day.")))}
        self.assertEqual(c["requires at most 5 years"]["label"], "insufficient")
        self.assertTrue(c["requires at most 5 years"]["answer"].startswith("I cannot tell from the posting"))

    def test_visa_claims(self):
        c = {x["claim"]: x for x in shortlist.claims(flt.evaluate(P()))}
        self.assertEqual(c["offers visa sponsorship"]["label"], "insufficient")
        self.assertTrue(c["offers visa sponsorship"]["answer"].startswith("I cannot tell from the posting"))
        r = flt.evaluate(P(content=GOOD + " We are unable to sponsor visas."))
        c = {x["claim"]: x for x in shortlist.claims(r)}
        self.assertEqual(c["offers visa sponsorship"]["label"], "contradicted")

    def test_not_required_contradicts(self):
        r = flt.evaluate(P(content="3 years of experience. Must have SQL and Python. Tableau is not required."))
        c = {x["claim"]: x for x in shortlist.claims(r)}
        self.assertEqual(c["requires Tableau"]["label"], "contradicted")

    def test_every_claim_has_a_label_and_field(self):
        for x in shortlist.claims(flt.evaluate(P())):
            self.assertIn(x["label"], ("supported", "contradicted", "insufficient"))
            self.assertIn(x["field"], ("title", "location", "description"))


if __name__ == "__main__":
    unittest.main()
