"""Written from FILTER.md v1.0 BEFORE any filter code existed (2026-11-25). Each test names the rule it checks."""
import unittest
from tests.helpers import filt, cfg, P

TWO = "You will write SQL and Python every day."

class R1_TitleWholeWord(unittest.TestCase):
    def ev(self, title, text=TWO): return filt().evaluate(P(title=title, text=text), cfg())
    def test_role_words_pass(self):
        for t in ["Data Analyst", "Product Analytics Associate", "Business Intelligence Developer", "BI Developer", "Customer Insights Associate"]:
            self.assertTrue(self.ev(t)["r1"], t)
    def test_case_insensitive(self):
        self.assertTrue(self.ev("data ANALYST")["r1"])
    def test_bi_inside_a_word_does_not_match(self):          # wrong version 1: substring match
        for t in ["Mobile Engineer, Capabilities", "Accessibility Engineer", "Mobility Specialist", "Possibility Lab Engineer"]:
            self.assertFalse(self.ev(t)["r1"], t)
    def test_analyst_inside_a_word_does_not_match(self):
        self.assertFalse(self.ev("Psychoanalysts Liaison")["r1"])
        self.assertFalse(self.ev("Insightsful Engineer")["r1"])
    def test_no_role_word_rejected(self):
        d = self.ev("Software Engineer")
        self.assertEqual(d["status"], "rejected"); self.assertIn("R1", d["failed"])

class R2_Seniority(unittest.TestCase):
    def ev(self, title): return filt().evaluate(P(title=title, text=TWO), cfg())
    def test_seniority_words_reject(self):
        for t in ["Senior Data Analyst", "Sr. Data Analyst", "Sr Analyst", "Lead Analyst", "Staff Analytics Engineer",
                  "Principal BI Analyst", "Manager, Analytics", "Director of Insights", "Head of Analytics", "VP, Analytics"]:
            d = self.ev(t)
            self.assertTrue(d["r2_reject"], t); self.assertEqual(d["status"], "rejected", t); self.assertIn("R2", d["failed"], t)
    def test_seniority_whole_word_only(self):
        for t in ["Leadership Development Analyst", "Staffing Analyst", "Headcount Analyst", "Management Analyst"]:
            self.assertFalse(self.ev(t)["r2_reject"], t)

class R3_TwoSkills(unittest.TestCase):
    def ev(self, text): return filt().evaluate(P(text=text), cfg())
    def test_one_skill_fails(self):
        d = self.ev("Proficiency in SQL is required.")
        self.assertFalse(d["r3"]); self.assertEqual(d["status"], "rejected"); self.assertIn("R3", d["failed"])
    def test_two_skills_pass(self):
        d = self.ev(TWO); self.assertTrue(d["r3"]); self.assertEqual(sorted(d["skills"]), ["Python", "SQL"])
    def test_phrases(self):
        d = self.ev("Build dashboards in Power BI and run A/B testing.")
        self.assertEqual(sorted(d["skills"]), ["A/B testing", "Power BI"])
    def test_skill_whole_word_only(self):          # NoSQL is not SQL; "pythonic" is not Python
        d = self.ev("Experience with NoSQL stores and pythonic code.")
        self.assertEqual(d["skills"], []); self.assertFalse(d["r3"])
    def test_repeated_skill_counts_once(self):
        d = self.ev("SQL. SQL. SQL. More SQL.")
        self.assertEqual(d["skills"], ["SQL"]); self.assertFalse(d["r3"])

