"""Full-time only (rule amendment 4, decided by Riya 2026-11-09: "i dont want to see coops and any type of part time
jobs i just want full time jobs"; Contract and Temporary included, by her OK in chat).
Written and committed BEFORE the change to jsagent/rules.py and jsagent/ats.py.
Run: python3 -m unittest tests.test_fulltime -v
"""

import json
import unittest
from pathlib import Path

from jsagent import ats, rules
from jsagent.contract import validate_verdict

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "arya-sahni.json").read_text())
SKILLS = "<p>You will use Python and SQL every day, with MLflow for experiments.</p>"


def posting(title, employment=None):
    """CONSTRUCTED posting that passes every other part of the rule."""
    p = {"id": "t-" + title, "title": title, "content": SKILLS, "location": {"name": "Boston, Massachusetts"}}
    if employment is not None:
        p["employment"] = employment
    return p


def verdict(p):
    return rules.judge(p, RESUME)["verdict"]


class TestTitleWords(unittest.TestCase):
    """Greenhouse has no employment-type field, so the title is the only signal there."""

    def test_coop_part_time_contract_temporary_titles_are_excluded(self):
        for t in ["Data Science Co-op (Spring 2027)", "Data Engineer, Part-time", "ML Engineer - Part Time",
                  "Data Engineer (6-month contract)", "AI Engineer (Contract)", "Analytics Engineer, Temporary",
                  "Data Engineer - Contractor", "Machine Learning Engineer (Fixed-Term)"]:
            self.assertEqual(verdict(posting(t)), "not_relevant", t)

    def test_reason_is_recorded(self):
        v = rules.judge(posting("AI Engineer (Contract)"), RESUME)
        self.assertIn("not full-time", v["justification"])
        validate_verdict(v, v["id"])

    def test_lookalikes_stay_relevant(self):
        # Whole-word: "Contracts", "Contracting", "Temporal", "Cooperative" are not employment types.
        for t in ["Data Engineer, Contracts Platform", "ML Engineer, Temporal Data", "AI Engineer, Cooperative Agents",
                  "Data Scientist (Full-time)"]:
            self.assertEqual(verdict(posting(t)), "relevant", t)


class TestEmploymentField(unittest.TestCase):
    """Ashby (employmentType) and SmartRecruiters (typeOfEmployment) say it directly."""

    def test_ashby_field_is_carried_by_the_adapter(self):
        raw = json.dumps({"jobs": [{"id": "a1", "title": "Data Engineer", "employmentType": "PartTime",
                                    "location": "Boston, Massachusetts", "descriptionHtml": SKILLS}]}).encode()
        p = ats.ashby_parse(raw, "x")[0]
        self.assertEqual(p["employment"], "PartTime")
        self.assertEqual(verdict(p), "not_relevant")

    def test_smartrecruiters_full_time_label_is_normalized(self):
        raw = json.dumps({"content": [{"id": "s1", "name": "Data Engineer", "location": {"city": "Boston"},
                                       "typeOfEmployment": {"id": "permanent", "label": "Full-time"}}]}).encode()
        self.assertEqual(ats.smartrecruiters_parse(raw, "x")[0]["employment"], "FullTime")

    def test_non_full_time_field_excludes_even_with_a_clean_title(self):
        for e in ["PartTime", "Contract", "Temporary", "Intern"]:
            self.assertEqual(verdict(posting("Data Engineer", employment=e)), "not_relevant", e)

    def test_full_time_field_or_no_field_is_unchanged(self):
        self.assertEqual(verdict(posting("Data Engineer", employment="FullTime")), "relevant")
        self.assertEqual(verdict(posting("Data Engineer")), "relevant")  # Greenhouse: no field, title decides


if __name__ == "__main__":
    unittest.main()
