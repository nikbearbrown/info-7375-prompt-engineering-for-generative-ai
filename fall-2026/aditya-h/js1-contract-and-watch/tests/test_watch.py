"""Tests for the watch (fetch allow-list, state, new-since-last, résumé guard),
written from CONTRACT.md before the implementation existed. All boards here are
constructed fixtures; no network access is used.
"""
import copy
import datetime as dt
import json
import pathlib
import tempfile
import unittest

from jobwatch import fetch, resume, state, watch

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAYA_PATH = ROOT / "personas" / "maya-sehgal.resume.json"
MAYA = json.loads(MAYA_PATH.read_text())
T0 = dt.datetime(2026, 10, 31, 22, 0, tzinfo=dt.timezone.utc)
T1 = dt.datetime(2026, 11, 1, 22, 0, tzinfo=dt.timezone.utc)


def job(pid, title="Product Manager, X", loc="US", office="US", updated="2026-10-30T00:00:00-04:00"):
    return {"id": pid, "title": title, "location": {"name": loc}, "offices": [{"name": office}],
            "updated_at": updated, "content": ""}


def board(*jobs):
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode()


class AllowList(unittest.TestCase):
    def test_board_url_is_on_allow_list(self):
        url = fetch.board_url("stripe")
        self.assertEqual(url, "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true")
        fetch.check_url(url)

    def test_other_hosts_refused(self):
        for url in ("https://example.com/jobs", "https://boards-api.greenhouse.io.evil.com/v1",
                    "http://boards-api.greenhouse.io/v1/boards/stripe/jobs", "https://api.lever.co/v0/postings/x"):
            with self.subTest(url=url), self.assertRaises(fetch.HostNotAllowed):
                fetch.check_url(url)

    def test_bad_slug_refused(self):
        with self.assertRaises(ValueError):
            fetch.board_url("stripe/../../x")

    def test_parse_rejects_non_json_and_missing_jobs(self):
        for raw in (b"<html>nope</html>", b'{"meta": {}}', b'{"jobs": "x"}'):
            with self.subTest(raw=raw), self.assertRaises(fetch.FetchError):
                fetch.parse_jobs(raw)


