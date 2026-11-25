"""Fixes found by the 2026-10-30 seeded run: the frozen revision-1 is the default prompt, a seeded
state keeps its label, and the printed report path is the real --runs folder.

No real `claude` call: the judge is replaced by a fake that records the template it was given.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests import helpers


def fake_reply(job, failed_check=True, verdict="not_relevant"):
    reply = {"posting_id": job["id"], "verdict": verdict,
             "citations": [{"resume_field": "skills.languages", "posting_field": "title",
                            "quote": job["title"]}],
             "label": "judgment"}
    if failed_check:
        reply["failed_check"] = "R1" if verdict == "not_relevant" else None
    return json.dumps(reply)


class AgentFixes(helpers.ContractTest):
    modules = ("agent.run", "agent.watch")

    def args(self, tmp, *extra, state=None):
        return [*extra, "--state", str(state or Path(tmp) / "state" / "seen_ids.json"),
                "--runs", str(Path(tmp) / "runs")]

    def judged_run(self, tmp, *extra, failed_check=True, verdict="not_relevant"):
        """A baseline, then a second run with one new posting judged by a fake Claude."""
        jobs = helpers.postings()
        self.run.main(self.args(tmp, "--replay", str(helpers.write_board(Path(tmp) / "b1.json", jobs[:-1]))))
        templates = []

        def fake_judge(job, resume, out_dir, template=None):
            templates.append(template)
            return {"status": "ran", "result": fake_reply(job, failed_check, verdict),
                    "meta": {"model": "fake", "session_id": "s", "date": "d"}}

        with mock.patch.object(self.run.claude_judge, "judge", side_effect=fake_judge):
            report = self.run.main(self.args(
                tmp, "--replay", str(helpers.write_board(Path(tmp) / "b2.json", jobs)), "--claude", *extra))
        return report, templates

    def test_default_run_uses_frozen_revision_1_and_its_schema(self):
        text = (helpers.ROOT / "prompts" / "revision-1.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            report, templates = self.judged_run(tmp)
        self.assertEqual(templates, [text])
        self.assertEqual(report["prompt"]["file"], "prompts/revision-1.md")
        self.assertEqual(report["prompt"]["schema"], "revision-1")
        self.assertEqual(report["prompt"]["sha256"],
                         "16ecb4366aaf1d07f52f33ac5f9bb0bc9e442616954bdab6795e96968c453206",
                         "the hash frozen in PROMPT-EXPERIMENT.md")
        judgment = report["claude"]["judgments"][0]
        self.assertEqual(judgment["validator_errors"], [])
        self.assertEqual(judgment["failed_check"], "R1")

    def test_default_schema_rejects_a_reply_without_failed_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, _ = self.judged_run(tmp, failed_check=False)
        errors = report["claude"]["judgments"][0]["validator_errors"]
        self.assertTrue(any("failed_check" in e for e in errors), errors)

    def test_prompt_baseline_keeps_the_old_prompt_and_schema(self):
        text = (helpers.ROOT / "prompts" / "baseline.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            report, templates = self.judged_run(tmp, "--prompt", "baseline", failed_check=False)
        self.assertEqual(templates, [text])
        self.assertEqual(report["prompt"]["schema"], "baseline")
        self.assertEqual(report["prompt"]["sha256"], hashlib.sha256(text.encode("utf-8")).hexdigest())
        judgment = report["claude"]["judgments"][0]
        self.assertEqual(judgment["validator_errors"], [])
        self.assertNotIn("failed_check", judgment, "a missing field is not reported as null")

    def test_report_md_names_prompt_file_and_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, _ = self.judged_run(tmp)
            md = (Path(tmp) / "runs" / report["run"] / "report.md").read_text(encoding="utf-8")
        self.assertIn("`prompts/revision-1.md`", md)
        self.assertIn(report["prompt"]["sha256"], md)
        self.assertIn("failed_check `R1`", md)

    def test_report_md_prints_a_null_failed_check_as_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, _ = self.judged_run(tmp, verdict="relevant")
            md = (Path(tmp) / "runs" / report["run"] / "report.md").read_text(encoding="utf-8")
        self.assertEqual(report["claude"]["judgments"][0]["validator_errors"], [])
        self.assertIsNone(report["claude"]["judgments"][0]["failed_check"])
        self.assertIn("failed_check `null`", md)
        self.assertNotIn("None", md)

    def test_seeded_run_keeps_the_seeded_label_and_note(self):
        jobs = helpers.postings()
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "seeded" / "seen_ids.json"
            state.parent.mkdir()
            state.write_text(json.dumps({"seeded": True, "note": "3 ids removed", "last_run": "x",
                                         "seen_ids": [j["id"] for j in jobs[:-1]]}), encoding="utf-8")
            board = helpers.write_board(Path(tmp) / "b.json", jobs)
            report = self.run.main(self.args(tmp, "--replay", str(board), "--seeded", state=state))
            saved = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(report["new_ids"], [jobs[-1]["id"]])
        self.assertIs(saved["seeded"], True)
        self.assertEqual(saved["note"], "3 ids removed")
        self.assertEqual(saved["seen_ids"], sorted(j["id"] for j in jobs))

    def test_seeded_label_is_added_and_never_dropped(self):
        jobs = helpers.postings()
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "s.json"
            board = helpers.write_board(Path(tmp) / "b.json", jobs)
            self.run.main(self.args(tmp, "--replay", str(board), "--seeded", state=state))
            first = json.loads(state.read_text(encoding="utf-8"))
            self.run.main(self.args(tmp, "--replay", str(board), state=state))
            second = json.loads(state.read_text(encoding="utf-8"))
        self.assertIs(first["seeded"], True)
        self.assertIn("SEEDED", first["note"])
        self.assertIs(second["seeded"], True, "a later unlabeled run must not make it look real")
        self.assertEqual(second["note"], first["note"])

    def test_unseeded_state_stays_unlabeled(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "s.json"
            board = helpers.write_board(Path(tmp) / "b.json", helpers.postings())
            self.run.main(self.args(tmp, "--replay", str(board), state=state))
            self.assertEqual(set(json.loads(state.read_text(encoding="utf-8"))), {"last_run", "seen_ids"})

    def test_printed_path_is_the_real_runs_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = helpers.write_board(Path(tmp) / "b.json", helpers.postings())
            line = self.run.cli(self.args(tmp, "--replay", str(board)))
            printed = Path(line.split("report in ", 1)[1])
            self.assertTrue(printed.is_file(), line)
            self.assertEqual(printed.resolve(), (Path(tmp) / "runs" / printed.parent.name / "report.md").resolve())
        self.assertEqual(self.run.summary({"run": "r", "total_postings": 2, "baseline": False, "new_ids": [1]},
                                          Path("seeded/rev1/runs")),
                         "r: 2 postings, 1 new, report in seeded/rev1/runs/r/report.md")


if __name__ == "__main__":
    unittest.main()
