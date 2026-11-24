"""CONTRACT.md "Wrong versions": each one is written out below as a plausible
but wrong implementation, and each test shows the check catches it while the
real implementation passes."""

import unittest

from agent import rule, state
from tests.fixtures import resume, variant

POSTINGS = [variant(id=30, title="Senior AI Engineer"),
            variant(id=10, title="AI Engineer"),
            variant(id=20, title="Sales Engineer", location="Paris, France")]


def pairing_errors(verdicts_by_id, postings):
    """Ids whose verdict is not about that posting."""
    by_id = {p["id"]: p for p in postings}
    return [i for i, v in verdicts_by_id.items()
            if v["posting_id"] != i or v["title"] != by_id[i]["title"]]


# Wrong version 1: verdicts computed on a sorted list, zipped back onto the
# ids in their original order.
def wrong_judge_all_misaligned(postings, resume):
    verdicts = [rule.judge(p, resume)
                for p in sorted(postings, key=lambda p: p["title"])]
    return {p["id"]: v for p, v in zip(postings, verdicts)}


# Wrong version 2: right verdict, but the "why" names nothing.
def wrong_judge_cites_nothing(posting, resume):
    v = rule.judge(posting, resume)
    v["justification"] = [{"check": "overall", "passed": True,
                           "posting_fields": [], "resume_fields": [],
                           "matched": []}]
    return v


# Wrong version 3: "new" means everything currently on the board.
def wrong_new_ids_everything(previous_state, current_ids):
    return sorted(current_ids) if previous_state else []


class TestWrongVersions(unittest.TestCase):
    def setUp(self):
        self.resume = resume()

    def test_1_real_pairing_passes(self):
        got = rule.judge_all(POSTINGS, self.resume)
        self.assertEqual(pairing_errors(got, POSTINGS), [])
        self.assertEqual(got[10]["verdict"], "relevant")
        self.assertEqual(got[30]["verdict"], "not_relevant")

    def test_1_misaligned_pairing_is_caught(self):
        got = wrong_judge_all_misaligned(POSTINGS, self.resume)
        self.assertNotEqual(pairing_errors(got, POSTINGS), [])

    def test_2_real_justifications_cite_both_sides(self):
        for p in POSTINGS:
            self.assertTrue(rule.justification_cites_fields(
                rule.judge(p, self.resume)))

    def test_2_empty_justification_is_caught(self):
        for p in POSTINGS:
            self.assertFalse(rule.justification_cites_fields(
                wrong_judge_cites_nothing(p, self.resume)))
        self.assertFalse(rule.justification_cites_fields(
            {"justification": []}))

    def _two_runs(self, new_ids):
        first = state.updated(None, "datadog", [1, 2, 3], {"stamp": "a"})
        return new_ids(first, [1, 2, 3, 4])

    def test_3_real_diff_reports_only_unseen(self):
        self.assertEqual(self._two_runs(state.new_ids), [4])

    def test_3_reporting_old_jobs_as_new_is_caught(self):
        self.assertNotEqual(self._two_runs(wrong_new_ids_everything), [4])


if __name__ == "__main__":
    unittest.main()