class State(unittest.TestCase):
    def test_missing_state_is_none(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(state.load_state(pathlib.Path(d) / "state.json"))

    def test_corrupt_state_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "state.json"
            for text in ("{not json", '{"seen_ids": "abc"}', "[]"):
                p.write_text(text)
                with self.subTest(text=text), self.assertRaises(state.StateError):
                    state.load_state(p)

    def test_new_is_by_id_only(self):
        jobs = [job(1, updated="2026-11-01T00:00:00Z"), job(2), job(3)]
        new = state.new_postings(jobs, {1, 2})
        self.assertEqual([j["id"] for j in new], [3])

    def test_duplicate_ids_reported_once(self):
        self.assertEqual([j["id"] for j in state.new_postings([job(5), job(5)], set())], [5])


class ResumeGuard(unittest.TestCase):
    def test_persona_is_valid(self):
        self.assertEqual(resume.validate_resume(MAYA), [])
        self.assertEqual(resume.persona_guard(MAYA), [])

    def test_real_looking_contacts_refused(self):
        r = copy.deepcopy(MAYA)
        r["personal"]["email"] = "someone@gmail.com"
        self.assertTrue(resume.persona_guard(r))
        r = copy.deepcopy(MAYA)
        r["personal"]["phone"] = "(617) 321-0196"
        self.assertTrue(resume.persona_guard(r))

    def test_missing_required_fields_invalid(self):
        r = copy.deepcopy(MAYA)
        del r["personal"]["location"]
        self.assertTrue(resume.validate_resume(r))
        r = copy.deepcopy(MAYA)
        r["experience"] = []
        self.assertTrue(resume.validate_resume(r))
        r = copy.deepcopy(MAYA)
        r["experience"][0]["title"] = ""
        self.assertTrue(resume.validate_resume(r))


class RunWatch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)
        self.state_path = self.dir / "state.json"

    def tearDown(self):
        self.tmp.cleanup()

    def run_with(self, raw, now):
        return watch.run("stripe", MAYA_PATH, self.state_path, self.dir, fetcher=lambda url: raw, now=now)

    def test_baseline_reports_none_new_and_records_all(self):
        rec = self.run_with(board(job(1), job(2), job(3)), T0)
        self.assertTrue(rec["baseline"])
        self.assertEqual(rec["counts"]["fetched"], 3)
        self.assertEqual(rec["counts"]["new"], 0)
        self.assertEqual(rec["verdicts"], [])
        self.assertEqual(set(state.load_state(self.state_path)["seen_ids"]), {1, 2, 3})
        self.assertTrue(pathlib.Path(rec["raw_response_path"]).exists())

    def test_second_run_reports_only_new_ids(self):
        self.run_with(board(job(1), job(2)), T0)
        rec = self.run_with(board(job(1, updated="2026-11-01T00:00:00Z"), job(2),
                                  job(3, title="Product Marketing Manager")), T1)
        self.assertFalse(rec["baseline"])
        self.assertEqual(rec["counts"]["new"], 1)
        self.assertEqual([v["posting_id"] for v in rec["verdicts"]], [3])
        self.assertEqual(rec["counts"]["relevant_rule"], 0)
        self.assertEqual(rec["counts"]["skipped"], 1)

    def test_removed_id_that_returns_is_not_new(self):
        self.run_with(board(job(1), job(2)), T0)
        self.run_with(board(job(2)), T1)
        rec = self.run_with(board(job(1), job(2)), T1 + dt.timedelta(days=1))
        self.assertEqual(rec["counts"]["new"], 0)

    def test_failed_fetch_leaves_state_untouched(self):
        self.run_with(board(job(1)), T0)
        before = self.state_path.read_text()

        def boom(url):
            raise fetch.FetchError("HTTP 503")

        with self.assertRaises(fetch.FetchError):
            watch.run("stripe", MAYA_PATH, self.state_path, self.dir, fetcher=boom, now=T1)
        self.assertEqual(self.state_path.read_text(), before)

    def test_non_json_body_saved_and_state_untouched(self):
        self.run_with(board(job(1)), T0)
        before = self.state_path.read_text()
        with self.assertRaises(fetch.FetchError):
            self.run_with(b"<html>maintenance</html>", T1)
        self.assertEqual(self.state_path.read_text(), before)
        self.assertTrue(any(p.read_bytes() == b"<html>maintenance</html>" for p in (self.dir / "raw").iterdir()))

    def test_empty_board_with_existing_state_is_suspect(self):
        self.run_with(board(job(1), job(2)), T0)
        before = self.state_path.read_text()
        rec = self.run_with(board(), T1)
        self.assertTrue(rec["suspect_empty"])
        self.assertEqual(self.state_path.read_text(), before)

    def test_corrupt_state_stops_run(self):
        self.state_path.write_text("{oops")
        with self.assertRaises(state.StateError):
            self.run_with(board(job(1)), T0)

    def test_every_reported_posting_is_in_raw_response(self):
        self.run_with(board(job(1)), T0)
        rec = self.run_with(board(job(1), job(7), job(8)), T1)
        raw_ids = {j["id"] for j in json.loads(pathlib.Path(rec["raw_response_path"]).read_text())["jobs"]}
        self.assertTrue({v["posting_id"] for v in rec["verdicts"]} <= raw_ids)

    def test_outputs_written(self):
        self.run_with(board(job(1)), T0)
        rec = self.run_with(board(job(1), job(2)), T1)
        self.assertTrue(pathlib.Path(rec["record_path"]).exists())
        self.assertTrue(pathlib.Path(rec["report_path"]).exists())
        self.assertIn("Product Manager, X", pathlib.Path(rec["report_path"]).read_text())

    def test_seeded_run_is_labelled(self):
        self.run_with(board(job(1)), T0)
        rec = watch.run("stripe", MAYA_PATH, self.state_path, self.dir, fetcher=None, now=T1,
                        seeded_raw=board(job(1), job(2)), seeded_from="raw/earlier.json")
        self.assertTrue(rec["seeded"])
        self.assertIn("SEEDED", pathlib.Path(rec["report_path"]).read_text())

    def test_refuses_non_persona_resume_before_fetch(self):
        bad = copy.deepcopy(MAYA)
        bad["personal"]["email"] = "real.person@gmail.com"
        p = self.dir / "bad.json"
        p.write_text(json.dumps(bad))
        called = []
        with self.assertRaises(resume.ResumeError):
            watch.run("stripe", p, self.state_path, self.dir, fetcher=lambda u: called.append(u), now=T0)
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
