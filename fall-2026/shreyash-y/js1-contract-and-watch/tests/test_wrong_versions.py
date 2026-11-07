"""CONTRACT.md section 6: the tests that must catch the two wrong versions (plus the
id-pairing and baseline checks named under 'Additional tests')."""
import unittest

from jsagent import rule, watch, posting
from tests import helpers, wrong_versions


class WrongVersion1TitleDedup(unittest.TestCase):
    """Two Software Engineer postings, different ids, Boston and New York."""

    def setUp(self):
        self.resume = helpers.load_persona()
        self.boston = helpers.make_job(101, title="Software Engineer")
        self.nyc = helpers.make_job(102, title="Software Engineer",
                                    location="New York, New York, United States",
                                    offices=("New York, NY",))

    def run_two(self):
        state = {}
        watch.process("testboard", helpers.board_payload([]), state, self.resume,
                      run_at="2026-10-28T00:00:00Z", source="constructed")
        report = watch.process("testboard", helpers.board_payload([self.boston, self.nyc]),
                               state, self.resume, run_at="2026-10-29T00:00:00Z",
                               source="constructed")
        return report

    def test_both_postings_reported_separately(self):
        report = self.run_two()
        self.assertEqual(sorted(r["posting_id"] for r in report["new"]), [101, 102])

    def test_verdicts_evaluated_independently(self):
        by_id = {r["posting_id"]: r for r in self.run_two()["new"]}
        self.assertEqual(by_id[101]["verdict"], "Relevant")
        self.assertEqual(by_id[102]["verdict"], "Not Relevant")
        self.assertIn(3, by_id[102]["failed_conditions"])

    def test_check_catches_wrong_version_1(self):
        # Same check, pointed at the wrong implementation: it must fail.
        out = wrong_versions.wrong_v1_new_postings_dedup_by_title([], [self.boston, self.nyc])
        self.assertNotEqual(sorted(j["id"] for j in out), [101, 102])

    def test_new_city_for_old_title_is_new(self):
        state = {}
        watch.process("testboard", helpers.board_payload([self.nyc]), state, self.resume,
                      run_at="2026-10-28T00:00:00Z", source="constructed")
        report = watch.process("testboard", helpers.board_payload([self.nyc, self.boston]),
                               state, self.resume, run_at="2026-10-29T00:00:00Z",
                               source="constructed")
        self.assertEqual([r["posting_id"] for r in report["new"]], [101])
        wrong = wrong_versions.wrong_v1_new_postings_dedup_by_title(
            [self.nyc["title"]], [self.nyc, self.boston])
        self.assertEqual(wrong, [], "the wrong version misses the Boston posting")


class WrongVersion2GenericJustification(unittest.TestCase):

    def setUp(self):
        self.resume = helpers.load_persona()
        self.jobs = [
            helpers.make_job(201),
            helpers.make_job(202, title="Actuarial Analyst", department="Actuarial"),
            helpers.make_job(203, title="Staff Software Engineer"),
            helpers.make_job(204, location="Remote", offices=("Remote (Florida)",),
                             content="<p>Python, SQL. Remote in the United States. "
                                     "6+ years of experience.</p>"),
        ]

    def test_every_line_cites_resume_and_posting_fields(self):
        for job in self.jobs:
            rec = rule.judge(posting.normalize(job, "testboard"), self.resume)
            self.assertTrue(helpers.justification_ok(rec), rec["justification"])

    def test_relevant_verdict_cites_all_six_conditions(self):
        rec = rule.judge(posting.normalize(self.jobs[0], "testboard"), self.resume)
        self.assertEqual(rec["verdict"], "Relevant")
        for n in range(1, 7):
            self.assertIn(f"C{n} ", rec["justification"])

    def test_not_relevant_names_failed_conditions_first(self):
        rec = rule.judge(posting.normalize(self.jobs[1], "testboard"), self.resume)
        first = rec["justification"].splitlines()[0]
        self.assertTrue(first.startswith("C1 FAIL") or first.startswith("C2 FAIL"), first)

    def test_check_catches_wrong_version_2(self):
        rec = wrong_versions.wrong_v2_generic_judge(
            posting.normalize(self.jobs[0], "testboard"), self.resume)
        self.assertFalse(helpers.justification_ok(rec))


