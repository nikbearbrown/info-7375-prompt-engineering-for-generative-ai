"""JS3's collection changes: full posting text from each system, gzip-saved raw responses, the
frozen corpus, and the code's numbers against FILTER.md."""
import gzip
import json
import os
import re
import unittest

from helpers import ASHBY, GH, GH_NAME, LEVER, ROOT, board, gh_name, make, stamp

import adapters
import corpus
import loop
import policy

FILTER = open(os.path.join(ROOT, "FILTER.md"), encoding="utf-8").read()

GH_FULL = json.dumps({"jobs": [{
    "id": 11, "title": "Data Analyst", "absolute_url": "https://example.invalid/11",
    "location": {"name": "New York, NY"}, "offices": [{"name": "NYC", "location": "New York, NY"}],
    "departments": [{"name": "Analytics"}],
    "content": "&lt;p&gt;Use &lt;strong&gt;SQL&lt;/strong&gt; &amp;amp; Tableau.&lt;/p&gt;&lt;ul&gt;&lt;li&gt;1-2 years&lt;/li&gt;&lt;/ul&gt;",
}]}).encode()
ASHBY_FULL = json.dumps({"jobs": [{
    "id": "a1", "title": "BI Analyst", "jobUrl": "https://example.invalid/a1", "location": "Remote",
    "secondaryLocations": [{"location": "Boston, MA"}], "workplaceType": "Remote", "department": "Data",
    "address": {"postalAddress": {"addressCountry": "United States"}},
    "descriptionPlain": "Build   dashboards.\n\n\nExcel required.",
}]}).encode()
LEVER_FULL = json.dumps([{
    "id": "l1", "text": "Business Analyst", "hostedUrl": "https://example.invalid/l1", "country": "US",
    "workplaceType": "hybrid", "categories": {"location": "Denver, CO", "allLocations": ["Denver, CO", "Austin, TX"],
                                              "team": "Ops"},
    "descriptionPlain": "About the role.", "lists": [{"text": "Requirements", "content": "<li>Python</li><li>3+ years</li>"}],
    "additionalPlain": "We sponsor visas.",
}]).encode()


