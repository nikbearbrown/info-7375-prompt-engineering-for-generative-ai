"""tools/compare_hand_labels.py on constructed labels and a constructed board (not real data)."""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import JS1, persona

_spec = importlib.util.spec_from_file_location("compare_hand_labels", JS1 / "tools" / "compare_hand_labels.py")
compare_hand_labels = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare_hand_labels)

BOARD = {"jobs": [
    {"id": 91, "title": "Product Manager", "location": {"name": "New York, NY"},
     "content": "&lt;p&gt;SQL and Python&lt;/p&gt;"},
    {"id": 92, "title": "Product Marketing Manager", "location": {"name": "Remote"}, "content": "SQL only"},
    {"id": 93, "title": "Product Analyst", "location": {"name": "London"},
     "content": "&lt;b&gt;A/B testing&lt;/b&gt; and user research"},
    {"id": 94, "title": "Associate Product Manager", "location": {"name": "nyc office"},
     "content": "Python, python"},
]}


def label(posting_id, c1, c2, c3, verdict, skills=()):
    return {"id": posting_id, "C1": c1, "C2": c2, "C3": c3, "skills_found": list(skills), "verdict": verdict}


LABELS = [
    label("91", True, True, True, "relevant", ["SQL", "Python"]),  # agrees
    label("92", True, True, False, "not_relevant", ["SQL"]),  # C1 differs
    label("93", True, False, False, "not_relevant", ["A/B testing"]),  # C3 differs
    label("94", True, True, False, "relevant", ["Python"]),  # verdict differs
]
EXPECTED = [
    "91  hand: C1=true  C2=true  C3=true  relevant  rule: C1=true  C2=true  C3=true  relevant  agree",
    "92  hand: C1=true  C2=true  C3=false  not_relevant  rule: C1=false  C2=true  C3=false  not_relevant"
    "  DISAGREE on C1",
    "    C1: rule matched in title: nothing",
    "    C1: rule compared title: 'Product Marketing Manager'",
    "93  hand: C1=true  C2=false  C3=false  not_relevant  rule: C1=true  C2=false  C3=true  not_relevant"
    "  DISAGREE on C3",
    "    C3: rule matched in content: 'A/B testing' as 'A/B testing', 'user research' as 'user research'",
    "    C3: rule found 2 distinct skill(s), needs 2; content present: true",
    "    C3: hand skills_found: ['A/B testing']",
    "94  hand: C1=true  C2=true  C3=false  relevant  rule: C1=true  C2=true  C3=false  not_relevant"
    "  DISAGREE on verdict",
    "    verdict: rule failing conditions: C3",
    "labels: 4  agree: 1  disagree: 3  C1 differs: 1  C2 differs: 0  C3 differs: 1  verdict differs: 1",
]


def run_tool(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = compare_hand_labels.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class CompareHandLabels(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.board = self.folder / "board.json"
        self.board.write_text(json.dumps(BOARD), encoding="utf-8")
        self.labels = self.write_labels(LABELS)

    def write_labels(self, labels, name="labels.json"):
        path = self.folder / name
        # An absolute source stays as it is when the tool joins it to JS1.
        path.write_text(json.dumps({"source": str(self.board), "labels": labels}), encoding="utf-8")
        return path

    def test_one_line_per_label_then_why_then_totals(self):
        code, out, err = run_tool(str(self.labels))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.splitlines(), EXPECTED)

    def test_labels_file_argument_and_default(self):
        heldout = self.write_labels(LABELS[:1], "hand_labels_heldout.json")
        code, out, _ = run_tool(str(heldout))
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [EXPECTED[0], "labels: 1  agree: 1  disagree: 0  C1 differs: 0  "
                                                         "C2 differs: 0  C3 differs: 0  verdict differs: 0"])
        with mock.patch.object(compare_hand_labels, "DEFAULT_LABELS", self.labels):
            code, out, _ = run_tool()  # no argument: the default labels file
        self.assertEqual((code, out.splitlines()), (0, EXPECTED))

    def test_totals(self):
        doc = {"source": "board.json", "labels": LABELS}
        _, totals = compare_hand_labels.compare(doc, persona(), lambda source: compare_hand_labels.load_postings(
            self.folder / source))
        self.assertEqual(totals, {"agree": 1, "disagree": 3, "C1": 1, "C2": 0, "C3": 1, "verdict": 1})

    def test_bad_input_is_an_error_with_no_output(self):
        not_labels = self.folder / "state.json"
        not_labels.write_text('["91"]', encoding="utf-8")
        cases = {
            "not a labels file": not_labels,
            "missing file": self.folder / "missing.json",
            "id not in source": self.write_labels([label("99", False, False, False, "not_relevant")], "l1.json"),
            "C1 not a boolean": self.write_labels([dict(LABELS[0], C1="yes")], "l2.json"),
            "unknown verdict": self.write_labels([dict(LABELS[0], verdict="maybe")], "l3.json"),
        }
        for name, path in cases.items():
            with self.subTest(name):
                code, out, err = run_tool(str(path))
                self.assertNotEqual(code, 0)
                self.assertEqual(out, "")
                self.assertIn("error", err)

    def test_writes_no_files(self):
        before = sorted(self.folder.iterdir())
        run_tool(str(self.labels))
        self.assertEqual(sorted(self.folder.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
