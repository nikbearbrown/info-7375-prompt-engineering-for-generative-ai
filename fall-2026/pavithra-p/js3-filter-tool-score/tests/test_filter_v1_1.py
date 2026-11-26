"""Each v1.1 change (FILTER.md section 7) on CONSTRUCTED postings, with v1.0 as the contrast, plus the saved-run record."""
import unittest

from agent import collection, config, filter as filt
from agent.policy import Policy
from tests.jobs import PERSONA, job

V10 = filt.load_filter(config.ROOT / "filters" / "v1.0.json")
V11 = filt.load_filter(config.ROOT / "filters" / "v1.1.json")


def verdict(spec, **kw):
    return filt.decide(job(**kw), "constructed:board", PERSONA, spec)


class Changes(unittest.TestCase):
    def test_a_role_plus_one_skill_is_kept_in_v1_1_only(self):
        self.assertEqual(verdict(V10, content="<p>Python only</p>").verdict, filt.REJECT)
        self.assertEqual(verdict(V11, content="<p>Python only</p>").verdict, filt.KEEP)

    def test_b_four_years_passes_in_v1_1_five_does_not(self):
        self.assertEqual(verdict(V10, content="<p>4+ years of Python and Kafka</p>").verdict, filt.REJECT)
        self.assertEqual(verdict(V11, content="<p>4+ years of Python and Kafka</p>").verdict, filt.KEEP)
        self.assertEqual(verdict(V11, content="<p>5+ years of Python and Kafka</p>").verdict, filt.REJECT)

    def test_c_us_city_behind_a_non_us_country_tag(self):
        loc = "Toronto; New York, NY (CA)"  # the Lever shape found in the audit
        self.assertFalse(verdict(V10, location=loc).gates["G1 location"]["passed"])
        self.assertTrue(verdict(V11, location=loc).gates["G1 location"]["passed"])
        self.assertFalse(verdict(V11, location="Toronto (CA)").gates["G1 location"]["passed"])

    def test_d_helm_the_benchmark_is_not_the_skill(self):
        bench = "<p>Python. Built eval frameworks (lm-evaluation-harness, HELM or similar)</p>"
        self.assertIn("Helm", verdict(V10, content=bench).parts["S2 skills"]["skills"])
        self.assertNotIn("Helm", verdict(V11, content=bench).parts["S2 skills"]["skills"])
        self.assertIn("Helm", verdict(V11, content="<p>Python, Kubernetes and Helm charts</p>").parts["S2 skills"]["skills"])

    def test_e_senior_asked_in_the_text(self):
        text = "<p>We're looking for a Senior Backend Engineer. Python and Kafka.</p>"
        self.assertEqual(verdict(V10, content=text).verdict, filt.KEEP)
        d = verdict(V11, content=text)
        self.assertEqual(d.verdict, filt.REJECT)
        self.assertFalse(d.gates["G4 senior in text"]["passed"])

    def test_g_was_rejected_intern_and_staff_still_fail(self):
        for title in ("Software Engineer Intern", "Staff Software Engineer"):
            self.assertEqual(verdict(V11, title=title).verdict, filt.REJECT, title)

    def test_v1_1_counts_on_the_saved_run(self):
        postings, _ = collection.load_run(config.RUNS_DIR / "20261125T204144Z", Policy())
        kept = sum(filt.decide(j, b, PERSONA, V11).verdict == filt.KEEP for b, j in postings)
        self.assertEqual(kept, 15)


class SavedPostings(unittest.TestCase):
    """The same changes on the real postings that led to them (run 20261125T204144Z, read from disk, no request)."""

    @classmethod
    def setUpClass(cls):
        postings, _ = collection.load_run(config.RUNS_DIR / "20261125T204144Z", Policy())
        cls.jobs = {f"{b}:{j['id']}": (b, j) for b, j in postings}

    def decide(self, key, spec):
        board, j = self.jobs[key]
        return filt.decide(j, board, PERSONA, spec)

    def test_c_the_real_toronto_and_new_york_posting(self):
        key = "lever:spotify:1ee5dcb7-a5fe-465b-91da-d42ebab374c8"  # "Toronto; New York, NY (CA)"
        self.assertFalse(self.decide(key, V10).gates["G1 location"]["passed"])
        self.assertTrue(self.decide(key, V11).gates["G1 location"]["passed"])

    def test_d_the_real_helm_posting(self):
        key = "ashby:ramp:d8925f84-562f-470c-a5bd-4f6c20009361"  # "lm-evaluation-harness, HELM or similar"
        self.assertIn("Helm", self.decide(key, V10).parts["S2 skills"]["skills"])
        self.assertNotIn("Helm", self.decide(key, V11).parts["S2 skills"]["skills"])

    def test_e_the_real_backend_postings_that_ask_for_a_senior_engineer(self):
        for key in ("ashby:ramp:c0a71032-1efb-40dc-b1e8-aa0f30cd5961", "ashby:ramp:47a75895-24af-49b7-9858-1be0ec0e7c71"):
            self.assertFalse(self.decide(key, V11).gates["G4 senior in text"]["passed"], key)


class KnownLimits(unittest.TestCase):
    """FILTER.md section 8: two known limits of the word rules, recorded as they are (CONSTRUCTED postings).
    If a later version fixes them, these tests fail on purpose and FILTER.md must be updated."""

    def test_company_age_is_read_as_years_asked(self):
        d = verdict(V11, content="<p>Our company has been operating for 10 years. Python and Kafka.</p>")
        self.assertFalse(d.gates["G3 years"]["passed"])

    def test_working_alongside_senior_engineers_is_read_as_a_senior_role(self):
        d = verdict(V11, content="<p>You will work alongside senior software engineers. Python and Kafka.</p>")
        self.assertFalse(d.gates["G4 senior in text"]["passed"])


if __name__ == "__main__":
    unittest.main()
