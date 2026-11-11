import json
import os
import unittest
from unittest import mock

from js2 import independent_check, loop, wrong_answer_demo
from tests.helpers import FakeResponse, SandboxTestCase, greenhouse_body, http_error, lever_body

URLOPEN = "js2.fetch.urllib.request.urlopen"


class CheckTraceTest(SandboxTestCase):
    def setUp(self):
        super().setUp()
        self.raw_dir = os.path.join(self.output, "raw")
        os.makedirs(self.raw_dir)

    def write_raw(self, name, body):
        path = os.path.join(self.raw_dir, name)
        with open(path, "wb") as f:
            f.write(body)
        return path

    def write_trace(self, status, boards):
        path = os.path.join(self.output, "trace.json")
        with open(path, "w") as f:
            json.dump({"status": status, "boards": boards}, f)
        return path

    def ok_board(self, name, raw_path, ids, ats="greenhouse"):
        return {"board": name, "ats": ats, "outcome": "ok", "raw_path": raw_path,
                "posting_count": len(ids), "posting_ids": ids}

    def types(self, trace_path):
        return sorted(p["type"] for p in independent_check.check_trace(trace_path, self.raw_dir))

    def test_consistent_trace_has_no_discrepancies(self):
        gh = self.write_raw("a-greenhouse-x.json", greenhouse_body(1, 2))
        lv = self.write_raw("a-lever-y.json", lever_body("s1"))
        trace = self.write_trace("finished", [self.ok_board("x", gh, ["1", "2"]),
                                              self.ok_board("y", lv, ["s1"], ats="lever")])
        self.assertEqual(self.types(trace), [])

    def test_finished_with_empty_raw_file(self):
        empty = self.write_raw("a-greenhouse-x.json", b"")
        trace = self.write_trace("finished", [self.ok_board("x", empty, [])])
        self.assertIn("finished_with_empty_or_missing_raw", self.types(trace))

    def test_finished_with_missing_raw_file(self):
        trace = self.write_trace("finished", [self.ok_board("x", "/gone/a-greenhouse-x.json", ["1"])])
        self.assertIn("finished_with_empty_or_missing_raw", self.types(trace))

    def test_zero_postings_recorded_success(self):
        raw = self.write_raw("a-greenhouse-x.json", b'{"jobs": []}')
        trace = self.write_trace("incomplete", [self.ok_board("x", raw, [])])
        self.assertEqual(self.types(trace), ["zero_postings_recorded_success"])

    def test_raw_absent_but_success_claimed(self):
        trace = self.write_trace("incomplete", [self.ok_board("x", "/gone/a-greenhouse-x.json", ["1"]),
                                                self.ok_board("y", None, ["1"])])
        self.assertEqual(self.types(trace), ["raw_absent_claimed_success"] * 2)

    def test_invalid_raw_recorded_success(self):
        raw = self.write_raw("a-greenhouse-x.json", b"<html>not json</html>")
        trace = self.write_trace("incomplete", [self.ok_board("x", raw, ["1"])])
        self.assertEqual(self.types(trace), ["invalid_raw_recorded_success"])

    def test_posting_ids_mismatch(self):
        raw = self.write_raw("a-greenhouse-x.json", greenhouse_body(1, 2))
        trace = self.write_trace("incomplete", [self.ok_board("x", raw, ["1", "3"])])
        self.assertEqual(self.types(trace), ["posting_ids_mismatch"])

    def test_finished_with_failed_board(self):
        trace = self.write_trace("finished", [{"board": "x", "ats": "greenhouse", "outcome": "failed"}])
        self.assertEqual(self.types(trace), ["finished_with_failed_board"])

    def test_failed_board_in_incomplete_run_is_not_a_discrepancy(self):
        trace = self.write_trace("incomplete", [{"board": "x", "ats": "greenhouse", "outcome": "failed"}])
        self.assertEqual(self.types(trace), [])


class WrongDemoTest(SandboxTestCase):
    def test_demo_is_finished_but_wrong_and_the_check_catches_it(self):
        trace = wrong_answer_demo.run_wrong_demo(self.output)
        self.assertEqual(trace["status"], "finished")
        self.assertEqual(trace["exit_status"], "finished")
        self.assertEqual(trace["label"], "WRONG-DEMO")
        self.assertIn("deliberately finished-but-wrong", trace["notes"])
        self.assertTrue(trace["trace_path"].endswith("-WRONG-DEMO.json"))
        self.assertEqual(trace["boards"][1]["posting_count"], 0)

        problems = independent_check.check_trace(trace["trace_path"], os.path.join(self.output, "raw"))
        self.assertEqual(sorted((p["board"], p["type"]) for p in problems), [
            ("demo-empty", "finished_with_empty_or_missing_raw"),
            ("demo-empty", "zero_postings_recorded_success"),
        ])

    def test_same_boards_with_the_real_parser_are_incomplete(self):
        trace = loop.run(boards=wrong_answer_demo.DEMO_BOARDS, write_trace=False,
                         fetchers={"greenhouse": lambda token, timeout: {
                             "status_code": 200, "raw_path": None, "raw_write_decision": True,
                             "data": json.loads(wrong_answer_demo.DEMO_BODIES[token])}})
        self.assertEqual(trace["status"], "incomplete")

    def test_demo_trace_path_is_absolute_for_relative_output_dir(self):
        cwd = os.getcwd()
        os.chdir(self.tmp)
        self.addCleanup(os.chdir, cwd)
        trace = wrong_answer_demo.run_wrong_demo("output")
        self.assertTrue(os.path.isabs(trace["trace_path"]))
        self.assertTrue(os.path.isfile(trace["trace_path"]))

    def test_demo_writes_nothing_outside_allowed_output(self):
        outside = os.path.join(self.tmp, "elsewhere")
        trace = wrong_answer_demo.run_wrong_demo(outside)
        self.assertIsNone(trace["trace_path"])
        self.assertFalse(os.path.exists(outside))


class RealRunCheckTest(SandboxTestCase):
    def urlopen(self, req, timeout):
        if "invalid-board-xyz" in req.full_url:
            raise http_error(req.full_url, 404)
        if "api.lever.co" in req.full_url:
            return FakeResponse(lever_body("s1", "s2"))
        return FakeResponse(greenhouse_body(1, 2, 3))

    def test_real_loop_trace_passes_the_check(self):
        with mock.patch(URLOPEN, side_effect=self.urlopen):
            trace = loop.run()
        self.assertEqual(trace["status"], "incomplete")
        self.assertEqual(independent_check.check_trace(trace["trace_path"], os.path.join(self.output, "raw")), [])


if __name__ == "__main__":
    unittest.main()
