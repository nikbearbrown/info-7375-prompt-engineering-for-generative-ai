"""js3.shortlist and prompts/justify-v1.md on a CONSTRUCTED corpus.
`claude` is never run: every Claude call goes through a fake."""

import json
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from js3 import shortlist as sl
from tests.shortlist_fixtures import DECISIONS, ROOT, make_root

GOOD = json.dumps({"claims": [
    {"claim": "Uses PyTorch", "quote": "use PyTorch"},
    {"claim": "Uses Spark", "quote": "Spark"},
    {"claim": "Visa sponsorship", "quote": "NOT STATED"}]})


def jobs():
    """Six kept-type postings with different scores and a tie."""
    def job(i, title, body):
        return {"id": i, "title": title, "location": {"name": "Nowhere"},
                "content": body,
                "absolute_url": f"https://example.invalid/{i}"}
    return [
        job(5, "ML Engineer", "<p>PyTorch.</p>"),                 # 4
        job(4, "ML Engineer", "<p>PyTorch and Spark.</p>"),       # 5
        job(3, "ML Engineer", "<p>PyTorch, Spark, LLM.</p>"),     # 6
        job(2, "ML Engineer", "<p>PyTorch and Spark too.</p>"),   # 5
        job(1, "Data Engineer", "<p>PyTorch, Spark, MLOps.</p>"),  # 6
        job(9, "ML Engineer", "<p>Spark.</p>"),                   # 4
        job(8, "Account Executive", "<p>LLM PyTorch Spark.</p>"),  # 3, no
    ]


class FakeRunner:
    def __init__(self, stdout=GOOD, stderr="", code=0):
        self.calls = []
        self.result = (stdout, stderr, code)

    def __call__(self, prompt):
        self.calls.append(prompt)
        return self.result


class ShortlistTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_root(Path(self._tmp.name) / "project", jobs=jobs())
        self.out = self.root / "out" / "shortlist"

    def tearDown(self):
        self._tmp.cleanup()

    def build(self, run=False, runner=None, top=5):
        return sl.build(self.root, self.root / DECISIONS, top, self.out,
                        run, runner or FakeRunner(), log=lambda *a: None)

    def test_top_by_score_then_board_then_id(self):
        manifest = self.build()
        self.assertEqual([(p["id"], p["score"]) for p in
                          manifest["postings"]],
                         [("1", 6), ("3", 6), ("2", 5), ("4", 5), ("5", 4)])

    def test_prompts_written_without_running_claude(self):
        runner = FakeRunner()
        self.build(run=False, runner=runner)
        self.assertEqual(runner.calls, [])
        self.assertFalse((self.out / "claude_raw").exists())
        prompts = sorted(p.name for p in (self.out / "prompts").iterdir())
        self.assertEqual(prompts, [f"constructed__{i}.md"
                                   for i in ("1", "2", "3", "4", "5")])
        text = (self.out / "prompts" / "constructed__3.md").read_text()
        self.assertIn("PyTorch, Spark, LLM.", text)
        self.assertIn("exactly NOT STATED", text)
        self.assertIn('{"claims": [{"claim"', text)
        self.assertIn("Priya Nair", text)
        self.assertNotIn("{{", text)

    def test_rerun_is_stable_and_changed_prompt_is_refused(self):
        self.build()
        self.build()  # identical: fine
        path = self.out / "prompts" / "constructed__1.md"
        path.write_text("edited by hand\n")
        with self.assertRaises(sl.ShortlistError):
            self.build()
        self.assertEqual(path.read_text(), "edited by hand\n")

    def test_run_claude_saves_raw_records_and_never_overwrites(self):
        runner = FakeRunner(stdout="not json at all", stderr="warn", code=0)
        self.build(run=True, runner=runner)
        self.assertEqual(len(runner.calls), 5)
        raw_path = self.out / "claude_raw" / "constructed__1.json"
        record = json.loads(raw_path.read_text())
        self.assertEqual(set(record), set(sl.RAW_KEYS))
        self.assertEqual(record["raw_stdout"], "not json at all")  # kept
        self.assertEqual(record["raw_stderr"], "warn")
        self.assertEqual(record["returncode"], 0)
        self.assertEqual(record["command"][:2], ["claude", "-p"])
        prompt = (self.out / "prompts" / "constructed__1.md").read_text()
        self.assertEqual(record["prompt_sha256"], sl.sha256_text(prompt))
        datetime.fromisoformat(record["date_utc"])
        before = raw_path.read_bytes()
        second = FakeRunner(stdout=GOOD)
        self.build(run=True, runner=second)
        self.assertEqual(second.calls, [])
        self.assertEqual(raw_path.read_bytes(), before)

    def test_default_runner_command_via_injected_subprocess(self):
        seen = {}

        def fake_run(cmd, **kwargs):
            seen.update(cmd=cmd, **kwargs)
            return subprocess.CompletedProcess(cmd, 3, "out", "err")
        self.assertEqual(sl.run_claude("PROMPT", run=fake_run),
                         ("out", "err", 3))
        self.assertEqual(seen["cmd"], sl.CLAUDE_COMMAND)
        self.assertEqual(seen["input"], "PROMPT")

        def missing(cmd, **kwargs):
            raise FileNotFoundError("claude")
        stdout, stderr, code = sl.run_claude("P", run=missing)
        self.assertIsNone(code)
        self.assertIn("cannot start claude", stderr)

    def test_unsafe_names_and_no_kept(self):
        with self.assertRaises(sl.ShortlistError):
            sl.stem("constructed", "../../etc/passwd")
        self.assertEqual(sl.top_kept([{"decision": "rejected"}], 5), [])

    def test_template_placeholders_are_filled_once(self):
        template = (ROOT / "prompts" / "justify-v1.md").read_text()
        posting = {"board": "b", "id": "1", "title": "T {{body}}",
                   "location": "L", "body_text": "B {{title}}"}
        target = {"target_title_keywords": ["ai engineer"],
                  "excluded_terms": ["clearance"]}
        text = sl.render_prompt(template, posting, target)
        self.assertIn("title: T {{body}}", text)
        self.assertIn("B {{title}}", text)
        self.assertIn("ai engineer", text)


class PromptFileTests(unittest.TestCase):

    def test_justify_prompt_contract(self):
        text = (ROOT / "prompts" / "justify-v1.md").read_text()
        for phrase in ("3 to 5 claims", "verbatim", "exactly NOT STATED",
                       "JSON only", '{"claims": [{"claim": ',
                       "data/target.example.json", "Priya Nair"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
