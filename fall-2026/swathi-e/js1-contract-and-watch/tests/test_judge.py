"""Offline tests for the Claude judge and its validator (JUDGE-CONTRACT.md).

Written by Claude Code on 2026-10-25. Every "Claude output" below is a
HAND-MADE FAKE written for these tests; none of it came from Claude. No test
calls Claude or the network.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import judge  # noqa: E402
import persona  # noqa: E402

_, TARGETS = persona.load_persona()

# CONSTRUCTED description, not a real posting.
DESCRIPTION = ("We build ML platforms.\nRequirements:\n- 0-1 years of experience with Python "
               "and SQL\n- Visa sponsorship is available for this role")
POSTING = {"id": 999, "title": "ML Engineer, New Grad", "location": "Remote - US",
           "description": DESCRIPTION, "raw_file": "fake.json"}


def fake_output(**changes):
    output = {
        "verdict": "relevant",
        "label": "judgment",
        "experience_found": "0-1 years of experience with Python and SQL",
        "authorization_found": "Visa sponsorship is available for this role",
        "posting_fields_cited": ["title", "location", "description"],
        "resume_fields_cited": ["target roles", "location", "visa status"],
        "reason": "Entry-level ML role in the US; sponsorship available.",
    }
    output.update(changes)
    return json.dumps(output)


class ValidatorAccepts(unittest.TestCase):
    def test_valid_output_is_accepted(self):
        output, errors = judge.validate(fake_output(), DESCRIPTION)
        self.assertEqual(errors, [])
        self.assertEqual(output["verdict"], "relevant")

    def test_not_relevant_with_both_sentinels_is_accepted(self):
        text = fake_output(verdict="not_relevant", experience_found="experience not stated",
                           authorization_found="none stated")
        self.assertEqual(judge.validate(text, DESCRIPTION)[1], [])

    def test_quote_split_across_lines_differently_is_still_word_for_word(self):
        text = fake_output(experience_found="0-1 years of\n   experience with Python")
        self.assertEqual(judge.validate(text, DESCRIPTION)[1], [])


class ValidatorRejects(unittest.TestCase):
    def assertRejected(self, text, fragment):
        output, errors = judge.validate(text, DESCRIPTION)
        self.assertIsNone(output)
        self.assertTrue(any(fragment in e for e in errors), errors)

    def test_invalid_json(self):
        self.assertRejected('{"verdict": "relevant",', "not valid JSON")

    def test_json_inside_code_fences_or_prose(self):
        self.assertRejected("```json\n" + fake_output() + "\n```", "not valid JSON")
        self.assertRejected("Here is my verdict: " + fake_output(), "not valid JSON")

    def test_not_an_object(self):
        self.assertRejected('["relevant"]', "not a JSON object")

    def test_missing_and_extra_keys(self):
        missing = json.loads(fake_output())
        del missing["reason"]
        self.assertRejected(json.dumps(missing), "missing key 'reason'")
        self.assertRejected(fake_output(confidence=0.9), "extra key 'confidence'")

    def test_wrong_verdicts(self):
        for verdict in ("not relevant", "Relevant", "yes", "relevant ", None):
            with self.subTest(verdict=verdict):
                self.assertRejected(fake_output(verdict=verdict), "verdict")

    def test_label_other_than_judgment(self):
        for label in ("fact", "record", "Judgment"):
            with self.subTest(label=label):
                self.assertRejected(fake_output(label=label), "label")

    def test_empty_citations(self):
        self.assertRejected(fake_output(posting_fields_cited=[]), "posting_fields_cited")
        self.assertRejected(fake_output(resume_fields_cited=[]), "resume_fields_cited")
        self.assertRejected(fake_output(resume_fields_cited=[""]), "resume_fields_cited")

    def test_quote_not_in_description(self):
        self.assertRejected(fake_output(experience_found="3+ years of experience"), "experience_found quote")
        self.assertRejected(fake_output(authorization_found="US citizenship required"), "authorization_found quote")

    def test_quote_must_match_exactly_not_paraphrase_or_case(self):
        self.assertRejected(fake_output(experience_found="0-1 Years of Experience with Python"), "experience_found")
        self.assertRejected(fake_output(experience_found="zero to one years of experience"), "experience_found")

    def test_empty_quote_and_near_miss_sentinel(self):
        self.assertRejected(fake_output(experience_found=""), "experience_found")
        self.assertRejected(fake_output(authorization_found="None stated."), "authorization_found")


class DescriptionText(unittest.TestCase):
    def test_double_escaped_html_becomes_plain_text(self):
        content = "&lt;p&gt;&lt;strong&gt;AI Engineer – FDE&lt;/strong&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Spark™ &amp;amp; ML&lt;/li&gt;&lt;/ul&gt;"
        self.assertEqual(judge.description_text(content), "AI Engineer – FDE\n- Spark™ & ML")


def fake_runner(stdout, calls):
    def run(command, **kwargs):
        calls.append((command, kwargs, sorted(Path(kwargs["cwd"]).iterdir())))
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")
    return run


def envelope(result, model=judge.MODEL):
    return json.dumps({"type": "result", "is_error": False, "result": result,
                       "session_id": "fake-session", "modelUsage": {model: {}}})


class JudgeRuns(unittest.TestCase):
    def test_offline_by_default_never_calls_claude(self):
        def refuse(*args, **kwargs):
            raise AssertionError("offline judge must not run a subprocess")
        record = judge.judge_posting(POSTING, TARGETS, runner=refuse)
        self.assertEqual((record["mode"], record["claude_called"], record["status"]), ("offline", False, "not_run"))
        self.assertIn("visa status: F-1 OPT", record["user_message"])

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fixture-not-a-secret"})
    def test_live_call_shape_empty_folder_no_key_no_stdin(self):
        calls = []
        record = judge.judge_posting(POSTING, TARGETS, live=True, runner=fake_runner(envelope(fake_output()), calls))
        command, kwargs, folder_contents = calls[0]
        self.assertEqual(command[:2], ["claude", "-p"])
        for flag in (["--model", "claude-opus-5-5"], ["--tools", ""], ["--output-format", "json"]):
            self.assertIn(flag, [command[i:i + 2] for i in range(len(command) - 1)])
        self.assertIn("--no-session-persistence", command)
        self.assertEqual(folder_contents, [])
        self.assertIs(kwargs["stdin"], subprocess.DEVNULL)
        self.assertNotIn("ANTHROPIC_API_KEY", kwargs["env"])
        self.assertEqual((record["status"], record["label"], record["model_matches_pin"]),
                         ("accepted", "judgment", True))

    def test_rejected_output_is_recorded_not_repaired(self):
        fenced = "```json\n" + fake_output() + "\n```"
        record = judge.judge_posting(POSTING, TARGETS, live=True, runner=fake_runner(envelope(fenced), []))
        self.assertEqual(record["status"], "rejected")
        self.assertIsNone(record["judge_output"])
        self.assertEqual(record["raw_output"], fenced)

    def test_reported_model_other_than_pin_is_flagged(self):
        record = judge.judge_posting(POSTING, TARGETS, live=True,
                                     runner=fake_runner(envelope(fake_output(), model="claude-other"), []))
        self.assertFalse(record["model_matches_pin"])
        self.assertEqual(record["model_reported"], ["claude-other"])

    def test_broken_envelope_is_a_failed_call(self):
        record = judge.judge_posting(POSTING, TARGETS, live=True, runner=fake_runner("not json", []))
        self.assertEqual((record["status"], record["judge_output"]), ("call_failed", None))


class WatchWithJudge(unittest.TestCase):
    """The watch gives each new posting both verdicts. Fetches and Claude replies are FAKES."""

    def setUp(self):
        import tempfile
        import watch
        self.watch = watch
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.paths = {"state_path": self.root / "state.json", "raw_dir": self.root / "raw",
                      "report_dir": self.root / "reports", "judge_dir": self.root / "judge"}
        board = lambda *jobs: json.dumps({"jobs": [{"id": i, "title": t, "location": {"name": "Remote - US"},
                                                     "absolute_url": None} for i, t in jobs]}).encode()
        (self.root / "first.json").write_bytes(board((1, "Data Engineer")))
        (self.root / "second.json").write_bytes(board((1, "Data Engineer"), (2, "ML Engineer, New Grad")))

    def tearDown(self):
        self.tmp.cleanup()

    def fake_fetch(self, posting_id):
        path = self.root / f"job_{posting_id}.json"
        path.write_text(json.dumps({"id": posting_id, "title": "ML Engineer, New Grad",
                                    "location": {"name": "Remote - US"},
                                    "content": "&lt;p&gt;" + DESCRIPTION + "&lt;/p&gt;"}))
        return path

    def run_twice(self, **judge_args):
        self.watch.run(from_file=self.root / "first.json", **self.paths)
        return self.watch.run(from_file=self.root / "second.json", **self.paths, **judge_args)

    def test_default_run_never_calls_the_judge(self):
        def refuse(*args, **kwargs):
            raise AssertionError("watch must not fetch or call Claude without judge_live")
        summary = self.run_twice(fetch_posting=refuse, runner=refuse)
        entry = summary["report"][0]
        self.assertEqual((entry["rule"]["source"], entry["claude_judge"]["status"]), ("written rule (record)", "not_run"))

    def test_judge_live_adds_a_labelled_judgment_for_the_same_posting(self):
        summary = self.run_twice(judge_live=True, fetch_posting=self.fake_fetch,
                                 runner=fake_runner(envelope(fake_output()), []))
        entry = summary["report"][0]
        judged = entry["claude_judge"]
        self.assertEqual((entry["posting_id"], judged["posting_id"]), (2, 2))
        self.assertEqual((judged["label"], judged["status"], judged["verdict"]), ("judgment", "accepted", "relevant"))
        self.assertTrue((self.watch.HERE / judged["record_file"]).exists() or Path(judged["record_file"]).exists())

    def test_rejected_judgment_is_kept_next_to_the_rule_verdict(self):
        summary = self.run_twice(judge_live=True, fetch_posting=self.fake_fetch,
                                 runner=fake_runner(envelope("not json at all"), []))
        judged = summary["report"][0]["claude_judge"]
        self.assertEqual((judged["status"], judged["verdict"]), ("rejected", None))
        self.assertEqual(summary["report"][0]["rule"]["verdict"], "relevant")

    def test_judgment_attached_to_the_wrong_posting_is_caught(self):
        postings = self.watch.parse_postings((self.root / "second.json").read_bytes())
        report = self.watch.build_report(postings, TARGETS)
        report[0]["claude_judge"] = {"status": "accepted", "posting_id": postings[1]["id"]}
        self.assertTrue(self.watch.pairing_errors(postings, report, TARGETS))

    def test_judge_report_requires_explicit_live_flag(self):
        with self.assertRaises(SystemExit):
            self.watch.main(["--judge-report", "any.json"])


if __name__ == "__main__":
    unittest.main()
