"""Draws and hand-judgment sheets: repeatable, H and D disjoint, verdict lines parsed exactly, never overwritten."""
import json
import unittest

from helpers import HERE  # noqa: F401
from jsa3 import sheets, stats

CFG = json.loads((HERE / "config/filter.json").read_text())
SEEDS = json.loads((HERE / "config/seeds.json").read_text())


def recs():
    out = []
    for i in range(200):
        v = "keep" if i % 10 == 0 else "reject"
        close = v == "reject" and i % 7 == 0
        out.append({"board": "b", "id": str(i), "verdict": v, "score": 2 if close else 0, "exclude_match": None,
                    "location_status": "pass", "role_match": None})
    return out


class Draw(unittest.TestCase):
    def test_repeatable_and_disjoint(self):
        a = sheets.draw(recs(), CFG, SEEDS["seeds"], SEEDS["sizes"])
        b = sheets.draw(recs(), CFG, SEEDS["seeds"], SEEDS["sizes"])
        self.assertEqual([r["id"] for r in a["H"]], [r["id"] for r in b["H"]])
        h = {r["id"] for r in a["H"]}
        d = [r["id"] for part in a["D"].values() for r in part]
        self.assertFalse(h & set(d))
        self.assertEqual(len(d), len(set(d)))
        self.assertEqual(len(a["H"]), 30)
        self.assertEqual(len(a["D"]["random-rejects"]), 30)


class Verdicts(unittest.TestCase):
    def test_read_back(self):
        md = ("### R01 · b · 1\n\n**My verdict:** keep\n**Why (one line):** fits\n\n"
              "### R02 · b · 2\n\n**My verdict:** \n**Why (one line):** \n\n"
              "### R03 · b · 3\n\n**My verdict:** maybe\n")
        v = sheets.read_verdicts(md)
        self.assertEqual(v[("b", "1")]["verdict"], "keep")
        self.assertIsNone(v[("b", "2")]["verdict"])
        self.assertEqual(v[("b", "3")]["verdict"], "INVALID:maybe")

    def test_blind_block_hides_the_filter(self):
        r = {"board": "b", "id": "1", "title": "T", "location": "L", "url": "u", "filter_version": "0.1", "verdict": "reject",
             "reason": "SECRET-REASON", "score": 2, "role_match": None, "exclude_match": None, "location_status": "pass",
             "location_piece": "L", "topic_hits": []}
        self.assertNotIn("SECRET-REASON", sheets.block("H01", r, {"text": "x"}, blind=True))
        self.assertIn("SECRET-REASON", sheets.block("R01", r, {"text": "x"}, blind=False))


class Bounds(unittest.TestCase):
    def test_zero_of_thirty(self):
        self.assertAlmostEqual(stats.upper_one_sided(0, 30), 1 - 0.05 ** (1 / 30), places=6)
        self.assertAlmostEqual(stats.upper_one_sided(0, 30), 0.0950, places=3)

    def test_two_sided_contains_the_estimate(self):
        lo, hi = stats.two_sided(3, 30)
        self.assertTrue(lo < 0.1 < hi)


class CreateOnly(unittest.TestCase):
    def test_sheet_is_never_overwritten_and_stays_in_its_roots(self):
        from jsa import policy
        from jsa3 import cli
        with self.assertRaises(policy.PolicyError):
            cli.create_sheet("FILTER.md", "x")          # outside labels/ audit/ shortlist/
        with self.assertRaises(policy.PolicyError):
            cli.create_sheet("labels/../FILTER.md", "x")


if __name__ == "__main__":
    unittest.main()
