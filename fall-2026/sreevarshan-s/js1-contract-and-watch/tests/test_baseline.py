import io
import json
import tempfile
import unittest
from pathlib import Path

from js1 import watch
from js1.__main__ import run_baseline

FIXTURES = Path(__file__).parent / "fixtures"


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.state = tmp / "state" / "seen_ids.json"
        self.raw_dir = tmp / "evidence" / "raw"
        self.calls = []
        self.raw = (FIXTURES / "constructed_board_run1.json").read_bytes()

    def tearDown(self):
        self._tmp.cleanup()

    def _fetch(self):
        self.calls.append(1)
        return self.raw

    def _run(self):
        out, err = io.StringIO(), io.StringIO()
        code = run_baseline(self.state, self.raw_dir, self._fetch, "2026-10-29T12-00-00Z", out, err)
        return code, out.getvalue(), err.getvalue()

    def test_refuses_if_state_exists(self):
        self.state.parent.mkdir(parents=True)
        self.state.write_text('{"seen_ids": [1]}\n', encoding="utf-8")
        before = self.state.read_bytes()
        code, out, err = self._run()
        self.assertNotEqual(code, 0)
        self.assertIn("refusing --baseline", err)
        self.assertEqual(self.calls, [], "must not fetch when state exists")
        self.assertEqual(self.state.read_bytes(), before)
        self.assertFalse(self.raw_dir.exists())
        self.assertNotIn("BASELINE", out)

    def test_baseline_saves_raw_records_ids_reports_zero_new(self):
        # CONSTRUCTED fixture stands in for the live response.
        code, out, err = self._run()
        self.assertEqual(code, 0)
        self.assertEqual(self.calls, [1], "exactly one fetch")
        self.assertEqual((self.raw_dir / "2026-10-29T12-00-00Z.json").read_bytes(), self.raw)
        self.assertEqual(watch.load_seen(self.state), {9000001, 9000002, 9000003})
        self.assertIn("BASELINE: 3 postings recorded, 0 new", out)

    def test_second_baseline_is_refused(self):
        self.assertEqual(self._run()[0], 0)
        state_after_first = self.state.read_bytes()
        code, _, _ = self._run()
        self.assertNotEqual(code, 0)
        self.assertEqual(self.calls, [1])
        self.assertEqual(self.state.read_bytes(), state_after_first)


if __name__ == "__main__":
    unittest.main()
