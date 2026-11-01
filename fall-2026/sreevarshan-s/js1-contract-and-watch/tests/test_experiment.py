"""Prompt experiment runner. The claude subprocess is MOCKED: no real Claude call, no network."""

import io
import json
import tempfile
import unittest
from pathlib import Path

from experiments import run_experiment as rx

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text(encoding="utf-8"))
PROFILE = json.loads((ROOT / "persona" / "priya-nair.profile.json").read_text(encoding="utf-8"))
FIXTURES = Path(__file__).parent / "fixtures"

DEV_IDS = [7737233002, 8029666002, 8401114002, 8546367002, 8569392002,
           8648494002, 8692962002, 8824168002, 8847738002, 8921476002]
HELDOUT_IDS = [7958982002, 8091041002, 8540267002, 8560779002, 8574655002,
               8656900002, 8760167002, 8829033002, 8870159002, 8923831002]


def reply(pid, verdict):
    return json.dumps({"posting_id": pid, "verdict": verdict,
                       "skills_cited": [{"skill": "Python", "resume_field": "skills.languages"}],
                       "explanation": "The title and description were compared with Priya's fields."})


class SplitTests(unittest.TestCase):
    def test_frozen_split_is_read_from_label_set(self):
        self.assertEqual(rx.read_split(ROOT / "LABEL_SET.md", "dev"), DEV_IDS)
        self.assertEqual(rx.read_split(ROOT / "LABEL_SET.md", "heldout"), HELDOUT_IDS)

    def test_hand_labels_cover_all_twenty(self):
        labels = rx.read_hand_labels(ROOT / "labels" / "HAND_LABELS.md")
        self.assertEqual(sorted(labels), sorted(DEV_IDS + HELDOUT_IDS))
        self.assertTrue(set(labels.values()) <= {"relevant", "not relevant"})


class ScoringTests(unittest.TestCase):
    def test_pass_requires_valid_and_matching_verdict(self):
        self.assertTrue(rx.passes({"status": "valid", "verdict": "not relevant"}, "not relevant"))
        self.assertFalse(rx.passes({"status": "valid", "verdict": "relevant"}, "not relevant"))

    def test_invalid_result_is_a_fail(self):
        self.assertFalse(rx.passes({"status": "invalid", "posting_id": 1}, "not relevant"))
        self.assertFalse(rx.passes({"status": "invalid", "verdict": "not relevant"}, "not relevant"))
        self.assertEqual(rx.claude_verdict({"status": "invalid"}), "invalid")


class RunTests(unittest.TestCase):
    """End to end on CONSTRUCTED postings, with a fake claude that answers by prompt."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        # CONSTRUCTED: two postings from the test fixture, a two-row split and two hand labels.
        jobs = json.loads((FIXTURES / "constructed_postings.json").read_text(encoding="utf-8"))["jobs"]
        self.raw = self.tmp / "raw.json"
        self.raw.write_text(json.dumps({"jobs": [j for j in jobs if j["id"] in (8000001, 8000002)]}),
                            encoding="utf-8")
        self.label_set = self.tmp / "LABEL_SET.md"
        self.label_set.write_text("| # | posting id | title | split |\n|---|---|---|---|\n"
                                  "| 1 | 8000001 | Senior Data Engineer | development |\n"
                                  "| 2 | 8000002 | Data Engineer | held-out |\n"
                                  "| 3 | 8000002 | Data Engineer | development |\n", encoding="utf-8")
        self.hand = self.tmp / "HAND_LABELS.md"
        self.hand.write_text("| posting_id | label | borderline | why |\n|---|---|---|---|\n"
                             "| 8000001 | not relevant | no | CONSTRUCTED |\n"
                             "| 8000002 | relevant | no | CONSTRUCTED |\n", encoding="utf-8")
        self.results_dir = self.tmp / "experiments"
        self.results_dir.mkdir()
        self.calls = []

    def tearDown(self):
        self._tmp.cleanup()

    def _runner(self, prompt):
        self.calls.append(prompt)
        pid = 8000001 if '"id": 8000001' in prompt else 8000002
        if "Check every mandatory eligibility condition" in prompt:   # revised
            return 0, ("garbage" if pid == 8000002 else reply(pid, "not relevant")), ""
        return 0, reply(pid, "relevant"), ""                           # baseline says relevant to both

    def _run(self, split):
        out, err = io.StringIO(), io.StringIO()
        code = rx.run(split, runner=self._runner, stamp="2026-10-30T12-00-00Z", label_set=self.label_set,
                      hand_labels=self.hand, raw=self.raw, evidence_root=self.tmp / "evidence",
                      results_dir=self.results_dir, resume=RESUME, profile=PROFILE, out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    def test_heldout_is_refused_before_dev(self):
        code, _, err = self._run("heldout")
        self.assertEqual(code, rx.EXIT_HELDOUT_BEFORE_DEV)
        self.assertIn("run the dev split first", err)
        self.assertEqual(self.calls, [], "no Claude call before refusing")
        self.assertFalse((self.tmp / "evidence").exists())

    def test_dev_run_scores_and_counts_correctly(self):
        code, out, _ = self._run("dev")
        self.assertEqual(code, 0)
        # 8000001: hand not relevant; baseline relevant (fail), revised not relevant (pass), rule not relevant (pass)
        # 8000002: hand relevant; baseline relevant (pass), revised garbage twice -> invalid (fail), rule relevant (pass)
        self.assertIn("baseline 1/2, revised 1/2, rule 2/2", out)
        self.assertIn("invalid results: 1 (baseline 0, revised 1)", out)
        self.assertEqual(len(self.calls), 2 + 1 + 2, "baseline once each, revised once + one retry for 8000002")
        md = (self.results_dir / "results_dev.md").read_text(encoding="utf-8")
        self.assertIn("| 8000001 | Senior Data Engineer | not relevant | not relevant | relevant | not relevant | fail | pass |", md)
        self.assertIn("| 8000002 | Data Engineer | relevant | relevant | relevant | invalid | pass | fail |", md)
        self.assertIn("- **Baseline:** 1/2", md)
        self.assertIn("- **Revised:** 1/2", md)
        self.assertIn("- **Rule:** 2/2", md)
        evidence = self.tmp / "evidence" / "dev" / "2026-10-30T12-00-00Z"
        self.assertTrue((evidence / "rule_records.json").exists())
        self.assertTrue((evidence / "2026-10-30T12-00-00Z-revised-8000002-attempt2.txt").exists())

    def test_heldout_runs_after_dev(self):
        self._run("dev")
        code, out, _ = self._run("heldout")
        self.assertEqual(code, 0)
        self.assertIn("split: heldout (1 postings)", out)
        self.assertTrue((self.results_dir / "results_heldout.md").exists())


if __name__ == "__main__":
    unittest.main()
