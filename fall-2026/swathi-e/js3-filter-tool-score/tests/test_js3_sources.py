"""Tests for getting descriptions (G1-G6), written before the parser change.

From the test design Claude Code proposed on 2026-11-17 and Swathi approved,
checking FILTER.md's Expected sources (Greenhouse "fetched with descriptions
included", Ashby description) and the JS2 budget rules it keeps. This is a
CHANGE TO COPIED CODE: parsers.py gains include_description=False; with the
default, its output must stay exactly as in JS2 (G2). loop.py is not changed:
JS3 passes job_filter.JS3_URLS through run_loop's existing urls parameter.

Every response body below is SIMULATED (built here, never fetched). Written by
Claude Code. Every test runs inside no_network().
"""
from contextlib import contextmanager
import html
import importlib
import json
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import loop  # noqa: E402
import parsers  # noqa: E402
import policy  # noqa: E402


@contextmanager
def no_network():
    def refuse(*args, **kwargs):
        raise AssertionError("a network connection was attempted")
    with patch.object(socket, "create_connection", refuse), patch.object(socket.socket, "connect", refuse):
        yield


def job_filter():
    return importlib.import_module("job_filter")


def gh_body(*jobs):
    """SIMULATED Greenhouse ?content=true body; content is HTML escaped once more, as the API does."""
    out = []
    for job_id, title, content in jobs:
        job = {"id": job_id, "title": title, "location": {"name": "Boston, Massachusetts"},
               "absolute_url": f"https://example.invalid/gh/{job_id}"}
        if content is not None:
            job["content"] = content
        out.append(job)
    return json.dumps({"jobs": out, "meta": {"total": len(out)}}).encode()


def ashby_body(*jobs):
    """SIMULATED Ashby body."""
    out = []
    for job_id, title, description in jobs:
        job = {"id": job_id, "title": title, "location": "Remote - US", "secondaryLocations": [],
               "jobUrl": f"https://example.invalid/ashby/{job_id}", "isListed": True}
        if description is not None:
            job["descriptionHtml"] = description
        out.append(job)
    return json.dumps({"apiVersion": "1", "jobs": out}).encode()


class Parsers(unittest.TestCase):
    def test_G1_greenhouse_content_is_unescaped_once(self):
        """G1, FILTER.md Expected sources (Greenhouse description), change to copied parsers.py.
        SIMULATED: content escaped once by the API comes back as the original HTML, unescaped
        exactly once (an &amp; inside the original HTML stays &amp;)."""
        original = "<h2>Responsibilities</h2><p>Build &amp; ship SQL pipelines</p>"
        with no_network():
            postings, _ = parsers.parse_greenhouse(gh_body((1, "Data Engineer", html.escape(original))),
                                                   include_description=True)
        self.assertEqual(postings[0]["description_html"], original)

    def test_G2_default_output_unchanged(self):
        """G2, change to copied parsers.py must keep JS2 behavior: without include_description the
        postings have exactly the JS2 keys (id, title, location, url). SIMULATED bodies."""
        with no_network():
            gh, _ = parsers.parse_greenhouse(gh_body((1, "Data Engineer", "&lt;p&gt;x&lt;/p&gt;")))
            ashby, _ = parsers.parse_ashby(ashby_body(("a-1", "Data Engineer", "<p>x</p>")))
        self.assertEqual(set(gh[0]), {"id", "title", "location", "url"})
        self.assertEqual(set(ashby[0]), {"id", "title", "location", "url"})

    def test_G3_ashby_description_html_passed_through(self):
        """G3, FILTER.md Expected sources (Plaid/Ashby description), change to copied parsers.py.
        SIMULATED: descriptionHtml is returned unchanged as description_html."""
        with no_network():
            postings, _ = parsers.parse_ashby(ashby_body(("a-1", "Data Engineer", "<h3>Responsibilities</h3><p>SQL</p>")),
                                              include_description=True)
        self.assertEqual(postings[0]["description_html"], "<h3>Responsibilities</h3><p>SQL</p>")

    def test_G4_missing_or_empty_description_is_empty_string(self):
        """G4, FILTER.md Expected sources (a missing or empty description). SIMULATED: a missing or
        empty content/descriptionHtml becomes "" (the filter then says "I cannot tell")."""
        with no_network():
            gh, _ = parsers.parse_greenhouse(gh_body((1, "Data Engineer", None), (2, "Data Engineer", "")),
                                             include_description=True)
            ashby, _ = parsers.parse_ashby(ashby_body(("a-1", "Data Engineer", None), ("a-2", "Data Engineer", "")),
                                           include_description=True)
        self.assertEqual([p["description_html"] for p in gh + ashby], ["", "", "", ""])


class Urls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve() / "js3"
        for folder in ("runs", "state", "persona"):
            (self.root / folder).mkdir(parents=True)
        for name in ("priya-nair.resume.example.json", "priya-nair.targets.json"):
            shutil.copy(HERE / "persona" / name, self.root / "persona" / name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_G5_js3_urls(self):
        """G5, FILTER.md Expected sources (Greenhouse "fetched with descriptions included"): the
        Greenhouse URL is the JS2 URL plus ?content=true, still allowed by the permission policy;
        the Ashby URL is unchanged."""
        urls = job_filter().JS3_URLS
        self.assertEqual(urls["greenhouse"], loop.URLS["greenhouse"] + "?content=true")
        self.assertEqual(urls["ashby"], loop.URLS["ashby"])
        url = urls["greenhouse"].format(slug="databricks")
        self.assertEqual(policy.Policy(self.root).check_host(url), url)

    def test_G6_one_request_per_board_same_budgets(self):
        """G6, FILTER.md Expected sources plus JS2 rules (GATE.md budgets): run_loop with JS3_URLS
        makes exactly one request per board, to the ?content=true URLs, within loop.BUDGETS.
        SIMULATED fake transport and responses; nothing is fetched."""
        urls = job_filter().JS3_URLS
        boards = [{"name": "databricks", "system": "greenhouse", "slug": "databricks"},
                  {"name": "stripe", "system": "greenhouse", "slug": "stripe"},
                  {"name": "plaid", "system": "ashby", "slug": "plaid"}]
        bodies = {"greenhouse": gh_body((1, "Data Engineer", "&lt;p&gt;SQL&lt;/p&gt;")),
                  "ashby": ashby_body(("a-1", "Data Engineer", "<p>SQL</p>"))}
        calls = []

        def transport(url, timeout):
            calls.append(url)
            return 200, bodies["ashby" if "ashbyhq" in url else "greenhouse"]

        with no_network():
            result = loop.run_loop(boards, loop.BUDGETS, policy=policy.Policy(self.root), transport=transport,
                                   clock=lambda: 0.0, sleep=lambda s: None, urls=urls, run_id="SIMULATED-g6")
        self.assertEqual(calls, ["https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true",
                                 "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true",
                                 "https://api.ashbyhq.com/posting-api/job-board/plaid"])
        self.assertEqual(result.budgets["requests_used"], 3)
        self.assertEqual(result.exit, "finished")


if __name__ == "__main__":
    unittest.main()
