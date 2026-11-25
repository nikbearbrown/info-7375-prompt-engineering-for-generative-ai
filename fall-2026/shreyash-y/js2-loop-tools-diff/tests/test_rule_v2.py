"""Review packet test, written 2026-11-09 BEFORE the rule v2 patch. It must fail on rule v1.

Real cases (tests/fixtures/js1_real_postings.json) carry the expectations Shreyash wrote in JS1:
labels/DISPUTED-POSTINGS-REVIEW.md (the five Oscar postings) and experiment-2 hand-labels.csv
(Klaviyo). Constructed cases are labeled CONSTRUCTED."""
import json
import pathlib
import unittest

from jsagent import persona, posting, rule
from tests import helpers

FX = json.loads((pathlib.Path(__file__).parent / "fixtures" / "js1_real_postings.json").read_text())
REAL = {e["job"]["id"]: posting.normalize(e["job"], e["board_token"]) for e in FX["jobs"]}
VIEW = persona.public_view(helpers.load_persona())


def failed(pid):
    return rule.judge(REAL[pid], VIEW)["failed_conditions"]


def judge(**kw):
    return rule.judge(posting.normalize(helpers.make_job(900, **kw), "constructed"), VIEW)


class RealDefects(unittest.TestCase):
    """Each line: posting, condition, Shreyash's reading."""

    def test_8083703_c5_four_years_without_the_word_experience(self):
        self.assertIn(5, failed(8083703))      # "4+ years in industry or another quantitative field"

    def test_8319419_c5_long_phrase(self):
        self.assertIn(5, failed(8319419))      # "5+ years of technical program ... work"

    def test_7783904003_c5_years_of_responsibility(self):
        self.assertEqual(failed(7783904003), [4, 5])   # hand label, experiment 2

    def test_6555819_c3_hybrid_despite_remote_tag(self):
        self.assertIn(3, failed(6555819))      # office tag Remote, ad says commute to NYC/Tempe/LA

    def test_8250366_c3_hybrid_despite_remote_new_york_tag(self):
        self.assertIn(3, failed(8250366))      # "three days per week in the NYC office"

    def test_8172223_c3_remote_states_exclude_massachusetts(self):
        self.assertIn(3, failed(8172223))      # 17 named states, no Massachusetts


class RealPositivesStayRelevant(unittest.TestCase):
    """Shreyash's four Relevant Klaviyo labels must not be lost by the fix."""

    def test_four_positives(self):
        for pid in (8041054003, 7696724003, 7855793003, 7792539003):
            self.assertEqual(rule.judge(REAL[pid], VIEW)["verdict"], "Relevant", pid)


class ConstructedEdges(unittest.TestCase):
    """CONSTRUCTED postings for the boundaries of the new reading."""

    def test_preferred_years_do_not_count(self):
        rec = judge(content="<p>Requirements: Python, SQL. 2+ years of experience. "
                            "Nice to have: 6+ years of experience with Kafka.</p>")
        self.assertNotIn(5, rec["failed_conditions"])

    def test_mandatory_years_still_count(self):
        rec = judge(content="<p>What you'll need: Python, SQL, 5+ years building services. "
                            "Bonus: 1 year of Rust.</p>")
        self.assertIn(5, rec["failed_conditions"])

    def test_company_history_years_ignored(self):
        rec = judge(content="<p>Founded 12 years ago, we grew fast. Requirements: Python, SQL, 2 years of experience.</p>")
        self.assertNotIn(5, rec["failed_conditions"])

    def test_boston_hybrid_passes(self):
        self.assertNotIn(3, judge(content="<p>Python, SQL. This is a hybrid role, 3 days a week in our Boston office.</p>")["failed_conditions"])

    def test_hybrid_word_about_methods_is_not_hybrid_work(self):
        rec = judge(location="Remote", offices=("Remote",),
                    content="<p>Python, SQL. Fully remote in the United States. We use hybrid approaches to search.</p>")
        self.assertNotIn(3, rec["failed_conditions"])

    def test_remote_state_list_with_massachusetts_passes(self):
        rec = judge(location="Remote", offices=("Remote",),
                    content="<p>Python, SQL. Open to candidates who reside in: Florida; Massachusetts; Texas.</p>")
        self.assertNotIn(3, rec["failed_conditions"])

    def test_remote_single_other_state_office_fails(self):
        self.assertIn(3, judge(location="Remote", offices=("Remote (Florida)",))["failed_conditions"])

    def test_remote_massachusetts_office_passes(self):
        self.assertNotIn(3, judge(location="Remote", offices=("Remote (Massachusetts)",))["failed_conditions"])


if __name__ == "__main__":
    unittest.main()
