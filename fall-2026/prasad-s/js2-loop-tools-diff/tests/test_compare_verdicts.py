"""tools/compare_verdicts.py on a constructed run report (not real data)."""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

from support import JS1

_spec = importlib.util.spec_from_file_location("compare_verdicts", JS1 / "tools" / "compare_verdicts.py")
compare_verdicts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare_verdicts)

REPORT = {
    "summary": {"mode": "seeded", "new_count": 3},
    "new_postings": [
        {"posting_id": "11", "rule_verdict": "not_relevant", "claude_verdict": "not_relevant",
         "claude_justification": {"reply": "constructed"}},
        {"posting_id": "12", "rule_verdict": "not_relevant", "claude_verdict": "relevant",
         "claude_justification": {"reply": "constructed"}},
        {"posting_id": "13", "rule_verdict": "relevant", "claude_verdict": "rejected",
         "claude_justification": {"reply": "constructed", "reasons": ["line 1 is not a §6 line", "REASON is empty"]}},
    ],
}
EXPECTED = [
    "11  rule: not_relevant  judgment (Claude): not_relevant  agree",
    "12  rule: not_relevant  judgment (Claude): relevant  DISAGREE",
    "13  rule: relevant  judgment (Claude): rejected",
    "    - line 1 is not a §6 line",
    "    - REASON is empty",
    "records: 3  agree: 1  disagree: 1  rejected: 1",
]


def run_tool(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = compare_verdicts.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class CompareVerdicts(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.report = self.folder / "report.json"
        self.report.write_text(json.dumps(REPORT), encoding="utf-8")

    def test_one_line_per_record_then_totals(self):
        code, out, _ = run_tool(str(self.report))
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), EXPECTED)

    def test_totals(self):
        _, totals = compare_verdicts.compare(REPORT)
        self.assertEqual(totals, {"agree": 1, "disagree": 1, "rejected": 1})

    def test_not_a_report_is_an_error(self):
        not_report = self.folder / "state.json"
        not_report.write_text('["11", "12"]', encoding="utf-8")
        for path in (not_report, self.folder / "missing.json"):
            with self.subTest(path=path.name):
                code, out, err = run_tool(str(path))
                self.assertNotEqual(code, 0)
                self.assertEqual(out, "")
                self.assertIn("error", err)

    def test_writes_no_files(self):
        before = sorted(self.folder.iterdir())
        run_tool(str(self.report))
        self.assertEqual(sorted(self.folder.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
