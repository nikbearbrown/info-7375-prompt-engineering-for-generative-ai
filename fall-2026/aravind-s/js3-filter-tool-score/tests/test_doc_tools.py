"""Two tools behind the documents: tools/boundary_table.py fills BOUNDARY-TESTS.md the same way however
often it runs, and tools/explain_rule.py shows either contract's reading of check 7, so posting 19's bug
can still be seen with --contract 0.1 after the review packet's patch (4b1a418)."""

import importlib.util
import io
import unittest
from contextlib import redirect_stdout

from .loop_helpers import REPO

POSTING_19 = "9efcef02-0515-4672-bace-81329944b38b"
BASELINE = REPO / "runs" / "2026-10-30T093102Z" / "response.json"
TABLE = """# Boundary tests

| # | Action | My prediction | Actual | Match |
|---:|---|---|---|---|
| 1 | GET a host off the allow-list | refuse |  |  |
| 2 | Write runs/../persona/jane-doe.json | allow |  |  |
"""
RESULTS = {1: ("refuse", "refused: not on the allow-list"), 2: ("refuse", "refused: a path with '..'")}


def tool(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BoundaryTableTest(unittest.TestCase):
    def test_filling_the_table_again_gives_the_same_file(self):
        boundary_table = tool("boundary_table")
        once = boundary_table.filled(TABLE, RESULTS)
        self.assertEqual(once.count("predictions match."), 1)
        self.assertIn("1 of 2 predictions match.", once)
        self.assertEqual(boundary_table.filled(once, RESULTS), once)


class ExplainRuleTest(unittest.TestCase):
    def explain(self, *options):
        out = io.StringIO()
        with redirect_stdout(out):
            code = tool("explain_rule").main([str(BASELINE), POSTING_19, *options])
        return code, out.getvalue()

    def test_contract_0_1_still_shows_posting_19s_bug(self):
        code, out = self.explain("--contract", "0.1")
        self.assertEqual(code, 0)
        self.assertIn("contract v0.1", out)
        self.assertIn("Rule verdict (record): relevant", out)
        self.assertIn("states no years of experience", out)

    def test_the_default_is_the_agents_contract(self):
        code, out = self.explain()
        self.assertEqual(code, 0)
        self.assertIn("contract v0.2", out)
        self.assertIn("Rule verdict (record): not_relevant", out)

    def test_an_unknown_contract_is_refused(self):
        self.assertEqual(self.explain("--contract", "0.3")[0], 2)


if __name__ == "__main__":
    unittest.main()