class AdditionalChecks(unittest.TestCase):

    def setUp(self):
        self.resume = helpers.load_persona()

    def test_verdicts_stay_on_their_ids_in_any_order(self):
        jobs = [helpers.make_job(301),
                helpers.make_job(302, title="Claims Specialist", department="Insurance Operations"),
                helpers.make_job(303, title="ML Engineer", location="Remote",
                                 offices=("Remote",),
                                 content="<p>PyTorch and Python, US remote. 1 year of experience.</p>")]
        expected = {301: "Relevant", 302: "Not Relevant", 303: "Relevant"}
        for order in ([0, 1, 2], [2, 1, 0], [1, 2, 0]):
            state = {}
            watch.process("testboard", helpers.board_payload([]), state, self.resume,
                          run_at="2026-10-28T00:00:00Z", source="constructed")
            report = watch.process("testboard", helpers.board_payload([jobs[i] for i in order]),
                                   state, self.resume, run_at="2026-10-29T00:00:00Z",
                                   source="constructed")
            got = {r["posting_id"]: r["verdict"] for r in report["new"]}
            self.assertEqual(got, expected)
            for r in report["new"]:
                self.assertIn(f"posting.id={r['posting_id']}", r["justification"])
            shifted = {r["posting_id"]: r["verdict"]
                       for r in wrong_versions.wrong_v3_labels_shifted(report["new"])}
            self.assertNotEqual(shifted, expected, "the shifted-label wrong version is caught")

    def test_first_run_is_baseline_with_zero_new(self):
        state = {}
        jobs = [helpers.make_job(i) for i in (401, 402, 403)]
        report = watch.process("testboard", helpers.board_payload(jobs), state, self.resume,
                               run_at="2026-10-28T00:00:00Z", source="constructed")
        self.assertTrue(report["baseline"])
        self.assertEqual(report["new"], [])
        self.assertEqual(report["fetched"], 3)
        self.assertEqual(sorted(state["boards"]["testboard"]["seen_ids"]), [401, 402, 403])

    def test_second_run_reports_only_unseen(self):
        state = {}
        jobs = [helpers.make_job(i) for i in (401, 402)]
        watch.process("testboard", helpers.board_payload(jobs), state, self.resume,
                      run_at="2026-10-28T00:00:00Z", source="constructed")
        report = watch.process("testboard", helpers.board_payload(jobs + [helpers.make_job(499)]),
                               state, self.resume, run_at="2026-10-29T00:00:00Z",
                               source="constructed")
        self.assertFalse(report["baseline"])
        self.assertEqual([r["posting_id"] for r in report["new"]], [499])
        self.assertTrue(all(r["is_new"] for r in report["new"]))

    def test_vanished_then_back_is_not_new(self):
        state = {}
        a, b = helpers.make_job(501), helpers.make_job(502)
        for day, jobs in (("28", [a, b]), ("29", [a]), ("30", [a, b])):
            report = watch.process("testboard", helpers.board_payload(jobs), state, self.resume,
                                   run_at=f"2026-10-{day}T00:00:00Z", source="constructed")
        self.assertEqual(report["new"], [])

    def test_boards_are_kept_apart(self):
        state = {}
        watch.process("board_a", helpers.board_payload([helpers.make_job(601)]), state,
                      self.resume, run_at="2026-10-28T00:00:00Z", source="constructed")
        report = watch.process("board_b", helpers.board_payload([helpers.make_job(601)]), state,
                               self.resume, run_at="2026-10-28T00:00:00Z", source="constructed")
        self.assertTrue(report["baseline"], "a second board starts with its own baseline")


if __name__ == "__main__":
    unittest.main()
