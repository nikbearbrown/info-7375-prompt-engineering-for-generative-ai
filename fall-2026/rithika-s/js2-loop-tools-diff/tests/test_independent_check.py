"""The independent checker: PASS on a clean run, FLAG on each GATE case."""

import ast
import io
import json
import tempfile
import unittest
from pathlib import Path

import js2_harness as h
from checks import independent_check

CHECKER = Path(independent_check.__file__)


class IndependentCheckTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = h.make_root(Path(self._tmp.name) / "proj")

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, run_id="RUN1"):
        out = io.StringIO()
        code = independent_check.check_run(f"out/runs/{run_id}",
                                           root=self.root, out=out)
        return code, out.getvalue()

    def test_checker_imports_nothing_from_agent(self):
        tree = ast.parse(CHECKER.read_text(encoding="utf-8"))
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules |= {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                modules.add(node.module or "")
        self.assertFalse([m for m in modules if m.split(".")[0] == "agent"],
                         modules)

    def test_pass_on_clean_run(self):
        script = h.default_script()
        script[h.NO_SUCH] = [h.ok(h.gh_body([1]))]
        h.run(self.root, h.FakeTransport(script))
        code, text = self.check()
        self.assertEqual(code, 0, text)
        self.assertEqual(text.count("PASS"), 4, text)

    def test_failed_board_reported_as_unknown_passes(self):
        h.run(self.root, h.FakeTransport(h.default_script()))
        code, text = self.check()
        self.assertEqual(code, 0, text)
        self.assertIn("PASS rithika-js2-no-such-board", text)

    def test_flags_board_that_had_postings_and_now_reports_zero(self):
        # The known limit: the agent says finished, the checker flags it.
        h.write_state(self.root, "scaleai", [1, 2, 3])
        script = h.default_script()
        script[h.SCALE] = [h.ok(h.gh_body([]))]
        h.run(self.root, h.FakeTransport(script))
        self.assertEqual(h.board(h.summary(self.root), "scaleai")["new"], 0)
        code, text = self.check()
        self.assertEqual(code, 1)
        self.assertIn("FLAG scaleai: board previously had 3 postings but "
                      "now reports 0", text)

    def test_flags_greenhouse_total_mismatch(self):
        script = h.default_script()
        script[h.DATABRICKS] = [h.ok(h.gh_body([10, 11], total=916))]
        h.run(self.root, h.FakeTransport(script))
        code, text = self.check()
        self.assertEqual(code, 1)
        self.assertIn("FLAG databricks: Greenhouse len(jobs) = 2 but "
                      "meta.total = 916", text)

    def test_flags_failed_board_with_a_number(self):
        h.run(self.root, h.FakeTransport(h.default_script()))
        path = self.root / "out/runs/RUN1/summary.json"
        data = json.loads(path.read_text())
        h.board(data, "rithika-js2-no-such-board")["new"] = 0
        path.write_text(json.dumps(data))
        code, text = self.check()
        self.assertEqual(code, 1)
        self.assertIn("FLAG rithika-js2-no-such-board", text)
        self.assertIn("instead of unknown", text)

    def test_flags_summary_count_that_differs_from_raw(self):
        h.run(self.root, h.FakeTransport(h.default_script()))
        path = self.root / "out/runs/RUN1/summary.json"
        data = json.loads(path.read_text())
        h.board(data, "openai")["postings_seen"] = 99
        path.write_text(json.dumps(data))
        code, text = self.check()
        self.assertEqual(code, 1)
        self.assertIn("FLAG openai: summary says 99 postings", text)

    def test_unreadable_run_exits_2(self):
        code, _ = self.check("NOPE")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
