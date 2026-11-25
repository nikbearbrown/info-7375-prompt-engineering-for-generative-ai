"""Baseline / second-run tests and report checks, offline via --from-raw."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import fixtures
from agent import run, state


class RunHarness:
    """Runs agent.run.main against CONSTRUCTED raw files in a temp dir."""

    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.state = self.tmp / "state.json"
        self.reports = self.tmp / "reports"

    def run(self, postings, timestamp, extra=(), claude_runner=None):
        raw = fixtures.write_board(self.tmp / f"{timestamp}_scaleai.json",
                                   postings)
        argv = ["--from-raw", str(raw), "--state", str(self.state),
                "--resume", str(fixtures.RESUME_PATH),
                "--target", str(fixtures.TARGET_PATH),
                "--reports-dir", str(self.reports), *extra]
        with redirect_stdout(io.StringIO()):
            code = run.main(argv, claude_runner=claude_runner,
                            timestamp=timestamp)
        assert code == 0, code
        report = json.loads(
            (self.reports / f"{timestamp}.json").read_text(encoding="utf-8"))
        md = (self.reports / f"{timestamp}.md").read_text(encoding="utf-8")
        return report, md


class StateTests(unittest.TestCase):

    def test_baseline_reports_zero_new_and_records_all_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            h = RunHarness(tmp)
            report, md = h.run(fixtures.ALL, "20261031T010000Z")
            self.assertEqual(report["run_type"], "baseline")
            self.assertEqual(report["counts"]["new"], 0)
            self.assertEqual(report["new_postings"], [])
            self.assertEqual(state.load_seen(h.state),
                             {p["id"] for p in fixtures.ALL})
            self.assertIn("Baseline run", md)

    def test_second_run_reports_only_ids_not_in_state(self):
        first = [fixtures.RELEVANT, fixtures.EXCLUDED, fixtures.WRONG_TITLE]
        second = first + [fixtures.ONE_SKILL, fixtures.TWO_SKILLS]
        with tempfile.TemporaryDirectory() as tmp:
            h = RunHarness(tmp)
            h.run(first, "20261031T010000Z")
            seen_after_first = state.load_seen(h.state)
            report, _ = h.run(second, "20261031T020000Z")
            new_ids = [e["id"] for e in report["new_postings"]]
            self.assertEqual(report["run_type"], "seeded")
            self.assertEqual(new_ids, [9004, 9005])
            self.assertFalse(set(new_ids) & seen_after_first)
            self.assertEqual(report["counts"]["previously_seen"], 3)
            # A third identical run finds nothing new.
            report3, _ = h.run(second, "20261031T030000Z")
            self.assertEqual(report3["counts"]["new"], 0)

    def test_split_new_without_state_is_baseline(self):
        self.assertEqual(state.split_new([1, 2], None), ([], True))
        self.assertEqual(state.split_new([1, 2, 3], {2}), ([1, 3], False))

    def test_report_has_hash_labels_and_no_contact_fields(self):
        resume, _ = fixtures.load_example_inputs()
        contacts = [resume["personal"][k]
                    for k in ("email", "phone", "linkedin", "github")]
        with tempfile.TemporaryDirectory() as tmp:
            h = RunHarness(tmp)
            h.run([fixtures.EXCLUDED], "20261031T010000Z")
            report, md = h.run(fixtures.ALL, "20261031T020000Z")
            raw = Path(tmp) / "20261031T020000Z_scaleai.json"
            self.assertEqual(report["raw_sha256"],
                             run.fetch.sha256_hex(raw.read_bytes()))
            entry = report["new_postings"][0]
            self.assertEqual(entry["rule_verdict"]["label"], "record")
            self.assertEqual(entry["claude_verdict"],
                             {"status": "not run", "label": "judgment"})
            self.assertIn("Claude verdict (judgment): not run", md)
            self.assertIn("Rule verdict (record)", md)
            files = list((Path(tmp) / "reports").iterdir()) + [h.state]
            for path in files:
                text = path.read_text(encoding="utf-8")
                for value in contacts:
                    self.assertNotIn(value, text, path.name)

    def test_claude_flag_records_judgment_and_never_overrides_rule(self):
        def disagreeing_fake(prompt):
            pid = int(prompt.split("posting.id: ")[1].split()[0])
            return json.dumps({"posting_id": pid, "verdict": "relevant",
                               "resume_fields": ["skills.languages"],
                               "posting_fields": ["posting.content"],
                               "reason": "FAKE runner output for tests."})

        with tempfile.TemporaryDirectory() as tmp:
            h = RunHarness(tmp)
            h.run([], "20261031T010000Z")
            report, md = h.run([fixtures.EXCLUDED], "20261031T020000Z",
                               extra=["--claude"],
                               claude_runner=disagreeing_fake)
            entry = report["new_postings"][0]
            self.assertEqual(entry["rule_verdict"]["verdict"], "not_relevant")
            self.assertEqual(entry["claude_verdict"]["status"], "judged")
            self.assertEqual(entry["claude_verdict"]["label"], "judgment")
            self.assertIn("judgment, not a record", md)


if __name__ == "__main__":
    unittest.main()
