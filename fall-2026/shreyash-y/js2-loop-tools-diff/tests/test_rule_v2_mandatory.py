"""Regression test for the defect found in patch revision 2 (review/11-finding-rev2.txt). Written
2026-11-09, BEFORE patch revision 3. It must fail on rev 2.

17 REAL postings (tests/fixtures/dropped_requirement_postings.json). 14 state a mandatory minimum
under "What We Require:", "Education and Experience:" or "What We're Looking For", and condition 5
must fail with that number. 3 put their years under "Preferred skills:" or "Preferred experience
(guidance, not gates)", and condition 5 must pass. That is Shreyash's 2026-10-31 decision: mandatory
qualifications only. Plus CONSTRUCTED edges for the same traps."""
import json
import pathlib
import unittest

from jsagent import persona, providers, rule
from tests import helpers

FX = json.loads((pathlib.Path(__file__).parent / "fixtures" / "dropped_requirement_postings.json").read_text())
VIEW = persona.public_view(helpers.load_persona())


def parsed(e):
    body = json.dumps({"jobs": [e["job"]]} if e["ats"] == "greenhouse" else [e["job"]]).encode()
    return providers.parse(e["ats"], e["board"], 200, body)[0][0]


def c5(p):
    rec = rule.judge(p, VIEW)
    return rec, next(l for l in rec["conditions"] if l["n"] == 5)


class RealMandatoryAndPreferred(unittest.TestCase):
    def test_seventeen_real_postings(self):
        self.assertEqual(len(FX["postings"]), 17)
        for e in FX["postings"]:
            p = parsed(e)
            rec, line = c5(p)
            if e["expected_years"] is None:
                self.assertNotIn(5, rec["failed_conditions"], p["title"])
            else:
                self.assertIn(5, rec["failed_conditions"], p["title"])
                self.assertIn(f"requires {e['expected_years']} years", line["detail"], p["title"])


class ConstructedTraps(unittest.TestCase):
    def judge(self, text):
        return rule.judge(providers.parse("ashby", "x", 200, json.dumps({"jobs": [{
            "id": "c", "title": "Software Engineer", "department": "Engineering", "location": "Boston, MA",
            "descriptionPlain": "Python and SQL. " + text}]}).encode())[0][0], VIEW)["failed_conditions"]

    def test_inline_preferred_before_a_requirement_heading(self):
        self.assertIn(5, self.judge("Kubernetes experience preferred What We Require: 5+ years of professional experience."))

    def test_unknown_heading_then_requirement(self):
        self.assertIn(5, self.judge("Education and Experience: Bachelor's degree. 6+ years of progressive experience."))

    def test_early_compensation_word_does_not_hide_requirements(self):
        self.assertIn(5, self.judge("We offer competitive compensation. You will own services. 5+ years building backends."))

    def test_preferred_heading_years_do_not_count(self):
        self.assertNotIn(5, self.judge("Preferred skills: 6+ years of experience in AI solutions."))

    def test_preferred_after_the_number_counts_as_preferred(self):
        self.assertNotIn(5, self.judge("6+ years of Go experience preferred."))

    def test_ideally_about_the_domain_is_still_required(self):
        self.assertIn(5, self.judge("What We're Looking For 5+ years of payroll experience, ideally within a large company."))


if __name__ == "__main__":
    unittest.main()
