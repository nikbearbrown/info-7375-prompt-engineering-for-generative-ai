"""Tests for TEST-EXPECTATIONS.md rows 1-13. Postings built inline are CONSTRUCTED; the rest are real snapshots."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from earlybird import Refused, claude_judge, fetch, rule, validate  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402
from earlybird.watch import watch  # noqa: E402
import wrong_versions  # noqa: E402

RESUME_PATH = ROOT / "data/resume/rohan-desai.example.json"
DAY1 = json.loads((ROOT / "data/raw/2026-10-14/ashby_commure.json").read_text(encoding="utf-8"))["jobs"]
DAY2 = json.loads((ROOT / "data/raw/2026-10-23/ashby_commure.json").read_text(encoding="utf-8"))["jobs"]
EXPECTED_NEW = {p["id"] for p in DAY2} - {p["id"] for p in DAY1}


def constructed(title, country="USA", desc="Build web services."):
    """A CONSTRUCTED posting for rule tests; not from any board."""
    return {"id": "constructed-" + title.lower().replace(" ", "-"), "title": title,
            "address": {"postalAddress": {"addressCountry": country}}, "descriptionPlain": desc}


class Watch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / "seen.json"

    def tearDown(self):
        self.tmp.cleanup()

    def run_two_days(self, fn):
        first = fn(DAY1, self.state, "commure", "2026-10-14", "t1")
        second = fn(DAY2, self.state, "commure", "2026-10-23", "t2")
        return first, second

    # row 1
    def test_baseline_reports_zero_new(self):
        self.assertEqual(watch(DAY1, self.state, "commure", "2026-10-14", "t1"), [])
        self.assertEqual(len(json.loads(self.state.read_text())["seen"]), len({p["id"] for p in DAY1}))

    # row 2
    def test_state_is_saved_and_repeat_run_is_zero(self):
        watch(DAY1, self.state, "commure", "2026-10-14", "t1")
        self.assertEqual(watch(DAY1, self.state, "commure", "2026-10-14", "t2"), [])

    # row 3
    def test_second_run_reports_only_new_ids(self):
        _, second = self.run_two_days(watch)
        self.assertEqual({p["id"] for p in second}, EXPECTED_NEW)
        self.assertEqual(len(EXPECTED_NEW), 12)

    def test_tests_catch_wrong_version_1(self):
        first, _ = self.run_two_days(wrong_versions.watch_baseline_reports_all)
        self.assertNotEqual(first, [], "wrong version 1 should report a non-empty baseline")

    def test_tests_catch_wrong_version_2(self):
        wrong_versions.watch_never_saves(DAY1, self.state, "commure", "2026-10-14", "t1")
        self.assertFalse(self.state.exists(), "wrong version 2 never writes state")
        # with no state the next run is a baseline again, so the 12 real new postings are lost
        second = wrong_versions.watch_never_saves(DAY2, self.state, "commure", "2026-10-23", "t2")
        self.assertNotEqual({p["id"] for p in second}, EXPECTED_NEW)


class Refusals(unittest.TestCase):
    # row 4
    def test_off_allowlist_host_refused(self):
        called = []
        with self.assertRaises(Refused):
            fetch.fetch("https://boards-api.greenhouse.io/v1/boards/stripe/jobs", opener=lambda *a, **k: called.append(1))
        self.assertEqual(called, [], "nothing may be fetched")

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

    # row 5
    def test_validator_rejects_prose_and_fences(self):
        for text in ["Relevant!", "```json\n" + json.dumps(self.good) + "\n```", json.dumps(self.good) + " Hope this helps"]:
            v, errs = claude_judge.parse_and_validate(text, self.posting, self.resume)
            self.assertIsNone(v)
            self.assertTrue(errs)

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

    def test_claude_judgment_is_labeled_and_rejected_output_hidden(self):
        bad = claude_judge.judge(self.posting, self.resume, "{{POSTING}}", ask=lambda p, m: ("relevant", {"model": "fake"}))
        self.assertEqual((bad["kind"], bad["valid"], bad["verdict"]), ("judgment", False, None))
        ok = claude_judge.judge(self.posting, self.resume, "{{POSTING}}",
                                ask=lambda p, m: (json.dumps(self.good), {"model": "fake"}))
        self.assertEqual((ok["kind"], ok["valid"], ok["verdict"]), ("judgment", True, "not_relevant"))


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
