"""The blind audit kit: deterministic for a seed, 45 distinct postings, no filter reasons. Reads out/."""
import csv
import tempfile
import unittest
from pathlib import Path

from tests.js3_helpers import ROOT

RESUME = ROOT / "data" / "resume.example.json"
LEAKS = ("F1 [", "F2 [", "F3 [", "F4 [", "abstain: cannot tell", "no role word", "excluded word",
         "no US part", "shipped skills named")


class AuditKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from audit import make_kit
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.sizes, cls.pools = make_kit.build(20261124, ROOT / "out", cls.out / "a", RESUME)
        make_kit.build(20261124, ROOT / "out", cls.out / "b", RESUME)
        cls.rows = list(csv.DictReader(open(cls.out / "a" / "audit.csv", encoding="utf-8-sig")))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_sizes_and_distinct_postings(self):
        self.assertEqual(self.sizes, {"reject": 30, "close": 5, "accept": 10})
        self.assertEqual(len({r["posting_id"] for r in self.rows}), 45)

    def test_same_seed_same_kit(self):
        for name in ["audit.csv"] + sorted(p.name for p in (self.out / "a" / "postings").iterdir()):
            sub = "" if name == "audit.csv" else "postings"
            a = (self.out / "a" / sub / name).read_bytes()
            self.assertEqual(a, (self.out / "b" / sub / name).read_bytes(), name)

    def test_judgment_columns_blank_and_no_reason_leaks(self):
        self.assertTrue(all(r["my_relevant"] == "" and r["my_note"] == "" for r in self.rows))
        for path in [self.out / "a" / "audit.csv"] + list((self.out / "a" / "postings").iterdir()):
            text = path.read_text(encoding="utf-8-sig")
            for leak in LEAKS:
                self.assertNotIn(leak, text, path.name)


if __name__ == "__main__":
    unittest.main()
