"""Watch mechanism and allow-list. Offline: a fake fetcher returns
CONSTRUCTED responses; nothing here touches the network."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent import fetch, watch

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "resume.json").read_text())


def _response(*jobs):
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode()


A = {"id": 1, "title": "Backend Engineer", "content": "<p>Go</p>", "absolute_url": "u1"}
B = {"id": 2, "title": "ML Engineer, LLM", "content": "<p>Python</p>", "absolute_url": "u2"}
C = {"id": 3, "title": "Designer", "content": "<p>Figma</p>", "absolute_url": "u3"}


class Watch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.state = self.tmp / "state" / "gitlab_seen.json"
        self.evidence = self.tmp / "evidence"

    def _run(self, raw, minute):
        now = datetime(2026, 10, 30, 12, minute, tzinfo=timezone.utc)
        return watch.run("gitlab", RESUME, self.state, self.evidence,
                         fetch=lambda url: raw, now=now)

    def test_first_run_is_baseline_reporting_none(self):
        report = self._run(_response(A, B), 0)
        self.assertTrue(report["baseline"])
        self.assertEqual(report["new"], [])
        self.assertEqual(json.loads(self.state.read_text())["seen_ids"], [1, 2])

    def test_second_run_reports_only_unseen_ids(self):
        self._run(_response(A, B), 0)
        report = self._run(_response(B, C, A), 1)
        self.assertFalse(report["baseline"])
        self.assertEqual([r["id"] for r in report["new"]], [3])
        self.assertEqual(json.loads(self.state.read_text())["seen_ids"], [1, 2, 3])

    def test_rerun_with_no_change_reports_none(self):
        self._run(_response(A, B), 0)
        self.assertEqual(self._run(_response(A, B), 1)["new"], [])

    def test_raw_response_saved_byte_for_byte_with_timestamp(self):
        raw = _response(A)
        report = self._run(raw, 7)
        path = Path(report["evidence_file"])
        self.assertEqual(path.name, "gitlab_jobs_20261030T120700Z.json")
        self.assertEqual(path.read_bytes(), raw)

    def test_from_file_replays_without_fetching_or_resaving(self):
        self._run(_response(A, B), 0)
        seeded = self.tmp / "gitlab_jobs_SEEDED_x.json"
        seeded.write_bytes(_response(A, B, C))

        def no_network(url):
            raise AssertionError("from_file run must not fetch")

        report = watch.run("gitlab", RESUME, self.state, self.evidence, fetch=no_network,
                           now=datetime(2026, 10, 30, 13, 0, tzinfo=timezone.utc),
                           from_file=seeded)
        self.assertTrue(report["seeded"])
        self.assertEqual([r["id"] for r in report["new"]], [3])
        self.assertEqual(report["evidence_file"], str(seeded))
        self.assertEqual(len(list(self.evidence.iterdir())), 1)  # only run 1's file

    def test_rejects_non_fictional_resume(self):
        real_looking = dict(RESUME, email="someone@gmail.com")
        with self.assertRaises(ValueError):
            watch.validate_resume(real_looking)


class AllowList(unittest.TestCase):
    def test_board_url_is_on_allow_list(self):
        self.assertEqual(fetch.check_url(fetch.board_jobs_url("gitlab")),
                         "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true")

    def test_other_hosts_refused(self):
        for url in ("https://api.lever.co/v0/postings/gitlab",
                    "http://boards-api.greenhouse.io/v1/boards/gitlab/jobs",
                    "https://boards-api.greenhouse.io.evil.example/v1",
                    "https://evil.example/?h=boards-api.greenhouse.io"):
            with self.subTest(url=url), self.assertRaises(fetch.HostNotAllowed):
                fetch.fetch(url)

    def test_off_list_redirect_refused(self):
        handler = fetch._AllowListRedirects()
        with self.assertRaises(fetch.HostNotAllowed):
            handler.redirect_request(None, None, 302, "Found", {}, "https://evil.example/")

    def test_board_token_cannot_inject_path(self):
        with self.assertRaises(ValueError):
            fetch.board_jobs_url("gitlab/../../x")


if __name__ == "__main__":
    unittest.main()
