"""The three ATS readers. Bodies here are CONSTRUCTED, shaped like the real
responses saved in runs/ (checked against them in test_real_shapes)."""

import gzip
import pathlib
import unittest

from agent import providers
from agent.policy import Policy
from tests.loop_fakes import ashby, gh, lever

ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestUrls(unittest.TestCase):
    def test_urls_are_on_the_allow_list(self):
        p = Policy(ROOT)
        for ats in providers.PROVIDERS:
            self.assertEqual(p.decide_url(providers.url_for(ats, "x")).outcome,
                             "allow")

    def test_bad_board_names_refused(self):
        for bad in ["../x", "a/b", "", "a b", "x?y=1", "-x", "a" * 65]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                providers.url_for("greenhouse", bad)

    def test_unknown_ats(self):
        with self.assertRaises(ValueError):
            providers.url_for("workday", "x")


class TestParse(unittest.TestCase):
    def test_each_ats(self):
        self.assertEqual(providers.parse("greenhouse", gh(7))[0]["id"], "7")
        self.assertEqual(providers.parse("lever", lever(7))[0]["id"], "lv-7")
        self.assertEqual(providers.parse("ashby", ashby(7))[0]["title"],
                         "Job 7")

    def test_bad_bodies(self):
        for ats, body in [("greenhouse", b""), ("greenhouse", b"<html>"),
                          ("greenhouse", b'{"jobz": []}'),
                          ("lever", b'{"ok": false, "error": "Document not found"}'),
                          ("ashby", b'{"jobs": {}}'),
                          ("ashby", b'{"jobs": [{"title": "no id"}]}')]:
            with self.subTest(ats=ats, body=body), \
                    self.assertRaises(providers.BadBody):
                providers.parse(ats, body)

    def test_empty_list_is_not_bad_body(self):
        self.assertEqual(providers.parse("greenhouse", b'{"jobs": []}'), [])


class TestRealShapes(unittest.TestCase):
    """Every saved 200 response from a live run parses with its reader."""

    def test_saved_live_responses_parse(self):
        files = sorted(ROOT.glob("runs/*-live/raw/*-http200.body.gz"))
        if not files:
            self.skipTest("no live run saved yet")
        for f in files:
            ats = f.name.split("-", 1)[0]
            with self.subTest(file=f.name):
                self.assertGreater(len(providers.parse(
                    ats, gzip.decompress(f.read_bytes()))), 0)


if __name__ == "__main__":
    unittest.main()
