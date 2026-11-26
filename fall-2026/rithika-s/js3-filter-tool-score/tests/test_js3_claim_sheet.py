"""js3.claim_sheet on a CONSTRUCTED corpus with fake Claude outputs."""

import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from js3 import claim_sheet as cs
from js3 import corpus as js3_corpus
from js3 import shortlist as sl
from tests.shortlist_fixtures import DECISIONS, make_root
from tests.test_js3_shortlist import FakeRunner, jobs

GOOD = json.dumps({"claims": [
    {"claim": "Uses PyTorch", "quote": "pytorch, spark"},
    {"claim": "Builds LLM systems", "quote": "LLM"},
    {"claim": "Sponsors visas", "quote": "NOT STATED"},
    {"claim": "Remote role", "quote": "fully remote"}]})


class ClaimSheetTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_root(Path(self._tmp.name) / "project", jobs=jobs())
        self.out = self.root / "out" / "shortlist"
        self.labels = self.root / "labels"
        self.labels.mkdir()
        self.postings = {(p["board"], str(p["id"])): p for p in
                         js3_corpus.load(self.root)["postings"]}

    def tearDown(self):
        self._tmp.cleanup()

    def shortlist(self, runner, top=2):
        sl.build(self.root, self.root / DECISIONS, top, self.out, True,
                 runner, log=lambda *a: None)

    def test_sheet_and_blank_labels(self):
        # rank 1 = id 1 gets valid JSON; rank 2 = id 3 gets a parse error
        replies = iter([(GOOD, "", 0), ("Sure! " + GOOD, "", 0)])
        self.shortlist(lambda prompt: next(replies), top=2)
        sheet, csv_path, n = cs.write(self.out, self.labels, self.postings)
        self.assertEqual(n, 4)
        with open(csv_path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(list(rows[0]), cs.COLUMNS)
        self.assertEqual([(r["posting"], r["claim_no"]) for r in rows],
                         [("constructed__1", str(i)) for i in range(1, 5)])
        self.assertTrue(all(r["label"] == "" and r["note"] == ""
                            for r in rows))
        text = sheet.read_text()
        self.assertIn("quote_found", text)
        self.assertIn("not_stated", text)
        self.assertIn("quote_not_found", text)
        self.assertIn("**candidate**", text)
        self.assertIn("**I cannot tell**", text)
        self.assertNotIn("**supported**", text)
        self.assertIn("parse error: not JSON-only output", text)
        self.assertIn("Sure! ", text)  # raw output kept
        self.assertIn("PyTorch, Spark, MLOps.", text)  # context

    def test_refuses_to_overwrite(self):
        self.shortlist(FakeRunner(stdout=GOOD))
        _, csv_path, _ = cs.write(self.out, self.labels, self.postings)
        csv_path.write_text(csv_path.read_text().replace(
            "constructed__1,1,,", "constructed__1,1,supported,mine"))
        before = csv_path.read_text()
        with self.assertRaises(cs.SheetError):
            cs.write(self.out, self.labels, self.postings)
        self.assertEqual(csv_path.read_text(), before)
        with contextlib.redirect_stderr(io.StringIO()) as err:
            code = cs.main(["--root", str(self.root), "--shortlist",
                            str(self.out), "--labels", str(self.labels)])
        self.assertIn("refusing to overwrite", err.getvalue())
        self.assertEqual(code, 1)

    def test_no_parsed_claims_writes_nothing(self):
        self.shortlist(FakeRunner(stdout="no json"))
        with self.assertRaises(cs.SheetError):
            cs.write(self.out, self.labels, self.postings)
        self.assertEqual(list(self.labels.iterdir()), [])

    def test_prompt_hash_mismatch_is_flagged(self):
        self.shortlist(FakeRunner(stdout=GOOD), top=1)
        raw_path = self.out / "claude_raw" / "constructed__1.json"
        record = json.loads(raw_path.read_text())
        record["prompt_sha256"] = "0" * 64
        raw_path.write_text(json.dumps(record))
        sheet, _, _ = cs.write(self.out, self.labels, self.postings)
        self.assertIn("warning: prompt_sha256", sheet.read_text())


if __name__ == "__main__":
    unittest.main()
