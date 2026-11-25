"""JS1 tests for the code JS2 carries over unchanged (resume.py, validate.py, rule.py), copied from
../js1-contract-and-watch/tests/test_earlybird.py. JS1's watch, fetch and Claude tests are replaced by test_js2.py."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from earlybird import Refused, rule, validate  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402

RESUME_PATH = ROOT / "data/resume/rohan-desai.example.json"
DAY1 = json.loads((ROOT / "data/raw/2026-10-14/ashby_commure.json").read_text(encoding="utf-8"))["jobs"]
DAY2 = json.loads((ROOT / "data/raw/2026-10-23/ashby_commure.json").read_text(encoding="utf-8"))["jobs"]
EXPECTED_NEW = {p["id"] for p in DAY2} - {p["id"] for p in DAY1}


def constructed(title, country="USA", desc="Build web services."):
    """A CONSTRUCTED posting for rule tests; not from any board."""
    return {"id": "constructed-" + title.lower().replace(" ", "-"), "title": title,
            "address": {"postalAddress": {"addressCountry": country}}, "descriptionPlain": desc}


class Refusals(unittest.TestCase):
    # row 13
    def test_real_resume_refused(self):
        real = json.loads(RESUME_PATH.read_text(encoding="utf-8"))
        real["_comment"] = "my resume"
        real["personal"].update(email="someone@gmail.com", phone="(617) 222-0127")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "resume.json"
            p.write_text(json.dumps(real), encoding="utf-8")
            with self.assertRaises(Refused):
                load_resume(p)

    def test_fictional_resume_accepted(self):
        self.assertEqual(load_resume(RESUME_PATH)["personal"]["name"], "Rohan Desai")


class Validator(unittest.TestCase):
    def setUp(self):
        self.resume = load_resume(RESUME_PATH)
        self.posting = next(p for p in DAY2 if p["id"] in EXPECTED_NEW)
        self.good = {"posting_id": self.posting["id"], "verdict": "not_relevant", "justification": "Senior title.",
                     "resume_fields": ["experience"], "posting_fields": ["title"]}

    def test_good_passes(self):
        self.assertEqual(validate.errors(self.good, self.posting, self.resume), [])

    def test_validator_rejects_bad_verdict_and_extra_keys(self):
        for change in ({"verdict": "maybe"}, {"confidence": 0.9}):
            self.assertTrue(validate.errors({**self.good, **change}, self.posting, self.resume))

    # row 6
    def test_validator_rejects_missing_or_fake_citations(self):
        for change in ({"resume_fields": []}, {"posting_fields": []}, {"resume_fields": ["years_of_experience"]},
                       {"posting_fields": ["salary"]}):
            self.assertTrue(validate.errors({**self.good, **change}, self.posting, self.resume), change)

    def test_validator_rejects_wrong_posting(self):
        other = next(p for p in DAY2 if p["id"] != self.posting["id"])
        self.assertTrue(validate.errors(self.good, other, self.resume))


class Rule(unittest.TestCase):
    def setUp(self):
        self.resume = load_resume(RESUME_PATH)

    def check(self, posting, verdict, failed):
        v = rule.judge(posting, self.resume)
        self.assertEqual((v["verdict"], v["failed_check"]), (verdict, failed), v["justification"])
        self.assertEqual(validate.errors(v, posting, self.resume), [], "the record must cite real fields")

    def test_rule_sales_title(self):  # row 7
        self.check(constructed("Account Executive, AI Sales"), "not_relevant", "R1")

    def test_rule_senior_title(self):  # row 8, real 10-23 posting
        p = next(p for p in DAY2 if p["title"] == "Senior Software Engineer, Claims Intelligence")
        self.check(p, "not_relevant", "R2")

    def test_rule_years(self):  # row 9
        self.check(constructed("Software Engineer", desc="You have 5+ years of experience."), "not_relevant", "R2")

    def test_rule_years_range_uses_lower_bound(self):
        self.check(constructed("Software Engineer", desc="1–4 years of professional experience"), "relevant", None)

    def test_rule_outside_us(self):  # row 10
        self.check(constructed("Software Engineer", country="Brazil"), "not_relevant", "R3")
        self.check(constructed("Software Engineer", country=None), "not_relevant", "R3")

    def test_rule_sponsorship_blocker(self):  # row 11
        p = constructed("Software Engineer", desc="We are unable to sponsor visas.")
        self.check(p, "not_relevant", "R4")
        no_need = copy.deepcopy(self.resume)
        no_need["work_authorization"]["needs_sponsorship"] = False
        self.assertEqual(rule.judge(p, no_need)["verdict"], "relevant")

    def test_rule_entry_swe_relevant(self):  # row 12
        self.check(constructed("Fullstack Engineer, Ambient AI"), "relevant", None)


if __name__ == "__main__":
    unittest.main()
