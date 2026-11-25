"""js3.measure on CONSTRUCTED decisions and verdicts (not real labels)."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from js3 import measure


def decision(pid, dec, score):
    return {"board": "constructed", "id": pid, "title": f"Title {pid}",
            "decision": dec, "score": score}


DECISIONS = [decision("a", "kept", 5), decision("b", "kept", 4),
             decision("c", "rejected", 1), decision("d", "rejected", 3),
             decision("e", "abstain", 3), decision("f", "rejected", 0),
             decision("g", "kept", 6)]
KEY = {"a": {"stratum": "kept", "decision": "kept", "score": 5},
       "b": {"stratum": "close_call", "decision": "kept", "score": 4},
       "c": {"stratum": "rejected", "decision": "rejected", "score": 1},
       "d": {"stratum": "close_call", "decision": "rejected", "score": 3},
       "e": {"stratum": "close_call", "decision": "abstain", "score": 3},
       "f": {"stratum": "rejected", "decision": "rejected", "score": 0}}


class WilsonTests(unittest.TestCase):

    def test_known_values(self):
        low, high = measure.wilson(0, 10)
        self.assertAlmostEqual(low, 0.0, places=4)
        self.assertAlmostEqual(high, 0.2775, places=4)
        low, high = measure.wilson(2, 10)
        self.assertAlmostEqual(low, 0.0567, places=4)
        self.assertAlmostEqual(high, 0.5098, places=4)

    def test_n_zero_refused(self):
        with self.assertRaises(ValueError):
            measure.wilson(0, 0)


class MeasureTests(unittest.TestCase):

    def test_counts_disagreements_and_unlabeled(self):
        verdicts = {"a": "relevant", "b": "not", "c": "relevant",
                    "d": "not", "e": "relevant", "f": None}
        res = measure.measure(DECISIONS, verdicts)
        self.assertEqual(res["counts"], {
            "kept&relevant": 1, "kept&not": 1, "rejected&relevant": 1,
            "rejected&not": 1, "unsure": 0, "abstain": 1, "unlabeled": 1})
        self.assertEqual(sorted(r["id"] for r in res["disagreements"]),
                         ["b", "c"])
        self.assertEqual(res["unlabeled"], ["f"])

    def test_key_ids_missing_from_verdicts_are_unlabeled(self):
        res = measure.measure(DECISIONS, {"a": "relevant"}, KEY)
        self.assertEqual(res["counts"]["unlabeled"], 5)
        self.assertEqual(res["counts"]["kept&relevant"], 1)
        rej = res["strata"]["rejected"]
        self.assertEqual((rej["n"], rej["errors"], rej["unlabeled"]),
                         (0, 0, 2))
        self.assertIsNone(rej["wilson95"])

    def test_per_stratum_errors_with_interval_wording(self):
        verdicts = {"a": "relevant", "b": "not", "c": "not", "d": "unsure",
                    "e": "not", "f": "relevant"}
        res = measure.measure(DECISIONS, verdicts, KEY)
        close = res["strata"]["close_call"]
        self.assertEqual((close["n"], close["errors"], close["unsure"],
                          close["abstain"]), (1, 1, 1, 1))
        text = measure.report(res)
        self.assertIn("sample estimate (n=1), not a measured rate for all "
                      "postings", text)
        self.assertIn("sample estimate (n=2)", text)

    def test_csv_blank_and_invalid_verdicts_are_unlabeled(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "v.csv"
            path.write_text("id,verdict,reason\na, Relevant ,x\nb,,\n"
                            "c,yes,typo\n")
            verdicts, problems = measure.load_verdicts(path)
        self.assertEqual(verdicts, {"a": "relevant", "b": None, "c": None})
        self.assertEqual(len(problems), 1)

    def test_cli_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "d.jsonl").write_text(
                "\n".join(json.dumps(d) for d in DECISIONS) + "\n")
            (tmp / "v.csv").write_text("id,verdict,reason\na,relevant,\n")
            (tmp / "k.json").write_text(json.dumps({"key": KEY}))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = measure.main(["--decisions", str(tmp / "d.jsonl"),
                                     "--verdicts", str(tmp / "v.csv"),
                                     "--key", str(tmp / "k.json")])
        self.assertEqual(code, 0)
        self.assertIn("unlabeled          5", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
