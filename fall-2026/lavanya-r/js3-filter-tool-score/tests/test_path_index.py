"""Review packet: the test written BEFORE the patch to agent/claude_judge.py.

Written 2026-11-10, BEFORE any patch to agent/claude_judge.py (see git log).
Provenance: Claude listed the paths, wrote this harness AND chose every
EXPECTED value; I handed this decision to Claude (2026-11-10). So the spec below
is Claude's, approved by me.
True = the validator should accept this résumé field, False = reject it.

The spec: an index means "item N of a list", written either `[N]` or `.N`.
It must exist (0 <= N < length). An index on something that is not a list is
wrong. A list path with no index keeps its JS1 meaning ("any item"), which is
out of scope for this fix.

Run from the JS2 folder:  python3 -B -m unittest tests.test_path_index -v
Before the patch, at least the `.0` rows must fail. That is the reproduction.
"""
import json
import pathlib
import unittest

from agent.claude_judge import path_exists, validate

HERE = pathlib.Path(__file__).resolve().parent.parent
RESUME = json.loads((HERE / "persona/priya-nair.resume.json").read_text())
# Priya's résumé has exactly 1 education entry and 1 experience entry; skills is an object
# (check with: python3 -c "import json;r=json.load(open('persona/priya-nair.resume.json'));print(len(r['education']),len(r['experience']))").

# ---- EXPECTED values: chosen by Claude, approved by Lavanya, 2026-11-10 ----
CASES = [
    # path                         EXPECTED  # why (optional, your words)
    ("education.end_date",          True ),
    ("education[0].end_date",       True ),
    ("education.0.end_date",        True ),   # the reported defect
    ("education.0.status",          True ),   # also in the real 2026-10-30 reply
    ("experience.0.title",          True ),   # her one job: index in range
    ("experience.1.title",          False),   # a second job she doesn't have
    ("education[5].end_date",       False),   # index out of range, bracket form
    ("education.5.end_date",        False),   # index out of range, dot form
    ("education.-1.end_date",       False),   # negative index
    ("skills.0",                    False),   # skills is an object, not a list
    ("education[0]",                True ),   # stops at a list item, no field
]
# ------------------------------------------------------------------------------

REAL_REPLY_FILE = (HERE.parent / "js1-contract-and-watch/evidence/claude/"
                   "experiment/revision-dev/6865698002.json")


class TestPathIndex(unittest.TestCase):
    def test_every_case_has_an_expected_value(self):
        missing = [p for p, e in CASES if e is None]
        self.assertEqual(missing, [], "fill in EXPECTED for these paths")

    def test_paths(self):
        for path, expected in CASES:
            if expected is None:
                continue
            with self.subTest(path=path):
                self.assertIs(path_exists(RESUME, path), expected)

    def test_real_reply_from_2026_10_30(self):
        """The real Claude reply that JS1 marked INVALID only for `.0` paths.
        Write here what the validator SHOULD return for it:"""
        SHOULD_BE_VALID = True
        self.assertIsNotNone(SHOULD_BE_VALID, "fill in SHOULD_BE_VALID")
        saved = json.loads(REAL_REPLY_FILE.read_text())
        parsed, errors = validate(saved["raw_reply"], 6865698002, RESUME)
        self.assertIs(parsed is not None, SHOULD_BE_VALID, errors)


if __name__ == "__main__":
    unittest.main()
