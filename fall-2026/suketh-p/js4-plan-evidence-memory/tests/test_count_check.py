"""The count check: the Board count claim, and the Capture -> watcher edge, in PLAN.md v0.2.

PLAN.md v0.2: "The count checker will decode the saved raw responses with standard-library code
independent of the watchers, ATS parser, and summary generator. The count fixture will contain
exactly 42 unique keys, numbered 1 through 42. I'll first check that the recount returns 42. I'll
then put 99 in the summary and require rejection before publication." Its evidence matrix: "Compare
the independently counted raw keys with the trace and displayed summary."

The checker is checks/independent_check.py, the plan's "separate checker". These tests run it the
way a TA would, in isolated mode (python -I), where it cannot import jobwatch even by accident. The
folders in fixtures/ are constructed (FIXTURE), not board responses. Claude Code wrote these tests
on 2026-11-25, before changing the checker. Rejection *before publication* is tested again once the
run's publish step exists: this file tests the check that gate will use."""

import ast
import gzip
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "checks" / "independent_check.py"
FIXTURES = ROOT / "fixtures"
CLEAN = FIXTURES / "count-42"
PLANTED = FIXTURES / "count-42-planted-99"
FIXTURE_RAW = "raw/greenhouse-fixture-count-42.body.gz"


def run_check(run_dir, *state_args):
    done = subprocess.run([sys.executable, "-I", str(CHECKER), str(run_dir), *state_args],
                          capture_output=True, text=True, cwd=run_dir)
    return done.returncode, done.stdout + done.stderr


def recount_line(board, jobs):
    return re.compile(rf"^  {re.escape(board)}: saved body is HTTP 200, \d+ bytes, {jobs} jobs$", re.M)


def gh(*ids):
    return json.dumps({"jobs": [{"id": i, "title": "t"} for i in ids]}).encode()


def ashby(*urls):
    return json.dumps({"apiVersion": "1", "jobs": [{"jobUrl": u, "title": "t"} for u in urls]}).encode()


