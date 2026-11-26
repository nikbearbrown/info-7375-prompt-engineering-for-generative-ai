"""js3.batch_label on a CONSTRUCTED labels folder (no real postings)."""

import contextlib
import copy
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from js3 import batch_label as bl
from js3 import sample

POSTINGS = [
    {"board": "constructed", "id": f"id{i}", "title": f"Role {i} ",
     "location": "Nowhere", "url": f"https://example.invalid/{i}",
     "body_text": f"Body of posting {i} builds pipelines."}
    for i in range(1, 25)
]


def suggestion(p, row):
    return {"row": row, "batch": bl.batch_of(row), "id": p["id"],
            "board": p["board"], "title": p["title"].strip(),
            "verdict": "not", "confidence": "high",
            "reason": f"constructed reason {row}",
            "justification": f"Constructed justification number {row} "
                             f"with distinct wording {'x' * row}.",
            "evidence": [f"posting {row} builds"],
            "uncertainty": "none", "borderline": False,
            "borderline_note": ""}


class BatchLabelTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.labels = Path(self._tmp.name)
        (self.labels / "heldout_sheet.md").write_text(
            sample.render_sheet("t", "v.csv", POSTINGS), "utf-8")
        sample.write_verdict_template(self.labels / "heldout_verdicts.csv",
                                      [p["id"] for p in POSTINGS])
        (self.labels / bl.RUBRIC).write_text("rubric v1\n", "utf-8")
        (self.labels / "suggestions").mkdir()
        self.rubric_sha = bl.sha256_file(self.labels / bl.RUBRIC)
        self.sugg = [suggestion(p, n) for n, p in enumerate(POSTINGS, 1)]
        self.write_batches(self.sugg)

    def tearDown(self):
        self._tmp.cleanup()

    def write_batches(self, suggestions, rubric_sha=None):
        for old in (self.labels / "suggestions").glob("*.json"):
            old.unlink()
        for batch in sorted({s["batch"] for s in suggestions}):
            (self.labels / "suggestions" /
             f"heldout_batch_{batch:02d}.json").write_text(json.dumps({
                 "dataset": "heldout", "batch": batch,
                 "rubric_sha256": rubric_sha or self.rubric_sha,
                 "labeler": "test", "human_reviewed": False,
                 "suggestions": [s for s in suggestions
                                 if s["batch"] == batch]}), "utf-8")

    def errors(self):
        p = bl.paths(self.labels, "heldout")
        return bl.validate("heldout", bl.parse_sheet(p["sheet"]),
                           bl.load_suggestions(p, "heldout"),
                           self.rubric_sha)[0]

    def run_cli(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(io.StringIO()) as err:
            code = bl.main(["--labels", str(self.labels), *argv])
        return code, out.getvalue() + err.getvalue()

    def csv_rows(self):
        with open(self.labels / "heldout_verdicts.csv", newline="") as fh:
            return list(csv.DictReader(fh))

    def test_sheet_round_trip(self):
        rows = bl.parse_sheet(self.labels / "heldout_sheet.md")
        self.assertEqual([r["id"] for r in rows],
                         [p["id"] for p in POSTINGS])
        self.assertEqual(rows[0]["body"], POSTINGS[0]["body_text"])

    def test_valid_suggestions_pass(self):
        self.assertEqual(self.errors(), [])

    def test_evidence_must_be_verbatim_in_that_posting(self):
        self.sugg[0]["evidence"] = ["posting 2 builds"]
        self.write_batches(self.sugg)
        self.assertTrue(any("not found verbatim" in e for e in self.errors()))

    def test_missing_and_duplicate_ids(self):
        dup = copy.deepcopy(self.sugg[1])
        dup.update(row=1, batch=1)
        self.write_batches([dup] + self.sugg[1:])
        errs = self.errors()
        self.assertTrue(any("id1: no suggestion" in e for e in errs))
        self.assertTrue(any("2 suggestions" in e for e in errs))

    def test_reason_with_comma_and_bad_verdict(self):
        self.sugg[0]["reason"] = "sales, not engineering"
        self.sugg[1]["verdict"] = "maybe"
        self.write_batches(self.sugg)
        errs = self.errors()
        self.assertTrue(any("without commas" in e for e in errs))
        self.assertTrue(any("verdict 'maybe'" in e for e in errs))

    def test_unsure_must_be_borderline(self):
        self.sugg[0]["verdict"] = "unsure"
        self.write_batches(self.sugg)
        self.assertTrue(any("must be borderline" in e for e in self.errors()))

    def test_changed_rubric_is_refused(self):
        (self.labels / bl.RUBRIC).write_text("rubric v1 edited\n", "utf-8")
        code, out = self.run_cli("assemble", "--dataset", "heldout")
        self.assertEqual(code, 1)
        self.assertIn("criteria changed after labeling", out)

    def test_assemble_writes_schema_and_is_idempotent(self):
        self.assertEqual(self.run_cli("assemble", "--dataset", "heldout")[0],
                         0)
        rows = self.csv_rows()
        self.assertEqual(list(rows[0]), ["id", "verdict", "reason"])
        self.assertEqual([r["id"] for r in rows],
                         [p["id"] for p in POSTINGS])
        self.assertEqual(self.run_cli("assemble", "--dataset", "heldout")[0],
                         0)
        review = (self.labels / "suggestions"
                  / "heldout_review.md").read_text()
        self.assertIn("NOT REVIEWED BY A HUMAN", review)

    def test_human_edit_is_never_overwritten_without_approval(self):
        self.run_cli("assemble", "--dataset", "heldout")
        rows = self.csv_rows()
        rows[3]["verdict"], rows[3]["reason"] = "relevant", "my call"
        with open(self.labels / "heldout_verdicts.csv", "w",
                  newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=bl.COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        code, out = self.run_cli("assemble", "--dataset", "heldout")
        self.assertEqual(code, 1)
        self.assertIn("Not overwritten", out)
        self.assertEqual(self.csv_rows()[3]["verdict"], "relevant")
        lines, _ = bl.check_dataset(self.labels, "heldout")
        self.assertIn("(changed by a human): 1 ['id4']", "\n".join(lines))

    def test_check_reports_blank_verdicts(self):
        lines, nerr = bl.check_dataset(self.labels, "heldout")
        self.assertGreater(nerr, 0)
        self.assertIn("24 blank verdict(s)", "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
