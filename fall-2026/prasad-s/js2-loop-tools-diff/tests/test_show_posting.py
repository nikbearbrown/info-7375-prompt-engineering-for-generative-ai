"""tools/show_posting.py: shows the §4-cleaned posting and no verdicts or hints.

Uses one constructed posting, not real data, in a temporary board file.
"""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

from support import JS1

_spec = importlib.util.spec_from_file_location("show_posting", JS1 / "tools" / "show_posting.py")
show_posting = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(show_posting)

POSTING_ID = 123456
RAW_TITLE = "Product  Manager, Test Board "
RAW_LOCATION = "Testville"
# Before step 1 this is &lt;p&gt;..., as on the real board.
CONTENT = "&lt;p&gt;Ship   the payments&lt;/p&gt;&lt;ul&gt;&lt;li&gt;dashboard&lt;/li&gt;&lt;/ul&gt;"
# Worked by hand from §4: unescape, tags to spaces, collapse whitespace.
CLEANED = " Ship the payments dashboard "
FORBIDDEN = ("relevant", "C1", "C2", "C3", "verdict")


def write_board(folder):
    job = {"id": POSTING_ID, "title": RAW_TITLE, "location": {"name": RAW_LOCATION}, "content": CONTENT}
    text = json.dumps({"jobs": [job]}).replace("&", "\\u0026")
    path = Path(folder) / "board.json"
    path.write_text(text, encoding="utf-8")
    return path


def run_tool(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = show_posting.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class ShowPosting(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.board = write_board(self._tmp.name)

    def test_view_shows_raw_title_location_and_cleaned_content(self):
        code, out, _ = run_tool(str(POSTING_ID), "--source", str(self.board))
        self.assertEqual(code, 0)
        self.assertIn(f"posting_id: {POSTING_ID}", out)
        self.assertIn(f"title: {RAW_TITLE}", out)
        self.assertIn(f"location.name: {RAW_LOCATION}", out)
        self.assertIn(f"content: {CLEANED}", out)
        for leftover in ("<", "&lt;", "\\u0026"):
            self.assertNotIn(leftover, out)

    def test_for_claude_prints_only_the_block(self):
        code, out, _ = run_tool(str(POSTING_ID), "--source", str(self.board), "--for-claude")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [f"TITLE: {RAW_TITLE}", f"LOCATION: {RAW_LOCATION}", f"CONTENT: {CLEANED}"])

    def test_output_has_no_verdicts_or_hints(self):
        for mode in ([], ["--for-claude"]):
            code, out, _ = run_tool(str(POSTING_ID), "--source", str(self.board), *mode)
            self.assertEqual(code, 0)
            for word in FORBIDDEN:
                with self.subTest(mode=mode or "default", word=word):
                    self.assertNotIn(word.lower(), out.lower())

    def test_unknown_id_is_an_error(self):
        code, out, err = run_tool("999", "--source", str(self.board))
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("999", err)

    def test_writes_no_files(self):
        before = sorted(Path(self._tmp.name).iterdir())
        run_tool(str(POSTING_ID), "--source", str(self.board))
        run_tool(str(POSTING_ID), "--source", str(self.board), "--for-claude")
        self.assertEqual(sorted(Path(self._tmp.name).iterdir()), before)


if __name__ == "__main__":
    unittest.main()
