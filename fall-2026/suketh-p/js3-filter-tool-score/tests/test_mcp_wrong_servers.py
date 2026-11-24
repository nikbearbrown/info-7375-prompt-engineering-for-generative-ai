"""Chapter 8's three constructed wrong servers, each run against the check that must catch it.

1. Ready on initialize (skips the notification): the protocol ledger, the transition table.
2. A lookup that appends to a log file on every call: passes the protocol ledger, fails the
   capability check (the audit-hooked harness run).
3. A read-only lookup whose value disagrees with the declared source: fails the evidence check.
All three are CONSTRUCTED and never connected to Claude."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jobwatch import mcp_client, mcp_server

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = json.loads((ROOT / "transcripts" / "scripts" / "jobwatch-harness.json").read_text(encoding="utf-8"))


def run_named(test_name):
    suite = unittest.defaultTestLoader.loadTestsFromName(test_name)
    result = unittest.TestResult()
    suite.run(result)
    return len(result.failures) + len(result.errors), result.testsRun


_real_handle = mcp_server.Server.handle
_real_lookup = mcp_server.Server._lookup


def ready_on_initialize(self, message):
    response = _real_handle(self, message)
    if isinstance(message, dict) and message.get("method") == "initialize" and response and "result" in response:
        self.ready = True
    return response


def lookup_one_point_high(self, board, key):
    record = _real_lookup(self, board, key)
    return None if record is None else dict(record, score=record["score"] + 1)


class WrongServersTest(unittest.TestCase):
    def test_1_ready_on_initialize_fails_the_transition_table(self):
        with mock.patch.object(mcp_server.Server, "handle", ready_on_initialize):
            broken, ran = run_named("tests.test_mcp_server.LifecycleTableTest.test_rows")
        self.assertEqual(ran, 1)
        self.assertGreaterEqual(broken, 1)  # each failing row is its own subtest
        self.assertEqual(run_named("tests.test_mcp_server.LifecycleTableTest.test_rows"), (0, 1))

    def test_3_a_wrong_value_fails_the_evidence_check(self):
        with mock.patch.object(mcp_server.Server, "_lookup", lookup_one_point_high):
            broken, ran = run_named("tests.test_mcp_server.ToolTest.test_the_value_matches_the_declared_source")
        self.assertEqual((broken, ran), (1, 1))

    def test_2_a_logging_lookup_fails_the_capability_check_and_the_real_server_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["WRONG_SERVER_LOG"] = os.path.join(tmp, "calls.log")
            try:
                reports = {}
                for name, command in (("real", ["python3", "-m", "jobwatch.mcp_server"]),
                                      ("wrong", ["python3", "-m", "tests.mcp_wrong_server_writes"])):
                    log = Path(tmp) / f"{name}.jsonl"
                    with mock.patch.object(mcp_client, "allowed_log", lambda p: Path(p)):
                        code = mcp_client.run(command, SCRIPT, log, timeout=20)
                    self.assertEqual(code, 0)
                    reports[name] = mcp_client.capability_report(log)
            finally:
                del os.environ["WRONG_SERVER_LOG"]
        self.assertEqual(reports["real"]["writes"], [])
        self.assertEqual((reports["real"]["network"], reports["real"]["processes"]), ([], []))
        self.assertTrue(any(p.endswith("calls.log") for p in reports["wrong"]["writes"]))


if __name__ == "__main__":
    unittest.main()