class FullText(unittest.TestCase):
    def test_greenhouse_escaped_html_becomes_plain_text(self):
        [p] = adapters.parse({"system": "greenhouse"}, GH_FULL)
        self.assertEqual(set(p), set(adapters.FIELDS))
        self.assertEqual(p["text"], "Use SQL & Tableau.\n1-2 years")
        self.assertEqual((p["department"], p["locations"]), ("Analytics", ["New York, NY", "New York, NY"]))

    def test_ashby_plain_description_and_location_fields(self):
        [p] = adapters.parse({"system": "ashby"}, ASHBY_FULL)
        self.assertEqual(p["text"], "Build dashboards.\nExcel required.")
        self.assertEqual((p["country"], p["workplace"], p["locations"]),
                         ("United States", "Remote", ["Remote", "Boston, MA"]))

    def test_lever_lists_and_additional_text_are_kept(self):
        [p] = adapters.parse({"system": "lever"}, LEVER_FULL)
        self.assertEqual(p["text"], "About the role.\nRequirements\nPython\n3+ years\nWe sponsor visas.")
        self.assertEqual((p["country"], p["department"]), ("US", "Ops"))

    def test_missing_description_is_none_not_an_empty_string(self):
        body = json.dumps({"jobs": [{"id": 1, "title": "Data Analyst", "location": {"name": "US"}}]}).encode()
        [p] = adapters.parse({"system": "greenhouse"}, body)
        self.assertIsNone(p["text"])
        self.assertIsNone(p["department"])

    def test_wrong_shapes_are_parse_errors_never_empty_lists(self):
        for system, body in (("greenhouse", b'{"meta": {}}'), ("ashby", b"Not Found"), ("lever", b'{"ok": false}'),
                             ("greenhouse", b'{"jobs": [{"title": "no id"}]}')):
            with self.subTest(system=system, body=body), self.assertRaises(adapters.ParseError):
                adapters.parse({"system": system}, body)

    def test_board_tokens_must_be_plain_names(self):
        for token in ("abacus/../x", "a?b=c", "", "UPPER", "a b"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                adapters.board_url({"system": "greenhouse", "token": token})


class FrozenCorpus(unittest.TestCase):
    BOARDS = [board("greenhouse", "abacusinsights"), board("ashby", "valon"), board("lever", "xsolla"),
              board("ashby", "valonn")]

    def collect(self):
        script = {GH_NAME.format("abacusinsights"): [(200, gh_name("X"))], GH.format("abacusinsights"): [(200, GH_FULL)],
                  ASHBY.format("valon"): [(200, ASHBY_FULL)], LEVER.format("xsolla"): [(200, LEVER_FULL)],
                  ASHBY.format("valonn"): [(404, b"Not Found")]}
        root, tools = make(self.BOARDS, script)
        run_dir, s = loop.run(tools, now=stamp(), sleep=lambda _: None)
        with open(os.path.join(root, "config", "corpus.json"), "w") as f:
            json.dump({"run": run_dir}, f)
        return root, tools, run_dir, s

    def test_raw_200_responses_are_gzip_and_decompress_to_the_exact_body(self):
        root, _, run_dir, s = self.collect()
        with open(os.path.join(root, run_dir, "raw", "lever_xsolla.json.gz"), "rb") as f:
            self.assertEqual(gzip.decompress(f.read()), LEVER_FULL)
        self.assertTrue(os.path.exists(os.path.join(root, run_dir, "raw", "ashby_valonn.http404.txt")))
        self.assertEqual(s["exit"], "incomplete")

    def test_corpus_reads_every_ok_board_and_never_a_failed_one(self):
        _, tools, run_dir, _ = self.collect()
        run, postings = corpus.load(tools)
        self.assertEqual(run, run_dir)
        self.assertEqual([p["key"] for p in postings],
                         ["ashby/valon/a1", "greenhouse/abacusinsights/11", "lever/xsolla/l1"])
        self.assertNotIn("ashby/valonn", {p["board"] for p in postings})

    def test_run_json_keeps_no_posting_text(self):
        root, tools, _, _ = self.collect()
        tools.script = {GH_NAME.format("abacusinsights"): [(200, gh_name("X"))],
                        GH.format("abacusinsights"): [(200, GH_FULL.replace(b'"id": 11', b'"id": 12'))],
                        ASHBY.format("valon"): [(200, ASHBY_FULL)], LEVER.format("xsolla"): [(200, LEVER_FULL)],
                        ASHBY.format("valonn"): [(404, b"Not Found")]}
        run_dir, s = loop.run(tools, now=stamp(), sleep=lambda _: None)
        [new] = s["results"]["greenhouse/abacusinsights"]["new"]
        self.assertEqual(set(new), set(loop.SUMMARY_FIELDS))


class FilterNumbers(unittest.TestCase):
    """A budget changes only by a new FILTER.md version: the code must match the file."""

    def test_collection_budget_matches_filter(self):
        m = re.search(r"\*\*Collection budget:\*\* at most (\d+) boards, (\d+) requests, and (\d+) seconds", FILTER)
        self.assertEqual((loop.BUDGETS["boards"], loop.BUDGETS["requests"], loop.BUDGETS["seconds"]),
                         tuple(int(x) for x in m.groups()))

    def test_write_approval_limit_matches_filter(self):
        m = re.search(r"any single write over (\d+) MB", FILTER)
        self.assertEqual(policy.MAX_WRITE_BYTES, int(m.group(1)) * 1024 * 1024)

    def test_js2_policy_numbers_are_unchanged(self):
        # FILTER.md: "JS2's permission policy carries over unchanged" (JS2 GATE.md at 41ae85c).
        self.assertEqual(policy.ALLOWED_HOSTS, {"boards-api.greenhouse.io", "api.ashbyhq.com", "api.lever.co"})
        self.assertEqual(policy.WRITE_DIRS, ("runs", "state"))
        self.assertEqual(loop.RETRY_DELAY, 2)

    def test_config_has_the_twelve_filter_boards(self):
        with open(os.path.join(ROOT, "config", "boards.json")) as f:
            configured = {f"{b['system']}/{b['token']}" for b in json.load(f)["boards"]}
        table = set(re.findall(r"\| (Greenhouse|Ashby|Lever) \| `([a-z0-9-]+)` \|", FILTER))
        self.assertEqual(configured, {f"{s.lower()}/{t}" for s, t in table})
        self.assertEqual(len(configured), 12)


if __name__ == "__main__":
    unittest.main()
