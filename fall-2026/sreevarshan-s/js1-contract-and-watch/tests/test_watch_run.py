"""Watch run (python3 -m js1, no flags). Fetch is MOCKED with CONSTRUCTED responses: no network."""

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from js1 import rule_judge, watch
from js1.__main__ import EXIT_FETCH_FAILED, EXIT_NO_BASELINE, run_baseline, run_watch

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).parent / "fixtures"
RUN1 = (FIXTURES / "constructed_board_run1.json").read_bytes()  # ids 9000001-9000003
RUN2 = (FIXTURES / "constructed_board_run2.json").read_bytes()  # drops 9000003, adds 9000004, 9000005
RESUME = json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text(encoding="utf-8"))
PROFILE = json.loads((ROOT / "persona" / "priya-nair.profile.json").read_text(encoding="utf-8"))
BASE_STAMP = "2026-10-29T22-00-00Z"
RUN_STAMP = "2026-10-30T12-00-00Z"


class WatchRunTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.state = tmp / "state" / "seen_ids.json"
        self.raw_dir = tmp / "evidence" / "raw"
        self.rule_dir = tmp / "evidence" / "rule"
        self.fetches = []

    def tearDown(self):
        self._tmp.cleanup()

    def _fetcher(self, body):
        def fetch_raw():
            self.fetches.append(1)
            if isinstance(body, Exception):
                raise body
            return body
        return fetch_raw

    def _baseline(self):
        code = run_baseline(self.state, self.raw_dir, self._fetcher(RUN1), BASE_STAMP, io.StringIO(), io.StringIO())
        self.assertEqual(code, 0)
        self.fetches.clear()

    def _watch(self, body, stamp=RUN_STAMP, judge=rule_judge.judge):
        out, err = io.StringIO(), io.StringIO()
        code = run_watch(self.state, self.raw_dir, self.rule_dir, self._fetcher(body), stamp, RESUME, PROFILE,
                         judge=judge, out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    def test_missing_state_is_refused(self):
        code, out, err = self._watch(RUN2)
        self.assertEqual(code, EXIT_NO_BASELINE)
        self.assertIn("--baseline", err)
        self.assertEqual(self.fetches, [], "must not fetch without a baseline")
        self.assertFalse(self.raw_dir.exists())
        self.assertFalse(self.state.exists())

    def test_new_and_removed_are_counted_against_constructed_responses(self):
        self._baseline()
        code, out, _ = self._watch(RUN2)
        self.assertEqual(code, 0)
        self.assertIn("4 fetched, 2 new, 1 removed", out)
        self.assertIn("NEW 9000004  CONSTRUCTED AI Engineer", out)
        self.assertIn("NEW 9000005  CONSTRUCTED Associate Data Engineer", out)
        saved = json.loads((self.rule_dir / f"{RUN_STAMP}.json").read_text(encoding="utf-8"))
        self.assertEqual((saved["run"]["fetched"], saved["run"]["new"], saved["run"]["removed"]), (4, 2, 1))
        self.assertEqual(saved["run"]["removed_ids"], [9000003])
        self.assertEqual((self.raw_dir / f"{RUN_STAMP}.json").read_bytes(), RUN2)

    def test_removed_is_not_counted_again_on_the_next_run(self):
        self._baseline()
        self._watch(RUN2)
        code, out, _ = self._watch(RUN2, stamp="2026-10-31T12-00-00Z")
        self.assertEqual(code, 0)
        self.assertIn("4 fetched, 0 new, 0 removed since 2026-10-30T12-00-00Z", out)

    def test_rule_judge_runs_only_on_new_postings(self):
        self._baseline()
        judged = []

        def spy(posting, resume, profile):
            judged.append(posting["id"])
            return rule_judge.judge(posting, resume, profile)

        self._watch(RUN2, judge=spy)
        self.assertEqual(judged, [9000004, 9000005])
        saved = json.loads((self.rule_dir / f"{RUN_STAMP}.json").read_text(encoding="utf-8"))
        self.assertEqual([r["posting_id"] for r in saved["records"]], [9000004, 9000005])
        self.assertTrue(all(r["label"] == "record" for r in saved["records"]))

    def test_state_updates_only_after_success_and_previous_state_is_kept(self):
        self._baseline()
        before = self.state.read_bytes()

        def broken(posting, resume, profile):
            raise RuntimeError("judge crashed")

        with self.assertRaises(RuntimeError):
            self._watch(RUN2, judge=broken)
        self.assertEqual(self.state.read_bytes(), before, "state must not change when a later step fails")
        self.assertFalse((self.state.parent / f"seen_ids.{BASE_STAMP}.json").exists())

        code, _, _ = self._watch(RUN2)
        self.assertEqual(code, 0)
        self.assertEqual((self.state.parent / f"seen_ids.{BASE_STAMP}.json").read_bytes(), before)
        after = watch.load_state(self.state)
        self.assertEqual(after["seen_ids"], {9000001, 9000002, 9000003, 9000004, 9000005})
        self.assertEqual(after["last_fetched_ids"], {9000001, 9000002, 9000004, 9000005})
        self.assertEqual(after["last_run"], RUN_STAMP)

    def test_failed_fetch_leaves_state_untouched(self):
        self._baseline()
        before = self.state.read_bytes()
        code, _, err = self._watch(urllib.error.URLError("no route to host"))
        self.assertEqual(code, EXIT_FETCH_FAILED)
        self.assertIn("state unchanged", err)
        self.assertEqual(self.state.read_bytes(), before)
        self.assertFalse((self.raw_dir / f"{RUN_STAMP}.json").exists())
        self.assertFalse(self.rule_dir.exists())

    def test_unusable_response_is_saved_but_leaves_state_untouched(self):
        self._baseline()
        before = self.state.read_bytes()
        code, _, _ = self._watch(b"<html>Service Unavailable</html>")
        self.assertEqual(code, EXIT_FETCH_FAILED)
        self.assertEqual((self.raw_dir / f"{RUN_STAMP}.json").read_bytes(), b"<html>Service Unavailable</html>")
        self.assertEqual(self.state.read_bytes(), before)

    def test_state_from_before_this_change_still_works(self):
        # The committed live state has only seen_ids; the previous stamp comes from the raw evidence name.
        self.state.parent.mkdir(parents=True)
        self.state.write_text(json.dumps({"seen_ids": [9000001, 9000002, 9000003]}) + "\n", encoding="utf-8")
        self.raw_dir.mkdir(parents=True)
        (self.raw_dir / f"{BASE_STAMP}.json").write_bytes(RUN1)
        code, out, _ = self._watch(RUN2)
        self.assertEqual(code, 0)
        self.assertIn(f"4 fetched, 2 new, 1 removed since {BASE_STAMP}", out)
        self.assertTrue((self.state.parent / f"seen_ids.{BASE_STAMP}.json").exists())


if __name__ == "__main__":
    unittest.main()