class IndependenceTest(unittest.TestCase):
    """The review's change: "require the checker to parse the raw bytes with its own code, with no
    imports from the watcher or parser modules"."""

    def imported_modules(self):
        modules = set()
        for node in ast.walk(ast.parse(CHECKER.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0, "a relative import")
                modules.add(node.module.split(".")[0])
        return modules

    def test_the_checker_imports_only_the_standard_library(self):
        modules = self.imported_modules()
        self.assertIn("json", modules)
        self.assertEqual(modules - set(sys.stdlib_module_names), set())

    def test_the_checker_never_imports_jobwatch_or_imports_dynamically(self):
        self.assertNotIn("jobwatch", self.imported_modules())
        text = CHECKER.read_text(encoding="utf-8")
        for needle in ("__import__", "importlib", "exec(", "eval(", "sys.path"):
            self.assertNotIn(needle, text)


class CountFixtureTest(unittest.TestCase):
    """The plan's two fixture checks: the recount is 42, and 99 in the summary is rejected."""

    def test_the_fixture_body_holds_exactly_the_keys_1_to_42(self):
        # Read here with gzip and json, not through the checker.
        data = json.loads(gzip.decompress((CLEAN / FIXTURE_RAW).read_bytes()))
        self.assertEqual([job["id"] for job in data["jobs"]], list(range(1, 43)))

    def test_the_fixture_trace_records_the_body_hash_and_42(self):
        trace = json.loads((CLEAN / "trace.json").read_text(encoding="utf-8"))
        [request] = [e for e in trace["events"] if e["event"] == "request"]
        body = gzip.decompress((CLEAN / request["raw"]).read_bytes())
        self.assertEqual(request["sha256"], hashlib.sha256(body).hexdigest())
        self.assertEqual(request["jobs"], 42)

    def test_the_recount_of_the_fixture_is_42_and_the_check_passes(self):
        code, out = run_check(CLEAN)
        self.assertEqual(code, 0, out)
        self.assertRegex(out, recount_line("greenhouse/fixture-count-42", 42))
        self.assertIn("PASS", out)

    def test_99_in_the_summary_is_rejected(self):
        code, out = run_check(PLANTED)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, recount_line("greenhouse/fixture-count-42", 42))
        self.assertIn("FLAG greenhouse/fixture-count-42: results.json reports 99 jobs; its saved response has 42", out)
        self.assertIn("FLAG greenhouse/fixture-count-42: results.md shows 99 jobs; its saved response has 42", out)
        self.assertNotIn("trace.json records", out)  # the trace says 42, as the raw body does
        self.assertNotIn("trace.md shows", out)
        self.assertIn("FAIL", out)

    def test_the_planted_fixture_differs_from_the_clean_one_only_in_the_summary(self):
        for name in ("trace.json", "trace.md"):
            self.assertEqual((CLEAN / name).read_bytes(), (PLANTED / name).read_bytes(), name)
        self.assertEqual(gzip.decompress((CLEAN / FIXTURE_RAW).read_bytes()),
                         gzip.decompress((PLANTED / FIXTURE_RAW).read_bytes()))
        clean, planted = (json.loads((d / "results.json").read_text(encoding="utf-8")) for d in (CLEAN, PLANTED))
        self.assertEqual([b["jobs"] for b in clean["boards"]], [42])
        self.assertEqual([b["jobs"] for b in planted["boards"]], [99])
        for data in (clean, planted):
            del data["label"], data["boards"][0]["jobs"]
        self.assertEqual(clean, planted)

    def test_every_fixture_file_is_labelled(self):
        for folder in (CLEAN, PLANTED):
            for name in ("trace.json", "results.json"):
                self.assertIn("FIXTURE", json.loads((folder / name).read_text(encoding="utf-8"))["label"])
            for name in ("trace.md", "results.md"):
                self.assertIn("FIXTURE", (folder / name).read_text(encoding="utf-8"))
        self.assertIn("PLANTED ERROR", json.loads((PLANTED / "results.json").read_text(encoding="utf-8"))["label"])

    def test_the_generator_rebuilds_the_committed_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, "-I", str(FIXTURES / "make_count_fixtures.py"), tmp],
                           check=True, capture_output=True)
            for folder in ("count-42", "count-42-planted-99"):
                for name in ("trace.json", "trace.md", "results.json", "results.md"):
                    self.assertEqual((Path(tmp) / folder / name).read_bytes(),
                                     (FIXTURES / folder / name).read_bytes(), f"{folder}/{name}")
                self.assertEqual(gzip.decompress((Path(tmp) / folder / FIXTURE_RAW).read_bytes()),
                                 gzip.decompress((FIXTURES / folder / FIXTURE_RAW).read_bytes()))


