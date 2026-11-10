"""Review packet (Chapter 6): the failed-board count defect, written before the patch.

The defect, found in the live run runs/run-2026-11-10T025118Z: the deliberately misspelled
board returned HTTP 404 and is correctly marked "failed", but summary.json says
"new_count": 0 for it and the console prints "new=0". GATE.md section 1: "A failed board must
not be reported as having zero new jobs."

Split of work (see SOURCES.md):
  setup       written by Claude: temporary folders, replayed responses, console capture
  assertions  written by Yash, where the two placeholders below say so

run from the js2-loop-tools-diff folder:
  python3 -m unittest tests.test_review_failed_board_count -v

Offline: agent.main() runs with --replay, so nothing is fetched. The three real boards answer
from small constructed responses, and the misspelled board has no replay file, so the replay
answers 404, the same status as the live run.
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER))
import agent  # noqa: E402

FAILED_BOARD = "Deliberate failure"          # the name in config/live.json


def constructed_greenhouse(*ids):
    return json.dumps({"_comment": "CONSTRUCTED test response",
                       "jobs": [{"id": i, "title": f"Posting {i}", "content": "", "location": {"name": "Remote"},
                                 "absolute_url": f"https://example.com/{i}"} for i in ids]})


def constructed_ashby(*ids):
    return json.dumps({"_comment": "CONSTRUCTED test response",
                       "jobs": [{"id": i, "title": f"Posting {i}", "descriptionHtml": "", "location": "Remote",
                                 "jobUrl": f"https://example.com/{i}"} for i in ids]})


class FailedBoardCount(unittest.TestCase):
    """Runs the real CLI on the live configuration (config/live.json), with replayed responses."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        replay, state, runs = root / "replay", root / "state", root / "runs"
        replay.mkdir()
        (replay / "greenhouse-databricks.json").write_text(constructed_greenhouse(1, 2))
        (replay / "greenhouse-anthropic.json").write_text(constructed_greenhouse(3))
        (replay / "ashby-openai.json").write_text(constructed_ashby("a-1"))
        # no replay file for greenhouse-databricks-misspelled: the replay answers HTTP 404

        console = io.StringIO()
        with contextlib.redirect_stdout(console):
            self.exit_code = agent.main(["--config", str(FOLDER / "config" / "live.json"), "--replay", str(replay),
                                         "--state-dir", str(state), "--runs-dir", str(runs)])
        self.console = console.getvalue()
        run_dir = sorted(runs.glob("run-*"))[-1]
        self.summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

        # What the assertions can use:
        #   self.failed_board          the failed board's entry in summary.json["boards"] (a dict)
        #   self.failed_console_line   the console line for the failed board (a string)
        #   self.summary, self.console, self.exit_code
        self.failed_board = next(b for b in self.summary["boards"] if b["name"] == FAILED_BOARD)
        self.failed_console_line = next(line for line in self.console.splitlines()
                                        if line.strip().startswith(FAILED_BOARD))

        # Setup check only, not the review assertion: the scenario really is a failed 404 board.
        self.assertEqual((self.failed_board["status"], self.failed_board["error"]), ("failed", "HTTP 404"),
                         "setup check: the replay did not reproduce the failed 404 board")

    
    def test_summary_does_not_report_zero_new_for_the_failed_board(self):
        # The board returned 404, so its new-job count is unknown.
        # It must not be reported as zero.
        self.assertIsNone(
            self.failed_board["new_count"],
            "A failed board should have new_count=null, not 0."
        )

        # -------------------------------------------------------------------------------------

    
    def test_console_does_not_print_new_0_for_the_failed_board(self):
        # The console must clearly show that no valid count was observed.
        self.assertIn(
            "new=unknown",
            self.failed_console_line,
            "The console should display new=unknown for a failed board."
        )

        self.assertNotIn(
            "new=0",
            self.failed_console_line,
            "The console must not report zero new jobs for a failed board."
        )

        # -------------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