class R4_Years(unittest.TestCase):
    def ev(self, text): return filt().evaluate(P(text=TWO + " " + text), cfg())
    def test_years_extraction_top_of_range(self):
        f = filt()
        self.assertEqual(max(f.years_in("2-4 years of experience")), 4)
        self.assertEqual(max(f.years_in("1–3 years of experience")), 3)
        self.assertEqual(max(f.years_in("5+ years of experience")), 5)
        self.assertEqual(max(f.years_in("3 to 5 years of experience")), 5)
        self.assertEqual(f.years_in("No experience mentioned"), [])
    def test_up_to_three_passes(self):
        d = self.ev("1-3 years of experience."); self.assertIs(d["r4"], True); self.assertEqual(d["years_max"], 3)
        self.assertEqual(d["status"], "kept")
    def test_range_top_above_three_fails(self):
        d = self.ev("2-4 years of experience."); self.assertIs(d["r4"], False); self.assertIn("R4", d["failed"])
        self.assertEqual(d["status"], "rejected")
    def test_largest_counts(self):
        d = self.ev("1 year of SQL and 5+ years of experience overall."); self.assertEqual(d["years_max"], 5); self.assertIs(d["r4"], False)
    def test_unstated_is_allowed_but_unknown(self):
        d = self.ev(""); self.assertIsNone(d["r4"]); self.assertIsNone(d["years_max"]); self.assertEqual(d["status"], "kept")

class Score(unittest.TestCase):
    def test_title_plus_two_skills_is_exactly_five_and_kept(self):
        d = filt().evaluate(P(text=TWO), cfg()); self.assertEqual(d["score"], 5); self.assertEqual(d["status"], "kept")
    def test_skill_cap_is_five(self):
        d = filt().evaluate(P(text="SQL Python Tableau Excel dbt Looker Snowflake ETL"), cfg()); self.assertEqual(d["score"], 8)
    def test_penalties(self):
        d = filt().evaluate(P(title="Senior Data Analyst", text=TWO + " 5+ years of experience."), cfg())
        self.assertEqual(d["score"], 3 + 2 - 3 - 3); self.assertEqual(d["status"], "rejected")
    def test_rule_failure_rejects_even_with_high_score(self):
        d = filt().evaluate(P(title="Senior Data Analyst", text="SQL Python Tableau Excel dbt Looker Snowflake ETL"), cfg())
        self.assertEqual(d["status"], "rejected")

class Ranking(unittest.TestCase):          # wrong version 2: rank by word count
    def test_senior_posting_listing_every_tool_never_ranks(self):
        f = filt(); c = cfg()
        everything = " ".join(["SQL Python Tableau Power BI Excel dbt Looker Snowflake A/B testing ETL"] * 5)
        ds = [f.evaluate(P(id="a", title="Data Analyst", text=TWO), c),
              f.evaluate(P(id="b", title="Senior Staff Data Analyst", text=everything), c),
              f.evaluate(P(id="c", title="Software Engineer", text=everything), c)]
        ranked = f.rank(ds)
        self.assertEqual([d["id"] for d in ranked], ["a"])
    def test_more_skills_ranks_higher_but_capped(self):
        f = filt(); c = cfg()
        ds = [f.evaluate(P(id="two", text=TWO), c),
              f.evaluate(P(id="four", text="SQL Python Tableau Looker"), c),
              f.evaluate(P(id="many", text=" ".join(["SQL Python Tableau Looker dbt Excel"] * 10)), c)]
        self.assertEqual([d["id"] for d in f.rank(ds)], ["many", "four", "two"])
        self.assertEqual(f.rank(ds)[0]["score"], 8)

class Missing(unittest.TestCase):          # FILTER.md section 3
    def test_missing_text_is_cannot_tell_not_rejected(self):
        for t in ["", "   ", None]:
            d = filt().evaluate(P(text=t), cfg()); self.assertEqual(d["status"], "cannot_tell", repr(t))
    def test_missing_title_is_cannot_tell(self):
        d = filt().evaluate(P(title="", text=TWO), cfg()); self.assertEqual(d["status"], "cannot_tell")
    def test_missing_location_does_not_change_verdict(self):
        a = filt().evaluate(P(text=TWO), cfg()); b = filt().evaluate(P(text=TWO, location=None), cfg())
        self.assertEqual((a["status"], a["score"]), (b["status"], b["score"]))

class FilterFile(unittest.TestCase):
    def test_numbers_come_from_the_filter_file(self):
        c = dict(cfg()); c["max_years"] = 5
        d = filt().evaluate(P(text=TWO + " 2-4 years of experience."), c); self.assertEqual(d["status"], "kept")
    def test_decision_records_filter_version(self):
        self.assertEqual(filt().evaluate(P(text=TWO), cfg())["filter_version"], "1.0")

if __name__ == "__main__": unittest.main()
