"""The independent check (GATE.md section 7) catches a finished run that is wrong.

The wrong run here is made by wrong version W5 on constructed responses: the
empty board is treated as a good board with no new jobs.
"""

import ast
import gzip
import unittest
from pathlib import Path
from unittest import mock

import check_run
from agent import loop
from tests.helpers import (ASHBY, LINEAR, THREE, FakeClock, FakeNet, ashby_body, ashby_job, gh_body, gh_job, GH,
                           LEVER, lever_body, lever_job, make_root, ok, run_loop)


def first_run(root, clock):
    return run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1)))],
                                          LEVER % "palantir": [ok(lever_body(lever_job("a")))],
                                          ASHBY % "linear": [ok(ashby_body(ashby_job("x"), ashby_job("y")))]}),
                    clock, run_id="run-1")


def second_run_with_linear_empty(root, clock):
    return run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1), gh_job(2)))],
                                          LEVER % "palantir": [ok(lever_body(lever_job("a")))],
                                          ASHBY % "linear": [ok(ashby_body())]}),
                    clock, run_id="run-2")


REAL_CLASSIFY = loop.classify


def wrong_classify(system, http_status, body):
    """W5: an empty board is a good board with nothing new."""
    status, reason, postings = REAL_CLASSIFY(system, http_status, body)
    if (status, reason) == ("suspect", "empty"):
        return "ok", None, []
    return status, reason, postings


def failed(checks):
    return sorted(c.name for c in checks if not c.passed)


class IndependentCheck(unittest.TestCase):
    def test_good_runs_pass_every_check(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = first_run(root, clock)
        self.assertEqual(failed(check_run.check(root / record["files"]["record"])), [])
        record = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1), gh_job(2)))],
                                                LEVER % "palantir": [ok(lever_body(lever_job("a")))],
                                                ASHBY % "linear": [ok(ashby_body(ashby_job("x")))]}),
                          clock, run_id="run-2")
        self.assertEqual(record["exit"], "finished")
        self.assertEqual(failed(check_run.check(root / record["files"]["record"])), [])

    def test_finished_wrong_answer_is_caught(self):
        root, clock = make_root(self, THREE), FakeClock()
        first_run(root, clock)
        with mock.patch.object(loop, "classify", wrong_classify):
            record = second_run_with_linear_empty(root, clock)
        linear = next(b for b in record["boards"] if b["key"] == "ashby/linear")
        # The loop's own report: finished, Linear fine, nothing new.
        self.assertEqual(record["exit"], "finished")
        self.assertEqual((linear["status"], linear["counts"]["postings"], linear["counts"]["new"]), ("ok", 0, 0))
        # The check does not believe it.
        self.assertEqual(failed(check_run.check(root / record["files"]["record"])),
                         ["finished_needs_postings_on_every_board", "no_drop_to_zero"])

    def test_the_real_agent_on_the_same_responses_passes(self):
        root, clock = make_root(self, THREE), FakeClock()
        first_run(root, clock)
        record = second_run_with_linear_empty(root, clock)
        self.assertEqual(record["exit"], "incomplete")
        self.assertEqual(failed(check_run.check(root / record["files"]["record"])), [])

    def test_tampered_raw_response_is_caught(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = first_run(root, clock)
        raw = root / record["boards"][0]["attempts"][0]["raw_file"]
        raw.chmod(0o644)
        raw.write_bytes(gzip.compress(gh_body(gh_job(1), gh_job(99))))
        self.assertIn("raw_sha256", failed(check_run.check(root / record["files"]["record"])))

    def test_wrong_new_ids_are_caught(self):
        root, clock = make_root(self, THREE), FakeClock()
        first_run(root, clock)
        record = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1), gh_job(2)))],
                                                LEVER % "palantir": [ok(lever_body(lever_job("a")))],
                                                ASHBY % "linear": [ok(ashby_body(ashby_job("x")))]}),
                          clock, run_id="run-2")
        path = root / record["files"]["record"]
        import json
        data = json.loads(path.read_text())
        data["boards"][0]["new_postings"] = []
        data["boards"][0]["counts"]["new"] = 0
        path.write_text(json.dumps(data))
        self.assertIn("new_ids_recomputed", failed(check_run.check(path)))

    def test_the_check_does_not_import_the_agent(self):
        tree = ast.parse(Path(check_run.__file__).read_text(encoding="utf-8"))
        modules = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        modules |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
        self.assertFalse(any(m == "agent" or m.startswith("agent.") or m == "tests" for m in modules), modules)


if __name__ == "__main__":
    unittest.main()
