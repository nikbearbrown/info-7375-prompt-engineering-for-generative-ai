"""Pre-patch regression cases using simulated responses and state approval."""

import gzip

from tests import test_loop as loop_cases
from tests.fakes import (
    ANTHROPIC_URL,
    DATABRICKS_URL,
    LINEAR_URL,
    NORMAL,
    Reply,
    gh_job,
    greenhouse,
)


class EmptyBoardReviewTest(loop_cases.LoopCase):
    def assert_empty_board_unverified(self, result, board_name, body):
        run_id = result["run_id"]
        trace = self.project.trace(run_id)
        request = next(
            event for event in trace["events"]
            if event["event"] == "request" and event["board"] == board_name
        )
        self.assertEqual(request["status"], 200)
        raw_path = self.project.run_dir(run_id) / request["raw"]
        self.assertEqual(gzip.decompress(raw_path.read_bytes()), body)

        board = loop_cases.by_board(result)[board_name]
        self.assertEqual(board["outcome"], "unverified")
        self.assertIn("empty jobs list", board["reason"].lower())
        self.assertIsNone(board["jobs"])
        self.assertIsNone(board["new_keys"])
        self.assertIsNone(board["new_postings"])
        self.assertEqual(result["status"], "incomplete")
        self.assertFalse(result["state_advanced"])

    def test_empty_greenhouse_board_does_not_create_a_baseline(self):
        body = b'{"jobs":[]}'
        script = loop_cases.normal_script({ANTHROPIC_URL: Reply(200, body)})
        result = self.run_loop("R1", NORMAL, script)

        self.assert_empty_board_unverified(
            result, "greenhouse/anthropic", body)
        self.assertEqual(self.transport.urls(), [
                         ANTHROPIC_URL, DATABRICKS_URL, LINEAR_URL])
        boards = loop_cases.by_board(result)
        for board_name in ("greenhouse/databricks", "ashby/linear"):
            self.assertEqual(boards[board_name]["outcome"], "usable")
            self.assertTrue(boards[board_name]["provisional"])
        self.assertIsNone(self.project.state_bytes())

    def test_empty_ashby_board_leaves_saved_state_byte_identical(self):
        self.baseline("R1")
        before = self.project.state_bytes()
        body = b'{"apiVersion":"1","jobs":[]}'
        script = loop_cases.normal_script({
            DATABRICKS_URL: Reply(body=greenhouse(gh_job(201), gh_job(202))),
            LINEAR_URL: Reply(200, body),
        })
        result = self.run_loop("R2", NORMAL, script)

        self.assert_empty_board_unverified(result, "ashby/linear", body)
        databricks = loop_cases.by_board(result)["greenhouse/databricks"]
        self.assertEqual(databricks["outcome"], "usable")
        self.assertEqual(databricks["new_keys"], ["202"])
        self.assertTrue(databricks["provisional"])
        self.assertEqual(self.project.state_bytes(), before)

    def test_all_empty_boards_end_in_error_without_creating_state(self):
        greenhouse_body = b'{"jobs":[]}'
        ashby_body = b'{"apiVersion":"1","jobs":[]}'
        script = {
            ANTHROPIC_URL: Reply(200, greenhouse_body),
            DATABRICKS_URL: Reply(200, greenhouse_body),
            LINEAR_URL: Reply(200, ashby_body),
        }
        result = self.run_loop("R1", NORMAL, script)

        self.assertEqual(
            self.transport.urls(), [ANTHROPIC_URL, DATABRICKS_URL, LINEAR_URL]
        )
        self.assertEqual(result["status"], "error")
        self.assertFalse(result["state_advanced"])
        self.assertIsNone(self.project.state_bytes())
        for board in result["boards"]:
            with self.subTest(board=board["board"]):
                self.assertEqual(board["outcome"], "unverified")

    def test_nonempty_boards_with_no_new_postings_still_finish(self):
        self.baseline("R1")
        result = self.run_loop("R2", NORMAL, loop_cases.normal_script())

        self.assertEqual(result["status"], "finished")
        self.assertTrue(result["state_advanced"])
        for board in result["boards"]:
            with self.subTest(board=board["board"]):
                self.assertEqual(board["outcome"], "usable")
                self.assertGreater(board["jobs"], 0)
                self.assertFalse(board["baseline"])
                self.assertEqual(board["new_keys"], [])
