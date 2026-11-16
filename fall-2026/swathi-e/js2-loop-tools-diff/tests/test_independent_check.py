"""Tests for the independent check, written before independent_check.py exists.

C1-C8 are the tests Claude Code proposed on 2026-11-05 and Swathi approved,
with her decisions: flag only drops to zero (no partial-drop threshold) and no
meta.total cross-check. Every docstring names the GATE.md item it checks.
Responses built in this file are SIMULATED; C8 reads one real, committed raw
response (the Nov 5 live Databricks run), read-only. Written by Claude Code.
Every test runs inside no_network(): socket connections fail.
"""
import ast
from contextlib import contextmanager
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import independent_check  # noqa: E402  (does not exist until the check is written)

REAL_NOV5_DATABRICKS = HERE / "runs" / "2026-11-05T23-11-48-228373-0500" / "001-databricks-request.json"
EMPTY = "EMPTY, UNVERIFIED"
UNREADABLE = "UNREADABLE"
DROP = "DROP TO ZERO"


@contextmanager
def no_network():
    def refuse(*args, **kwargs):
        raise AssertionError("a network connection was attempted")
    with patch.object(socket, "create_connection", refuse), patch.object(socket.socket, "connect", refuse):
        yield


def gh_body(n):
    """SIMULATED Greenhouse body with n postings."""
    return json.dumps({"jobs": [{"id": i, "title": f"Job {i}", "location": {"name": "Remote - US"}}
                                for i in range(n)], "meta": {"total": n}}).encode()


def ashby_body(n):
    """SIMULATED Ashby body with n postings."""
    return json.dumps({"apiVersion": "1", "jobs": [{"id": f"u-{i}", "title": f"Job {i}", "location": "NYC",
                                                    "isListed": True} for i in range(n)]}).encode()


class CheckCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.count = 0

    def tearDown(self):
        self.tmp.cleanup()

    def raw(self, body):
        self.count += 1
        path = self.dir / f"{self.count:02d}-SIMULATED.json"
        path.write_bytes(body)
        return path

    def check(self, *bodies):
        with no_network():
            return independent_check.check_files([self.raw(b) for b in bodies])

    def run_main(self, *bodies):
        out = io.StringIO()
        with no_network():
            code = independent_check.main([str(self.raw(b)) for b in bodies], out=out)
        return code, out.getvalue()


class Flags(CheckCase):
    def test_C1_empty_job_list_is_flagged(self):
        """C1, GATE.md wrong version 1 (an empty board reported as "0 new"). SIMULATED: a body
        with {"jobs": []} is flagged EMPTY, UNVERIFIED, with 0 postings."""
        [result] = self.check(b'{"jobs": [], "meta": {"total": 0}}')
        self.assertEqual(result["postings"], 0)
        self.assertIn(EMPTY, result["flags"])

    def test_C2_no_body_is_flagged(self):
        """C2, GATE.md error policy (empty response: no body). SIMULATED: a file with no content,
        or only whitespace, is flagged EMPTY, UNVERIFIED."""
        for body in (b"", b"  \n"):
            with self.subTest(body=body):
                [result] = self.check(body)
                self.assertIn(EMPTY, result["flags"])
                self.assertNotIn(UNREADABLE, result["flags"])

    def test_C3_non_empty_bodies_are_not_flagged(self):
        """C3, GATE.md Exits (finished needs a valid, non-empty response). SIMULATED: a Greenhouse
        body with 2 postings and an Ashby body with 3 are not flagged; counts and sha256 reported."""
        gh, ashby = self.check(gh_body(2)), self.check(ashby_body(3))
        self.assertEqual((gh[0]["postings"], gh[0]["flags"]), (2, []))
        self.assertEqual((ashby[0]["postings"], ashby[0]["flags"]), (3, []))
        self.assertEqual(len(gh[0]["sha256"]), 64)

    def test_C4_drop_to_zero_is_flagged_with_both_counts(self):
        """C4, GATE.md wrong version 1 (the finished wrong answer). SIMULATED: an earlier response
        with 3 postings, then one with 0: the later one is flagged DROP TO ZERO as well as EMPTY,
        and the output gives both counts. Only drops to zero are flagged (Swathi, 2026-11-05)."""
        earlier, later = self.check(gh_body(3), gh_body(0))
        self.assertEqual(earlier["flags"], [])
        self.assertIn(EMPTY, later["flags"])
        self.assertIn(DROP, later["flags"])
        _, output = self.run_main(gh_body(3), gh_body(0))
        self.assertIn("3 -> 0", output)
        partial = self.check(gh_body(3), gh_body(1))
        self.assertEqual(partial[1]["flags"], [])

    def test_C5_unreadable_bodies_are_flagged(self):
        """C5, GATE.md Revision (invalid JSON or a valid response of the wrong shape is failed).
        SIMULATED: invalid JSON, {"jobs": "x"}, a top-level list, and the Greenhouse 404 body shape
        are each flagged UNREADABLE, with no posting count."""
        for body in (b"<html>not json</html>", b'{"jobs": "x"}', b"[]",
                     b'{"status":404,"error":"Job not found"}'):
            with self.subTest(body=body):
                [result] = self.check(body)
                self.assertEqual(result["flags"], [UNREADABLE])
                self.assertIsNone(result["postings"])

    def test_C6_exit_code(self):
        """C6, GATE.md Error policy (escalate: anything not finished is reported). SIMULATED: main
        returns 1 when any file is flagged and 0 when none is."""
        self.assertEqual(self.run_main(gh_body(2), ashby_body(1))[0], 0)
        self.assertEqual(self.run_main(gh_body(2), gh_body(0))[0], 1)
        self.assertEqual(self.run_main(b"not json")[0], 1)


class Independence(unittest.TestCase):
    def test_C7_imports_nothing_from_the_agent(self):
        """C7, independence of the check (JS2 brief: a check that does not trust the agent). An AST
        scan of independent_check.py: it imports only json, hashlib, sys and pathlib; none of the
        agent's modules and no network module."""
        tree = ast.parse((HERE / "independent_check.py").read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertLessEqual(imported, {"json", "hashlib", "sys", "pathlib"})
        self.assertFalse(imported & {"watch", "loop", "parsers", "rule", "policy", "persona",
                                     "urllib", "socket", "http"})

    def test_C8_real_nov5_databricks_response_is_not_flagged(self):
        """C8, GATE.md Evidence (raw responses are saved). The REAL committed Nov 5 live Databricks
        response, read-only: not flagged, 923 postings."""
        with no_network():
            [result] = independent_check.check_files([REAL_NOV5_DATABRICKS])
        self.assertEqual(result["postings"], 923)
        self.assertEqual(result["flags"], [])


if __name__ == "__main__":
    unittest.main()
