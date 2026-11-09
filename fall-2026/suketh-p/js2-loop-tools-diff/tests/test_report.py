"""trace.md restates trace.json; it must not put the run's exit status in the HTTP column
(first seen in the real run 2026-11-08-failure-1, whose trace.md is kept as written)."""

import unittest

from jobwatch import report


class TraceMarkdownTest(unittest.TestCase):
    def test_the_exit_row_shows_the_run_status_as_its_outcome_not_as_an_http_code(self):
        trace = {"run_id": "R1", "status": "incomplete", "events": [
            {"seq": 1, "at": "t", "event": "request", "board": "greenhouse/anthropic", "status": 200,
             "elapsed_s": 0.5, "bytes": 10, "outcome": "usable", "jobs": 1, "raw": "raw/a.gz", "reason": None},
            {"seq": 2, "at": "t", "event": "exit", "status": "incomplete", "reason": "why"}]}
        rows = [line for line in report.trace_md(trace).splitlines() if line.startswith("| ")]
        request_cells = [c.strip() for c in rows[-2].split("|")]
        exit_cells = [c.strip() for c in rows[-1].split("|")]
        self.assertEqual((request_cells[5], request_cells[8]), ("200", "usable"))
        self.assertEqual((exit_cells[3], exit_cells[5], exit_cells[8]), ("exit", "—", "incomplete"))


if __name__ == "__main__":
    unittest.main()
