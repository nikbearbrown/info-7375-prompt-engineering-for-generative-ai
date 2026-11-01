import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import run
from jsagent.watch import load_raw, new_postings, next_state, parse_jobs, save_raw
from tests import fixtures as F


def rec(ids_jobs):
    return {"board": "stripe", "run_at_utc": "t", "new_ids": []}


class NewSinceLastTests(unittest.TestCase):
    def test_baseline_reports_none(self):
        self.assertEqual(new_postings(None, F.ALL), [])

    def test_only_unseen_ids_are_new(self):
        state = next_state(None, F.ALL[:3], rec(None))
        new = new_postings(state, F.ALL)
        self.assertEqual([str(j["id"]) for j in new], ["104", "105", "106"])

    def test_no_duplicate_reports(self):
        state = next_state(None, F.ALL[:3], rec(None))
        state = next_state(state, F.ALL, rec(None))
        self.assertEqual(new_postings(state, F.ALL), [])

    def test_removed_posting_is_not_new_when_it_returns(self):
        state = next_state(None, F.ALL, rec(None))
        state = next_state(state, F.ALL[1:], rec(None))  # 101 disappears from the board
        self.assertEqual(new_postings(state, F.ALL), [])  # ...and is not "new" when it comes back

    def test_id_type_does_not_matter(self):
        state = next_state(None, [dict(F.RELEVANT, id="101")], rec(None))
        self.assertEqual(new_postings(state, [F.RELEVANT]), [])

    def test_duplicate_ids_in_a_response_rejected(self):
        with self.assertRaises(ValueError):
            parse_jobs(F.response([F.RELEVANT, F.RELEVANT]))


class EvidenceTests(unittest.TestCase):
    def test_raw_saved_byte_for_byte(self):
        raw = F.response(F.ALL)
        with tempfile.TemporaryDirectory() as d:
            record = save_raw(raw, d, "20261031T000000Z", "live")
            self.assertEqual(load_raw(Path(d) / record["file"]), raw)
            self.assertEqual(record["bytes"], len(raw))


class EndToEndTests(unittest.TestCase):
    """Two runs through run.main on constructed files: baseline, then a second run with three new postings."""

    def test_baseline_then_second_run(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "first.json").write_bytes(F.response(F.ALL[3:]))
            (d / "second.json").write_bytes(F.response(F.ALL))
            common = ["--state", str(d / "state.json"), "--evidence", str(d / "raw"), "--reports", str(d / "reports")]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run.main(["--from-file", str(d / "first.json")] + common), 0)
                self.assertEqual(run.main(["--from-file", str(d / "second.json")] + common), 0)
            self.assertEqual(len(list((d / "raw").iterdir())), 2)  # both raw responses kept
            state = json.loads((d / "state.json").read_text())
            self.assertEqual([r["baseline"] for r in state["runs"]], [True, False])
            self.assertEqual(state["runs"][0]["new_ids"], [])
            self.assertEqual(state["runs"][1]["new_ids"], ["101", "102", "103"])
            self.assertTrue(all(r["label"] == "seeded" for r in state["runs"]))
            reports = [json.loads(f.read_text()) for f in (d / "reports").glob("*.json")]
            report = next(r for r in reports if not r["run"]["baseline"])
            self.assertEqual(len(report["postings"]), 3)
            for p in report["postings"]:  # the two judges stay separate and labeled
                self.assertEqual(p["verdict"], F.EXPECTED[p["posting_id"]])
                self.assertIn("RECORD", p["rule_label"])
                self.assertIn("MODEL JUDGMENT", p["claude"]["label"])
                self.assertIsNone(p["claude"]["verdict"])


if __name__ == "__main__":
    unittest.main()
