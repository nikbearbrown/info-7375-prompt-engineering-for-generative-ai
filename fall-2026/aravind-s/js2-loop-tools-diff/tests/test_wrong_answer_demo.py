"""tools/wrong_answer_demo.py on a constructed run of the course's four boards: the planted copy ends
"finished" and the independent check flags it; the unchanged copy passes the check. Offline."""

import importlib.util
import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from .loop_helpers import (FakeNet, REPO, Workspace, answer, ashby_job, greenhouse_job, lever_job, url)

spec = importlib.util.spec_from_file_location("wrong_answer_demo", REPO / "tools" / "wrong_answer_demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

OPENAI, VERKADA, PALANTIR, BAD = (("ashby", "openai"), ("greenhouse", "verkada"), ("lever", "palantir"),
                                  ("greenhouse", "no-such-board-js2-test"))


class WrongAnswerDemoTest(unittest.TestCase):
    def test_the_planted_replay_is_clean_and_wrong_and_the_check_catches_it(self):
        ws = Workspace()
        self.addCleanup(ws.cleanup)
        ws.boards(OPENAI, VERKADA, PALANTIR, BAD + ({"deliberate_failure": True},))
        ws.run(FakeNet({url(*OPENAI): [answer(*OPENAI, [ashby_job("a-1")])],
                        url(*VERKADA): [answer(*VERKADA, [greenhouse_job(101)])],
                        url(*PALANTIR): [answer(*PALANTIR, [lever_job("l-1")])],
                        url(*BAD): [answer(*BAD, status=404, raw=b'{"status":404,"error":"Job not found"}')]}))
        out = Path(tempfile.mkdtemp()) / "demo"
        self.addCleanup(shutil.rmtree, out.parent)
        with redirect_stdout(io.StringIO()) as screen:
            code = demo.main([str(ws.run_dirs()[0]), str(out)])
        self.assertEqual(code, 0, screen.getvalue())
        self.assertIn("planted replay: exit 0; check: exit 1", screen.getvalue())
        self.assertIn("unchanged replay: exit 1; check: exit 0", screen.getvalue())
        text = (out / "DEMO.md").read_text(encoding="utf-8")
        self.assertIn("PLANTED: wrong version 1a", text)
        self.assertIn("the report says 'read', but the saved answer is HTTP 404", text)
        self.assertIn("replay of the saved answers", (out / "planted-replay" / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