class CountOnlyModeTest(unittest.TestCase):
    """Run folders built by hand, one board each: the raw body, and the count each record claims."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.run_dir = Path(self._tmp.name) / "runs" / "R1"
        (self.run_dir / "raw").mkdir(parents=True)

    def write_run(self, board, body, trace_jobs, results_jobs, results_md_jobs=None, trace_md_jobs=None):
        raw = f"raw/{board.replace('/', '-')}.body.gz"
        (self.run_dir / raw).write_bytes(gzip.compress(body, mtime=0))
        event = {"seq": 1, "event": "request", "board": board, "status": 200, "raw": raw,
                 "sha256": hashlib.sha256(body).hexdigest(), "jobs": trace_jobs}
        (self.run_dir / "trace.json").write_text(json.dumps({"events": [event]}))
        row = {"board": board, "role": "normal", "outcome": "usable", "jobs": results_jobs,
               "baseline": True, "new_keys": []}
        (self.run_dir / "results.json").write_text(json.dumps({"status": "incomplete", "state_advanced": False,
                                                               "boards": [row]}))
        if results_md_jobs is not None:
            (self.run_dir / "results.md").write_text(
                "| Board | Role | Outcome | Jobs | Baseline | New | Reason |\n|---|---|---|---:|---|---:|---|\n"
                f"| {board} | normal | usable | {results_md_jobs} | True | 0 | — |\n", encoding="utf-8")
        if trace_md_jobs is not None:
            (self.run_dir / "trace.md").write_text(
                "| # | At | Event | Board | HTTP | Elapsed s | Bytes | Outcome | Jobs | Raw file | Reason |\n"
                "|---:|---|---|---|---:|---:|---:|---|---:|---|---|\n"
                f"| 1 | t | request | {board} | 200 | 0.1 | {len(body)} | usable | {trace_md_jobs} | {raw} | — |\n"
                "| 2 | t | exit | — | — | — | — | incomplete | — | — | done |\n", encoding="utf-8")

    def test_a_consistent_run_passes_and_says_the_state_was_not_checked(self):
        self.write_run("greenhouse/anthropic", gh(1, 2, 3), 3, 3, results_md_jobs=3, trace_md_jobs=3)
        code, out = run_check(self.run_dir)
        self.assertEqual(code, 0, out)
        self.assertRegex(out, recount_line("greenhouse/anthropic", 3))
        self.assertIn("state not checked", out)
        self.assertIn("PASS", out)

    def test_a_trace_count_that_differs_from_the_raw_body_is_flagged(self):
        self.write_run("greenhouse/anthropic", gh(1, 2, 3), 4, 3)
        code, out = run_check(self.run_dir)
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG greenhouse/anthropic: trace.json records 4 jobs; its saved response has 3", out)

    def test_a_count_shown_in_results_md_that_differs_is_flagged(self):
        self.write_run("greenhouse/anthropic", gh(1, 2, 3), 3, 3, results_md_jobs=99, trace_md_jobs=3)
        code, out = run_check(self.run_dir)
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG greenhouse/anthropic: results.md shows 99 jobs; its saved response has 3", out)
        self.assertNotIn("results.json reports", out)

    def test_a_count_shown_in_trace_md_that_differs_is_flagged(self):
        self.write_run("greenhouse/anthropic", gh(1, 2, 3), 3, 3, results_md_jobs=3, trace_md_jobs=99)
        code, out = run_check(self.run_dir)
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG greenhouse/anthropic: trace.md shows 99 jobs; its saved response has 3", out)

    def test_a_repeated_key_is_counted_once(self):
        self.write_run("greenhouse/anthropic", gh(1, 2, 2, 3), 3, 3)
        code, out = run_check(self.run_dir)
        self.assertEqual(code, 0, out)
        self.write_run("greenhouse/anthropic", gh(1, 2, 2, 3), 3, 4)
        code, out = run_check(self.run_dir)
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG greenhouse/anthropic: results.json reports 4 jobs; its saved response has 3", out)

    def test_an_ashby_board_is_counted_by_job_url(self):
        self.write_run("ashby/linear", ashby("https://x/1", "https://x/2", "https://x/2"), 2, 2, results_md_jobs=2)
        code, out = run_check(self.run_dir)
        self.assertEqual(code, 0, out)
        self.assertRegex(out, recount_line("ashby/linear", 2))

    def test_giving_only_one_state_file_is_a_usage_error(self):
        self.write_run("greenhouse/anthropic", gh(1, 2, 3), 3, 3)
        code, out = run_check(self.run_dir, "--state-before", "none")
        self.assertEqual(code, 2, out)


class RealCapturesTest(unittest.TestCase):
    """The two saved captures the replays use. These are real board responses, not fixtures."""

    def check_capture(self, run_id, expected):
        code, out = run_check(ROOT / "runs" / run_id)
        self.assertEqual(code, 0, out)
        for board, jobs in expected.items():
            self.assertRegex(out, recount_line(board, jobs))
        self.assertIn("state not checked", out)

    def test_the_nov_8_capture_passes_the_count_check(self):
        self.check_capture("2026-11-08-normal-1",
                           {"greenhouse/anthropic": 675, "greenhouse/databricks": 922, "ashby/linear": 32})

    def test_the_nov_24_capture_passes_the_count_check(self):
        self.check_capture("2026-11-24-js3-corpus",
                           {"greenhouse/anthropic": 631, "greenhouse/databricks": 890, "ashby/linear": 30})


if __name__ == "__main__":
    unittest.main()
