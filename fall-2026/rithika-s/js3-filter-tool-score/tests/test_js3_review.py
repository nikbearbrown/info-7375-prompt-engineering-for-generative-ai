"""js3.review on a CONSTRUCTED labels folder (no real postings or labels)."""

import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from js3 import batch_label as bl
from js3 import review, sample

TITLES = ["Applied AI Engineer, Customers", "Software Engineer, Training",
          "Account Executive", "Forward Deployed Engineer"]


def make_labels(folder):
    """Write sheets, blank CSVs, rubric and batch files for both sets."""
    folder = Path(folder)
    (folder / "suggestions").mkdir()
    (folder / bl.RUBRIC).write_text("rubric\n", "utf-8")
    sha = bl.sha256_file(folder / bl.RUBRIC)
    for dataset, n in bl.DATASETS.items():
        posts = [{"board": "constructed", "id": f"{dataset}{i}",
                  "title": TITLES[i % 4], "location": "Nowhere",
                  "url": "https://example.invalid",
                  "body_text": f"Posting {dataset} {i} body."}
                 for i in range(1, n + 1)]
        (folder / f"{dataset}_sheet.md").write_text(
            sample.render_sheet("t", "v.csv", posts), "utf-8")
        sugg = []
        for row, p in enumerate(posts, 1):
            border = row % 4 == 0
            sugg.append({
                "row": row, "batch": bl.batch_of(row), "id": p["id"],
                "board": p["board"], "title": p["title"],
                "verdict": "relevant" if row % 4 == 2 else "not",
                "confidence": "low" if border else "high",
                "reason": f"reason {row}",
                "justification": f"Constructed {dataset} {row} {'y' * row}",
                "evidence": [f"Posting {dataset} {row} body."],
                "uncertainty": "none", "borderline": border,
                "borderline_note": "constructed note" if border else ""})
        for batch in sorted({s["batch"] for s in sugg}):
            (folder / "suggestions" /
             f"{dataset}_batch_{batch:02d}.json").write_text(json.dumps({
                 "dataset": dataset, "batch": batch, "rubric_sha256": sha,
                 "labeler": "test", "human_reviewed": False,
                 "suggestions": [s for s in sugg if s["batch"] == batch]}))
        sample.write_verdict_template(folder / f"{dataset}_verdicts.csv",
                                      [p["id"] for p in posts])
    return folder


class ReviewTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.labels = make_labels(self._tmp.name)
        self.assertEqual(self.cli("init")[0], 0)
        # start from assembled suggestions, as in the real folder
        for dataset in bl.DATASETS:
            with contextlib.redirect_stdout(io.StringIO()):
                bl.main(["--labels", str(self.labels), "assemble",
                         "--dataset", dataset])

    def tearDown(self):
        self._tmp.cleanup()

    def cli(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(io.StringIO()) as err:
            code = review.main(["--labels", str(self.labels), *argv])
        return code, out.getvalue() + err.getvalue()

    def decisions(self):
        return review.read_decisions(self.labels / review.DECISIONS)

    def save(self, rows):
        with open(self.labels / review.DECISIONS, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=review.FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def verdicts(self, dataset):
        return bl.read_csv(self.labels / f"{dataset}_verdicts.csv")

    def test_init_all_pending_and_never_recreated(self):
        rows = self.decisions()
        self.assertEqual(len(rows), 74)
        self.assertEqual({r["status"] for r in rows}, {"pending"})
        code, out = self.cli("init")
        self.assertEqual(code, 1)
        self.assertIn("never recreated", out)

    def test_doc_lists_every_posting_with_status_and_flags(self):
        self.assertEqual(self.cli("doc")[0], 0)
        text = (self.labels / review.DOC).read_text()
        for r in self.decisions():
            self.assertIn(f"`{r['id']}`", text)
        self.assertIn("pending 74, approved 0, corrected 0", text)
        self.assertIn("**BORDERLINE**", text)
        self.assertIn("### Applied AI Engineers on customer teams", text)
        self.assertIn("AI/ML-sounding title word (ai)", text)
        self.assertNotIn("approved by", text.lower())

    def test_doc_never_hints_at_filter_decisions(self):
        batch = self.labels / "suggestions" / "audit_batch_01.json"
        data = json.loads(batch.read_text())
        data["suggestions"][3]["borderline_note"] = (
            "Title is a Priya target keyword; decide with row 8.")
        data["suggestions"][3]["uncertainty"] = (
            "Scope unclear; title matches Priya's target title.")
        batch.write_text(json.dumps(data))
        self.assertEqual(self.cli("doc")[0], 0)
        text = (self.labels / review.DOC).read_text().lower()
        for phrase in ("target keyword", "target title", "r1", "blindness",
                       "kept", "rejected", "infer"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)
        self.assertIn("decide with row 8.", text)
        self.assertIn("scope unclear.", text)

    def test_apply_keep_with_all_pending_changes_nothing(self):
        before = self.verdicts("audit")
        self.assertEqual(self.cli("apply", "--pending", "keep")[0], 0)
        self.assertEqual(self.verdicts("audit"), before)

    def test_apply_approved_corrected_and_blank_pending(self):
        rows = self.decisions()
        rows[0]["status"] = "approved"
        rows[1].update(status="corrected", final_verdict="unsure",
                       final_reason="text too short")
        self.save(rows)
        code, out = self.cli("apply", "--pending", "blank", "--dry-run")
        self.assertIn("nothing written", out)
        # dry run: row 2 is still the suggestion, not the correction
        self.assertEqual(self.verdicts("heldout")[1]["verdict"], "relevant")
        self.assertEqual(self.cli("apply", "--pending", "blank")[0], 0)
        held = self.verdicts("heldout")
        self.assertEqual((held[0]["verdict"], held[0]["reason"]),
                         ("not", "reason 1"))
        self.assertEqual((held[1]["verdict"], held[1]["reason"]),
                         ("unsure", "text too short"))
        self.assertEqual((held[2]["verdict"], held[2]["reason"]), ("", ""))
        self.assertTrue(all(r["verdict"] == "" for r in
                            self.verdicts("audit")))

    def test_invalid_decisions_are_refused(self):
        cases = [
            {"status": "corrected", "final_verdict": "not"},
            {"status": "corrected", "final_verdict": "maybe",
             "final_reason": "x"},
            {"status": "approved", "final_verdict": "relevant"},
            {"status": "done"},
            {"suggested_verdict": "unsure"},
        ]
        for change in cases:
            with self.subTest(change=change):
                rows = self.decisions()
                rows[0].update(change)
                self.save(rows)
                code, out = self.cli("apply", "--pending", "keep")
                self.assertEqual(code, 1)
                self.assertIn("not applied", out)

    def test_csv_edit_outside_decisions_is_not_overwritten(self):
        held = self.verdicts("heldout")
        held[0].update(verdict="unsure", reason="edited by hand")
        with open(self.labels / "heldout_verdicts.csv", "w",
                  newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=bl.COLUMNS)
            writer.writeheader()
            writer.writerows(held)
        code, out = self.cli("apply", "--pending", "keep")
        self.assertEqual(code, 1)
        self.assertIn("edited outside", out)
        self.assertEqual(self.verdicts("heldout")[0]["reason"],
                         "edited by hand")

    def test_pending_choice_is_required(self):
        with contextlib.redirect_stderr(io.StringIO()), \
                self.assertRaises(SystemExit):
            review.main(["--labels", str(self.labels), "apply"])


class HelperTests(unittest.TestCase):

    def test_role_groups(self):
        cases = {
            "Sr. Forward Deployed Engineer (FDE) - Financial Services":
                "Forward-deployed engineers",
            "Applied AI Engineer, Startups": "Applied AI Engineers on "
                                             "customer teams",
            "Lead Solutions Architect - Generative AI":
                "Solutions architects and developer advocates",
            "Research Engineer, Privacy": "Research engineers and scientists",
            "Staff Software Engineer - Ingestion":
                "Data platform, database and experimentation infrastructure",
            "Software Engineer, Cooperative AI":
                "Applied LLM, agent and AI-product engineering",
            "Staff Software Engineer (Money)":
                "Unclear team or not an engineering job",
        }
        for title, group in cases.items():
            with self.subTest(title=title):
                self.assertEqual(review.role_group(title), group)

    def test_keyword_notes(self):
        note = review.keyword_note({"title": "Applied AI Engineer",
                                    "verdict": "not"})
        self.assertIn("AI/ML-sounding title word (ai)", note)
        note = review.keyword_note({"title": "Lead SA - Generative AI",
                                    "verdict": "not"})
        self.assertIn("(generative ai)", note)
        self.assertEqual(review.keyword_note(
            {"title": "Head of Finance - Data Centers", "verdict": "not"}),
            "")
        self.assertEqual(review.keyword_note(
            {"title": "Software Engineer, Platform", "verdict": "relevant"}),
            "")

    def test_omit_keyword_remarks(self):
        omit = review.omit_keyword_remarks
        self.assertEqual(omit("Title contains a target keyword; the role "
                              "reads as a fellowship."),
                         "The role reads as a fellowship.")
        self.assertEqual(omit("Hands-on share is not stated; title matches "
                              "Priya's target title."),
                         "Hands-on share is not stated.")
        self.assertEqual(omit("Shapes financial targets for sales."),
                         "Shapes financial targets for sales.")


if __name__ == "__main__":
    unittest.main()
