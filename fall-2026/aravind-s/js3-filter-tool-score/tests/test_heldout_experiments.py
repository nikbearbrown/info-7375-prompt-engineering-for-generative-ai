"""The held-out experiment tool (tools/heldout_experiments.py): one change per run, and the agreement arithmetic.

Nothing here opens the held-out answers: the variants are compared as rule dictionaries, and the metrics run on
constructed rows.
"""

import importlib.util
import unittest

from job_agent import filter as flt

from .loop_helpers import REPO

spec = importlib.util.spec_from_file_location("heldout_experiments", REPO / "tools" / "heldout_experiments.py")
hx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hx)

RULES = flt.load_rules(version="1.0")


def differences(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += differences(a.get(k), b.get(k), f"{path}.{k}")
        return out
    return [] if a == b else [path]


class VariantsTest(unittest.TestCase):
    def test_each_change_touches_exactly_one_thing(self):
        expected = {"R0": [], "R0b": [], "X1": [".splitter_keeps"], "X2": [".years_company_words"],
                    "X3": [".topic_groups.Developer tools"], "X4": [".ranking.caution_penalty"],
                    "X5": [".ranking.shortlist_min"], "X6": [".ranking.shortlist_min"]}
        for name in hx.RUNS:
            with self.subTest(run=name):
                self.assertEqual(differences(RULES, hx.variant(RULES, name)), expected[name])

    def test_variants_never_change_the_loaded_rules(self):
        before = flt.load_rules(version="1.0")
        for name in hx.RUNS:
            hx.variant(RULES, name)
        self.assertEqual(RULES, before)

    def test_the_word_changes_are_the_planned_ones(self):
        self.assertEqual(hx.variant(RULES, "X2")["years_company_words"], ["grew", "grown", "founded", "history"])
        self.assertNotIn("build systems", hx.variant(RULES, "X3")["topic_groups"]["Developer tools"])
        self.assertEqual((hx.variant(RULES, "X5")["ranking"]["shortlist_min"],
                          hx.variant(RULES, "X6")["ranking"]["shortlist_min"]), (55, 50))


class MetricsTest(unittest.TestCase):
    def test_fate_and_cutoff_agreement_by_pool(self):
        rows = [{"pool": "random kept", "his": "Keep", "fate": "kept", "score": 55},
                {"pool": "random kept", "his": "Reject", "fate": "kept", "score": 65},
                {"pool": "random kept", "his": "?", "fate": "kept", "score": 70},
                {"pool": "random rejected", "his": "Reject", "fate": "rejected", "score": None},
                {"pool": "random rejected", "his": "Keep", "fate": "rejected", "score": None}]
        m = hx.metrics(rows, 60)
        self.assertEqual((m["kept"]["n"], m["kept"]["fate_agree"]), (2, 1))
        self.assertEqual((m["rejected"]["n"], m["rejected"]["fate_agree"]), (2, 1))
        self.assertEqual((m["all"]["n"], m["all"]["fate_disagree"]), (4, 2))
        # recommended = kept and at or above the cutoff: only the 65 (his Reject) counts at 60
        self.assertEqual((m["all"]["recommended"], m["all"]["cutoff_agree"]), (1, 1))
        self.assertEqual(hx.metrics(rows, 55)["all"]["cutoff_agree"], 2)


if __name__ == "__main__":
    unittest.main()
