"""The watch: allow-listed host, baseline reports 0 new, a second run reports only the added id."""
import io
import tempfile
import unittest
from pathlib import Path

from tests import helpers


class HostAllowList(helpers.ContractTest):
    modules = ("agent.watch",)

    def test_other_hosts_are_refused_before_any_network_call(self):
        calls = []

        def spy_opener(*args, **kwargs):
            calls.append(args)
            return io.BytesIO(b"{}")

        for url in (
            "https://api.lever.co/v0/postings/faire?mode=json",
            "https://boards-api.greenhouse.io.evil.example/v1/boards/faire/jobs",
            "https://boards-api.greenhouse.io@evil.example/v1/boards/faire/jobs",
        ):
            with self.subTest(url=url), self.assertRaises(self.watch.RefusedHost):
                self.watch.fetch(url, opener=spy_opener)
        self.assertEqual(calls, [], "no request may be made to a refused host")

    def test_allowed_host_is_fetched(self):
        calls = []

        def spy_opener(*args, **kwargs):
            calls.append(args)
            return io.BytesIO(b'{"jobs": []}')

        body = self.watch.fetch("https://boards-api.greenhouse.io/v1/boards/faire/jobs?content=true",
                                opener=spy_opener)
        self.assertEqual(body, b'{"jobs": []}')
        self.assertEqual(len(calls), 1)


class NewSinceLastRun(helpers.ContractTest):
    modules = ("agent.run",)

    def run_agent(self, board, tmp):
        return self.run.main(["--replay", str(board),
                              "--state", str(Path(tmp) / "state" / "seen_ids.json"),
                              "--runs", str(Path(tmp) / "runs")])

    def test_baseline_then_one_added_id(self):
        jobs = helpers.postings()
        with tempfile.TemporaryDirectory() as tmp:
            first = helpers.write_board(Path(tmp) / "board1.json", jobs[:-1])
            second = helpers.write_board(Path(tmp) / "board2.json", jobs)

            baseline = self.run_agent(first, tmp)
            self.assertTrue(baseline["baseline"])
            self.assertEqual(baseline["new_ids"], [])

            report = self.run_agent(second, tmp)
            self.assertFalse(report["baseline"])
            self.assertEqual(report["new_ids"], [jobs[-1]["id"]])
            self.assertEqual([v["posting_id"] for v in report["rule_verdicts"]], [jobs[-1]["id"]])


if __name__ == "__main__":
    unittest.main()
