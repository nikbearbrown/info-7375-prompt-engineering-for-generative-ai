"""Action surfaces: the chat text hides contact details, and the file way gives Claude only the Read tool.

The Claude reply here is CONSTRUCTED; no real Claude call is made.
"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from agent import config, resume, surfaces

JOB = {"id": 1, "title": "Software Engineer", "location": {"name": "Remote, US"},
       "content": "&lt;p&gt;Python and AWS&lt;/p&gt;"}
GOOD = {"verdict": "Relevant", "posting_fields": ["title"], "resume_fields": ["skills.languages"],
        "reason": "constructed reply"}


class SurfaceTests(unittest.TestCase):
    def setUp(self):
        self.out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.out)
        self.persona = resume.load(config.RESUME)

    def test_chat_text_has_no_email_or_phone(self):
        text = surfaces.chat_way(JOB, self.persona, out=self.out).read_text(encoding="utf-8")
        self.assertIn("Python and AWS", text)
        self.assertNotIn(self.persona["personal"]["email"], text)
        self.assertNotIn(self.persona["personal"]["phone"], text)

    def test_file_way_gives_only_the_read_tool_and_saves_the_reply(self):
        seen = {}

        def fake_run(cmd, cwd, **kwargs):
            seen["cmd"], seen["files"] = cmd, sorted(p.name for p in Path(cwd).iterdir())
            envelope = {"result": json.dumps(GOOD), "modelUsage": {"constructed": {}}, "num_turns": 3}
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(envelope), stderr="")

        saved = surfaces.file_way(JOB, config.RESUME, run=fake_run, out=self.out)
        tools = seen["cmd"][seen["cmd"].index("--tools") + 1]
        self.assertEqual(tools, "Read")
        self.assertEqual(seen["files"], ["posting.txt", "resume.json"], "Claude's folder holds only the two files")
        self.assertTrue(json.loads(saved.read_text())["valid"])


if __name__ == "__main__":
    unittest.main()
