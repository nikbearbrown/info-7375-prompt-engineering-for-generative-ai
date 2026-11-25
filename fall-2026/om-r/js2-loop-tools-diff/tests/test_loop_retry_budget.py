"""Retry-then-budget-hit (FRICTIONAL.md entry 1).

A board's request fails with a transient error (timeout or 503), so the loop
retries it, and the request budget runs out during the retries. The requests
that were made must be attributed to that board: it is `interrupted`, not
"never attempted" and not `ok`, its state file is untouched, and the run
exits `budget-exhausted`.

Request counts come from the fake fetcher's own call log, not from the
loop's report. All responses are CONSTRUCTED fixtures (tests/fakes.py).
"""
import shutil
import socket
import tempfile
import unittest
from pathlib import Path

from agent import loop
from tests.fakes import FakeFetch, greenhouse_body, http_error, lever_body

BOARDS = ["gitlab", "stripe", "palantir"]
GITLAB_URL = "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true"


class RetryThenBudgetHit(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="js2_retry_budget_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        # A first, healthy run gives gitlab an existing state file to protect.
        baseline = loop.run(["gitlab"], root=self.root, approved_new_boards={"gitlab"},
                            fetch=FakeFetch({"/boards/gitlab/": greenhouse_body(1, 2)}),
                            sleep=lambda s: None)
        self.assertEqual(baseline["exit"], "finished")
        self.state_file = self.root / "state" / "gitlab_seen.json"
        self.state_before = self.state_file.read_bytes()

    def _check(self, transient_error):
        fetch = FakeFetch({
            "/boards/gitlab/": [transient_error, transient_error, greenhouse_body(1, 2, 3)],
            "/boards/stripe/": greenhouse_body(4),
            "/postings/palantir": lever_body("a"),
        })
        sleeps = []
        report = loop.run(BOARDS, root=self.root, fetch=fetch, budgets={"max_requests": 2},
                          approved_new_boards=set(BOARDS), sleep=sleeps.append)

        # Ground truth: the first try and one retry were really made, both
        # for gitlab, and nothing else was requested.
        self.assertEqual(fetch.calls, [GITLAB_URL, GITLAB_URL])
        self.assertEqual(sleeps, [loop.BACKOFF_S, loop.BACKOFF_S])

        gitlab = report["boards"].get("gitlab")
        self.assertIsNotNone(gitlab, "gitlab made 2 requests but is missing from the report's boards")
        self.assertEqual(gitlab["board_status"], "interrupted")
        self.assertIn("2 request(s)", gitlab["error"])
        self.assertEqual(gitlab["new"], [])
        self.assertNotIn("gitlab", report["not_attempted"])
        self.assertEqual(report["not_attempted"], ["stripe", "palantir"])

        self.assertEqual(report["exit"], "budget-exhausted")
        self.assertEqual(report["budget_hit"], {"budget": "requests", "limit": 2})
        self.assertEqual(report["requests_made"], 2)

        self.assertEqual(self.state_file.read_bytes(), self.state_before, "gitlab state changed")
        self.assertFalse((self.root / "state" / "stripe_seen.json").exists())

        lines = [l for l in loop.format_report(report).splitlines() if l.strip().startswith("gitlab")]
        self.assertEqual(len(lines), 1)
        self.assertIn("INTERRUPTED", lines[0])

    def test_timeout_then_budget_hit_during_retry_is_interrupted(self):
        self._check(socket.timeout("timed out"))

    def test_503_then_budget_hit_during_retry_is_interrupted(self):
        self._check(http_error(GITLAB_URL, 503, "Service Unavailable"))


if __name__ == "__main__":
    unittest.main()
