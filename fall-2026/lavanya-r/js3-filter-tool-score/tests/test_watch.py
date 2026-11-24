"""The watch end to end, offline: a fake fetcher stands in for the board, so
these tests never touch the network."""

import gzip
import json
import os
import shutil
import tempfile
import unittest

from agent import fetch, persona, watch
from tests.fixtures import PERSONA, variant


def board(*ids):
    return json.dumps({"jobs": [variant(id=i) for i in ids]}).encode()


class TestAllowList(unittest.TestCase):
    def test_allowed_board_url_passes(self):
        fetch.check_allowed(fetch.board_url("datadog"))

    def test_other_hosts_and_plain_http_are_refused(self):
        for url in ["https://example.com/jobs",
                    "https://boards-api.greenhouse.io.evil.com/v1",
                    "http://boards-api.greenhouse.io/v1/boards/datadog/jobs",
                    "https://api.lever.co/v0/postings/x"]:
            with self.subTest(url=url):
                with self.assertRaises(fetch.HostNotAllowed):
                    fetch.get(url)  # raises before any network call

    def test_board_token_cannot_inject_a_path(self):
        with self.assertRaises(ValueError):
            fetch.board_url("datadog/../../x")


class TestPersona(unittest.TestCase):
    def test_shipped_persona_is_fictional(self):
        self.assertEqual(persona.validate(persona.load(PERSONA)), [])

    def test_real_looking_resume_is_refused(self):
        r = {"personal": {"email": "someone@gmail.com",
                          "phone": "(617) 234-0163"}, "skills": {}}
        self.assertEqual(persona.validate(r), [
            "email is not @example.com", "phone number has no 555"])


class TestWatchRuns(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)

    def run_once(self, raw, stamp, **kw):
        return watch.run("datadog", kw.pop("resume", PERSONA),
                         os.path.join(self.dir, "state.json"),
                         os.path.join(self.dir, "raw"),
                         os.path.join(self.dir, "reports"),
                         stamp=stamp, get=lambda url: raw, **kw)

    def test_baseline_then_new_only(self):
        first = self.run_once(board(1, 2, 3), "t1")
        self.assertTrue(first["run"]["baseline"])
        self.assertEqual(first["new"], [])

        second = self.run_once(board(2, 3, 4, 5), "t2")  # 1 removed, 4,5 added
        self.assertFalse(second["run"]["baseline"])
        self.assertEqual([v["posting_id"] for v in second["new"]], [4, 5])

        third = self.run_once(board(2, 3, 4, 5), "t3")
        self.assertEqual(third["new"], [])

    def test_removed_then_reposted_id_is_not_new(self):
        self.run_once(board(1, 2), "t1")
        self.run_once(board(2), "t2")
        self.assertEqual(self.run_once(board(1, 2), "t3")["new"], [])

    def test_state_from_another_board_is_refused(self):
        self.run_once(board(1, 2), "t1")
        with self.assertRaises(SystemExit):
            watch.run("databricks", PERSONA,
                      os.path.join(self.dir, "state.json"), self.dir,
                      self.dir, stamp="t2", get=lambda url: board(1, 2, 3))

    def test_raw_response_saved_byte_for_byte(self):
        raw = board(7, 8)
        report = self.run_once(raw, "t1")
        with open(report["run"]["raw_path"], "rb") as f:
            self.assertEqual(gzip.decompress(f.read()), raw)

    def test_saved_file_run_must_be_labeled_seeded(self):
        path = os.path.join(self.dir, "earlier.json")
        with open(path, "wb") as f:
            f.write(board(1))
        with self.assertRaises(SystemExit):
            self.run_once(None, "t1", from_file=path)
        report = self.run_once(None, "t1", from_file=path, seeded=True)
        self.assertEqual(report["run"]["kind"], "seeded")

    def test_real_looking_resume_stops_before_any_fetch(self):
        fake = os.path.join(self.dir, "real.json")
        with open(fake, "w") as f:
            json.dump({"personal": {"email": "me@gmail.com",
                                    "phone": "617-234-0000"},
                       "skills": {}}, f)

        def must_not_fetch(url):
            raise AssertionError("fetched despite a non-fictional résumé")
        with self.assertRaises(persona.NotFictional):
            watch.run("datadog", fake, os.path.join(self.dir, "s.json"),
                      self.dir, self.dir, get=must_not_fetch)


if __name__ == "__main__":
    unittest.main()
