"""Tests for loop.py, written before loop.py (the contract comes first).

Contract for the loop's pure parts:
  extract_code(reply)        -> the one ```python block in Claude's reply, or None (zero or several blocks)
  check_policy(code)         -> list of violations; [] means the code may be run by the scorer
  build_feedback(flags)      -> the next-round prompt, from the CLEAN copy's results only (never the defects)
  passes(score25, score99)   -> True only if both plantings: 5 of 5 caught, 0 clean rows flagged, 0 column-level
                                failures, 0 crashing checks, no error
  decide(round, max_rounds, score25, score99, flags) -> (stop: bool, reason: str)

Run:  .venv/bin/python -m unittest discover -s tests -v
"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import loop  # noqa: E402

REC = HERE / "results" / "2026-10-25"
CC = HERE / "claude-checks"


def j(name):
    return json.loads((REC / name).read_text())


class ExtractCode(unittest.TestCase):
    def test_saved_replies_give_the_saved_code(self):
        for n in (1, 2):
            reply = next(CC.glob(f"round{n}-reply-*.md")).read_text()
            code = loop.extract_code(reply)
            self.assertIsNotNone(code)
            self.assertEqual(code.strip(), (CC / f"round{n}_checks.py").read_text().strip())

    def test_no_block_or_two_blocks_is_refused(self):
        self.assertIsNone(loop.extract_code("Here are your checks: schema = ..."))
        self.assertIsNone(loop.extract_code("```python\na=1\n```\ntext\n```python\nb=2\n```"))


class Policy(unittest.TestCase):
    def test_claudes_real_checks_are_allowed(self):
        for n in (1, 2):
            self.assertEqual(loop.check_policy((CC / f"round{n}_checks.py").read_text()), [])

    def test_hand_written_check_is_allowed(self):
        self.assertEqual(loop.check_policy((HERE / "checks" / "fare_check.py").read_text()), [])

    def test_file_os_network_and_dynamic_code_are_refused(self):
        bad = {
            "import os\nschema = 1": "import os",
            "import subprocess\nschema = 1": "import subprocess",
            "from pathlib import Path\nschema = 1": "import pathlib",
            "schema = open('data/planted/25/answer_key.json').read()": "open",
            "import pandas as pd\nkey = pd.read_json('data/planted/25/answer_key.json')\nschema = 1": "read_json",
            "import pandas as pd\nschema = 1\npd.DataFrame().to_csv('x.csv')": "to_csv",
            "schema = eval('1')": "eval",
            "schema = __import__('os')": "__import__",
            "schema = ().__class__.__subclasses__()": "__subclasses__",
            "import pandas as pd": "no `schema`",
        }
        for code, why in bad.items():
            v = loop.check_policy(code)
            self.assertTrue(v, f"should refuse: {why}")
            self.assertTrue(any(why in x for x in v), f"{why!r} not named in {v}")

    def test_pandas_date_helpers_are_allowed(self):
        code = "import pandas as pd\nimport pandera.pandas as pa\nx = pd.to_datetime('2025-01-01')\nschema = pa.DataFrameSchema({})"
        self.assertEqual(loop.check_policy(code), [])

    def test_syntax_error_is_refused(self):
        self.assertTrue(loop.check_policy("schema = ("))


class Feedback(unittest.TestCase):
    def test_reproduces_the_hand_written_round2_prompt(self):
        """The loop's feedback from round 1's clean-copy results is the prompt I pasted by hand on 2026-10-25."""
        got = loop.build_feedback(j("claude-round1-clean-flags.json"))
        want = (CC / "PROMPT-round2.md").read_text()
        self.assertEqual(got.strip(), want.strip())

    def test_names_a_crashing_rule_on_the_clean_copy(self):
        got = loop.build_feedback(j("claude-round2-clean-flags.json"))
        self.assertIn("fare_amount not finite", got)
        self.assertIn("NotImplementedError", got)

    def test_never_mentions_the_defects(self):
        for f in ("claude-round1-clean-flags.json", "claude-round2-clean-flags.json"):
            got = loop.build_feedback(j(f)).lower()
            for word in ("planted", "defect", "answer key", "negative fare", "duplicate", "held-out"):
                self.assertNotIn(word, got)


class PassAndStop(unittest.TestCase):
    def test_recorded_rounds_do_not_pass(self):
        for lab in ("hand-written-baseline", "claude-round1", "claude-round2"):
            self.assertFalse(loop.passes(j(f"{lab}.json"), j(f"{lab}-heldout.json") if lab != "hand-written-baseline"
                                         else j(f"{lab}.json")))

    def test_a_perfect_score_passes(self):
        s = j("claude-round1.json")
        s["clean"] = {"flagged_rows": 0, "column_failures": [], "crashed_checks": [], "error": None}
        self.assertTrue(loop.passes(s, s))

    def test_stop_reasons(self):
        r1, r1h, f1 = j("claude-round1.json"), j("claude-round1-heldout.json"), j("claude-round1-clean-flags.json")
        self.assertEqual(loop.decide(1, 3, r1, r1h, f1), (False, "continue: clean-copy feedback to give"))
        self.assertEqual(loop.decide(3, 3, r1, r1h, f1)[0], True)
        self.assertIn("budget", loop.decide(3, 3, r1, r1h, f1)[1])
        ok = json.loads(json.dumps(r1)); ok["clean"] = {"flagged_rows": 0, "column_failures": [], "crashed_checks": [], "error": None}
        self.assertEqual(loop.decide(1, 3, ok, ok, {"distinct_rows": 0, "per_rule": [], "column_level": []}),
                         (True, "pass line met"))
        # clean copy is perfect but a defect type is missed: clean-only feedback has nothing left to say
        miss = json.loads(json.dumps(ok)); miss["types_caught"] = 4
        miss["types"]["negative_fare"]["verdict"] = "MISSED"
        stop, why = loop.decide(1, 3, miss, miss, {"distinct_rows": 0, "per_rule": [], "column_level": []})
        self.assertTrue(stop)
        self.assertIn("nothing left", why)


if __name__ == "__main__":
    unittest.main()
