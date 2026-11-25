"""Reject-audit draw (js3/reject_audit.py), written BEFORE the module.
Constructed fixtures only; no network."""
import unittest

from js3 import filter as flt
from tests.test_wrong_versions import posting


def fixture():
    ps = [posting(1000 + i, f"Ops Analyst {i}", "Spreadsheets and vendor management.") for i in range(60)]
    ps += [posting(2000 + i, f"Data Analyst {i}", "Daily Python and SQL.") for i in range(5)]       # exactly 1 word
    ps += [posting(3000, "Sales Engineer", "Python and LLM demos for customers.")]                  # passed r1, r2 fired
    ps += [posting(3001, "Sales Engineer", "Python and LLM. You will fine-tune models.")]            # r2 exception -> relevant
    ps += [posting(4000 + i, f"ML Engineer {i}", "Python, PyTorch, RAG.") for i in range(4)]          # relevant
    ps += [posting(5000, "Backend Engineer", ""), posting(5001, "Python LLM Engineer", None)]        # insufficient_data
    return flt.run_filter(ps)


class RejectAuditDraw(unittest.TestCase):
    def setUp(self):
        from js3 import reject_audit
        self.ra = reject_audit
        self.out = fixture()
        self.draw = reject_audit.draw(self.out, n_near=3)  # fixture pool has only 5 exactly-1-word postings

    def ids(self, group):
        return [r["id"] for r in self.draw[group]]

    def test_seed_is_fixed_and_documented(self):
        self.assertEqual(self.draw["seed"], self.ra.SEED)
        self.assertEqual(self.ids("random_rejected"), self.ids("random_rejected"))
        self.assertEqual(self.ids("random_rejected"), [r["id"] for r in self.ra.draw(fixture(), n_near=3)["random_rejected"]])

    def test_random_sample_is_n_drawn_only_from_the_reject_sampling_pool(self):
        pool = {r["id"] for r in flt.reject_sampling_pool(self.out)}
        self.assertEqual(len(self.ids("random_rejected")), self.ra.N_RANDOM)
        self.assertEqual(len(set(self.ids("random_rejected"))), self.ra.N_RANDOM)
        self.assertLessEqual(set(self.ids("random_rejected")), pool)

    def test_insufficient_data_never_drawn_anywhere(self):
        drawn = {i for g in ("random_rejected", "near_threshold", "relevant") for i in self.ids(g)}
        self.assertEqual(drawn & {5000, 5001}, set())

    def test_near_threshold_population_is_exactly_one_word_plus_rule2_only_rejects(self):
        self.assertEqual(sorted(r["id"] for r in self.draw["near_threshold_population"]),
                         [2000, 2001, 2002, 2003, 2004, 3000])

    def test_near_threshold_group_is_forced_rule2_only_plus_seeded_subsample(self):
        import random
        d = self.ra.draw(self.out, n_near=3)
        ids = [r["id"] for r in d["near_threshold"]]
        self.assertEqual(ids[0], 3000, "rule-2-only postings are forced includes, listed first")
        sampled = ids[1:]
        self.assertEqual(len(sampled), 3)
        exactly1 = sorted((r for r in self.out["rejected"] if len(r["matched_skills"]) == 1),
                          key=lambda r: (str(r["board"]), str(r["id"])))
        expected = [r["id"] for r in random.Random(self.ra.SEED).sample(exactly1, 3)]
        self.assertEqual(sampled, expected, "random.Random(SEED).sample over the exactly-1-word pool")
        self.assertEqual([r["id"] for r in self.ra.draw(fixture(), n_near=3)["near_threshold"]], ids)

    def test_default_near_sample_size_is_38_random_plus_forced(self):
        self.assertEqual(self.ra.N_NEAR_SAMPLE, 38)

    def test_relevant_group_is_every_relevant_posting(self):
        self.assertEqual(sorted(self.ids("relevant")), [3001, 4000, 4001, 4002, 4003])

    def test_draw_order_does_not_depend_on_input_order(self):
        rev = dict(self.out, rejected=list(reversed(self.out["rejected"])))
        self.assertEqual(self.ids("random_rejected"), [r["id"] for r in self.ra.draw(rev, n_near=3)["random_rejected"]])


if __name__ == "__main__":
    unittest.main()
