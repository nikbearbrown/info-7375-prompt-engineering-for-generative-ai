"""JS3 sampling tests on a CONSTRUCTED corpus."""

import contextlib
import csv
import io
import json
import random
import re
import tempfile
import unittest
from pathlib import Path

import js3_fixtures as fx
from js3 import corpus, run_filter, sample
from js3.filter import Filter

# Words that would leak the filter's output into a blind sheet.
LEAKS = re.compile(r"score|decision|kept|rejected|abstain|stratum|strata|"
                   r"close.call|title_engineer|title_other|R[1-4]\b",
                   re.IGNORECASE)


def constructed_draw(seed=sample.SEED):
    with tempfile.TemporaryDirectory() as tmp:
        postings = corpus.load(fx.make_corpus(tmp))["postings"]
    flt = Filter(fx.CONFIG)
    decisions = [flt.evaluate(p) for p in postings]
    return postings, decisions, sample.draw(postings, decisions, seed)


class DrawTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.postings, cls.decisions, drawn = constructed_draw()
        cls.heldout, cls.held_short, cls.audit, cls.audit_short = drawn

    def test_heldout_never_in_audit(self):
        held = {p["id"] for p in self.heldout}
        audit = {d["id"] for d in self.audit}
        self.assertEqual(held & audit, set())

    def test_heldout_is_16_plus_8_by_title(self):
        strata = [p["stratum"] for p in self.heldout]
        self.assertEqual(strata.count(sample.TITLE_STRATUM), 16)
        self.assertEqual(strata.count(sample.OTHER_STRATUM), 8)
        for p in self.heldout:
            titled = re.search(r"\b(engineer|scientist)\b", p["title"], re.I)
            self.assertEqual(bool(titled),
                             p["stratum"] == sample.TITLE_STRATUM)
        self.assertEqual(self.held_short, {})

    def test_audit_strata_sizes_and_membership(self):
        by = {}
        for d in self.audit:
            by.setdefault(d["stratum"], []).append(d)
        self.assertEqual(len(by["rejected"]), 30)
        self.assertEqual(len(by["close_call"]), 10)
        self.assertEqual(len(by["kept"]), 10)
        self.assertTrue(all(d["decision"] == "rejected"
                            for d in by["rejected"]))
        self.assertTrue(all(d["score"] in (3, 4) for d in by["close_call"]))
        self.assertTrue(all(d["decision"] == "kept" for d in by["kept"]))
        ids = [d["id"] for d in self.audit]
        self.assertEqual(len(ids), len(set(ids)))

    def test_audit_is_shuffled_not_grouped(self):
        strata = [d["stratum"] for d in self.audit]
        self.assertNotEqual(strata, sorted(strata, key=strata.index))

    def test_same_seed_same_draw(self):
        _, _, again = constructed_draw()
        self.assertEqual([p["id"] for p in again[0]],
                         [p["id"] for p in self.heldout])
        self.assertEqual([d["id"] for d in again[2]],
                         [d["id"] for d in self.audit])

    def test_other_seed_other_draw(self):
        _, _, other = constructed_draw(seed=1)
        self.assertNotEqual([d["id"] for d in other[2]],
                            [d["id"] for d in self.audit])

    def test_draw_ignores_input_order(self):
        rev = sample.draw(list(reversed(self.postings)),
                          list(reversed(self.decisions)))
        self.assertEqual([d["id"] for d in rev[2]],
                         [d["id"] for d in self.audit])

    def test_short_pool_is_recorded_not_hidden(self):
        few = [d for d in self.decisions if d["decision"] != "kept"][:40]
        few += [d for d in self.decisions if d["decision"] == "kept"][:3]
        rows, short = sample.draw_audit(few, [], random.Random(1))
        self.assertEqual(short["kept"], {"requested": 10, "available": 3})
        self.assertEqual(sum(r["stratum"] == "kept" for r in rows), 3)


class CliTests(unittest.TestCase):
    """run_filter + sample end to end on a CONSTRUCTED corpus folder."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root = fx.make_corpus(self.tmp / "root")
        self.out = self.tmp / "filter"
        self.labels = self.tmp / "labels"
        with contextlib.redirect_stdout(io.StringIO()):
            run_filter.main(["--config", str(fx.CONFIG_PATH), "--out",
                             str(self.out), "--root", str(self.root)])
            self.code = self._sample()

    def tearDown(self):
        self._tmp.cleanup()

    def _sample(self, *extra):
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            return sample.main(["--decisions",
                                str(self.out / "decisions.jsonl"),
                                "--labels", str(self.labels),
                                "--root", str(self.root), *extra])

    def test_summary_reports_unlisted_board_as_not_evaluated(self):
        summary = json.loads((self.out / "summary.json").read_text())
        self.assertEqual(summary["config_version"], "1.0")
        self.assertEqual(summary["boards"]["constructed"]["kept"], 30)
        self.assertEqual(summary["boards"]["constructed"]["rejected"], 90)
        self.assertEqual(summary["boards"]["constructed-404"]["status"],
                         "not evaluated")
        self.assertNotIn("kept", summary["boards"]["constructed-404"])
        self.assertEqual(summary["score_histogram"],
                         {"1": 60, "3": 30, "5": 30})

    def test_sheets_are_blind(self):
        self.assertEqual(self.code, 0)
        for name in ("heldout_sheet.md", "audit_sheet.md"):
            text = (self.labels / name).read_text()
            with self.subTest(sheet=name):
                self.assertIsNone(LEAKS.search(text), LEAKS.search(text))
                self.assertIn("## 1\n", text)
                self.assertIn("- url: https://example.invalid/", text)

    def test_sheet_body_cut_at_800_characters(self):
        long = {"id": 1, "title": "ML Engineer", "location": "x",
                "content": "word " * 400, "absolute_url": "u"}
        post = corpus.load(fx.make_corpus(self.tmp / "long", [long]))
        sheet = sample.render_sheet("t", "v.csv", post["postings"])
        body = sheet.split("~~~~text\n")[1].split("\n~~~~")[0]
        self.assertEqual(len(body), 800)

    def test_key_and_ids_files(self):
        key = json.loads((self.labels / "audit_key.json").read_text())
        held = json.loads((self.labels / "heldout_ids.json").read_text())
        self.assertEqual(key["seed"], 7375)
        self.assertEqual(len(key["key"]), 50)
        for entry in key["key"].values():
            self.assertLessEqual({"stratum", "decision", "score"},
                                 set(entry))
        self.assertEqual(len(held["ids"]), 24)
        self.assertEqual(set(held["ids"]) & set(key["key"]), set())

    def test_verdict_templates_are_blank(self):
        for name, n in (("heldout_verdicts.csv", 24),
                        ("audit_verdicts.csv", 50)):
            with open(self.labels / name, newline="") as handle:
                rows = list(csv.reader(handle))
            with self.subTest(file=name):
                self.assertEqual(rows[0], ["id", "verdict", "reason"])
                self.assertEqual(len(rows) - 1, n)
                self.assertTrue(all(r[1] == "" and r[2] == ""
                                    for r in rows[1:]))

    def test_rerun_refuses_and_never_overwrites_verdicts(self):
        self.assertEqual(self._sample(), 2)
        path = self.labels / "audit_verdicts.csv"
        path.write_text("id,verdict,reason\n100000,relevant,mine\n")
        self.assertEqual(self._sample("--force"), 0)
        self.assertIn("mine", path.read_text())


if __name__ == "__main__":
    unittest.main()
