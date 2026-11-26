"""Filter v1.0 (FILTER.md section 2) on CONSTRUCTED postings, plus two records on the saved run of 2026-11-25."""
import unittest

from agent import collection, config, filter as filt
from agent.policy import Policy
from tests.jobs import PERSONA, SPEC, decide

RUN = config.RUNS_DIR / "20261125T204144Z"


class Gates(unittest.TestCase):
    def test_keep_when_every_gate_passes_and_score_reaches_threshold(self):
        d = decide()
        self.assertEqual((d.verdict, d.score), (filt.KEEP, 6))  # role 3 + Python, Kafka, Redis

    def test_g1_location_without_a_us_word_is_rejected(self):
        d = decide(location="London, UK")
        self.assertEqual(d.verdict, filt.REJECT)
        self.assertFalse(d.gates["G1 location"]["passed"])

    def test_g1_city_and_state_alone_is_rejected_in_v1_0(self):
        # Figma writes some US locations without a country; v1.0 rejects them (the audit measures this).
        self.assertEqual(decide(location="San Francisco, CA • New York, NY").verdict, filt.REJECT)

    def test_g2_seniority_word_in_title(self):
        for title in ("Senior Software Engineer", "Sr. Backend Engineer", "Software Engineer Intern", "Staff Cloud Engineer"):
            self.assertEqual(decide(title=title).verdict, filt.REJECT, title)

    def test_g3_years_range_counts_its_lowest_number(self):
        self.assertEqual(decide(content="<p>3-5 years of Python, Kafka</p>").verdict, filt.REJECT)
        self.assertEqual(decide(content="<p>2-4 years of Python, Kafka</p>").verdict, filt.KEEP)
        self.assertEqual(decide(content="<p>2+ years of Python, Kafka</p>").verdict, filt.KEEP)


class Score(unittest.TestCase):
    def test_one_below_threshold_is_a_rejected_close_call(self):
        d = decide(content="<p>Python only</p>")
        self.assertEqual((d.verdict, d.score, d.close_call), (filt.REJECT, 4, True))

    def test_exactly_threshold_is_a_kept_close_call(self):
        d = decide(content="<p>Python and Redis</p>")
        self.assertEqual((d.verdict, d.score, d.close_call), (filt.KEEP, 5, True))

    def test_plain_engineer_title_gets_one_point(self):
        self.assertEqual(decide(title="Data Engineer", content="<p>Python, SQL, AWS, Docker</p>").score, 5)
        self.assertEqual(decide(title="Data Engineer", content="<p>Python, SQL, AWS</p>").verdict, filt.REJECT)

    def test_no_engineer_or_developer_gets_no_role_points(self):
        self.assertEqual(decide(title="Product Manager, Backend", location="Remote, US").parts["S1 role"]["points"], 0)

    def test_skill_points_are_capped(self):
        d = decide(content="<p>Python Java SQL Kafka Redis AWS Docker Kubernetes</p>")
        self.assertEqual(d.parts["S2 skills"]["points"], SPEC["skill_cap"])

    def test_whole_words_only(self):
        d = decide(content="<p>JavaScript, PostgreSQL, maintain, focus</p>")
        self.assertEqual(d.parts["S2 skills"]["skills"], ["PostgreSQL"])


class Missing(unittest.TestCase):
    def test_no_description_is_cannot_tell(self):
        d = decide(content="")
        self.assertEqual((d.verdict, d.missing), (filt.CANNOT_TELL, ["description"]))

    def test_no_location_is_cannot_tell(self):
        self.assertEqual(decide(location="").verdict, filt.CANNOT_TELL)

    def test_filter_file_missing_a_key_is_refused(self):
        import json, tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"version": "x"}, f)
        try:
            with self.assertRaises(ValueError):
                filt.load_filter(f.name)
        finally:
            os.unlink(f.name)


class SavedRun(unittest.TestCase):
    """Records on the real run saved on 2026-11-25 (read from disk; no request is made)."""

    def test_failed_board_gives_no_postings_and_is_listed_as_failed(self):
        postings, failed = collection.load_run(RUN, Policy())
        self.assertEqual([b for b, _ in failed], ["lever:no-such-board"])
        self.assertNotIn("lever:no-such-board", {b for b, _ in postings})

    def test_v1_0_counts_on_the_saved_run(self):
        postings, _ = collection.load_run(RUN, Policy())
        decisions = filt.decide_all(postings, PERSONA, SPEC)
        counts = {v: sum(d.verdict == v for d in decisions) for v in (filt.KEEP, filt.REJECT, filt.CANNOT_TELL)}
        self.assertEqual(counts, {filt.KEEP: 7, filt.REJECT: 582, filt.CANNOT_TELL: 0})


if __name__ == "__main__":
    unittest.main()
