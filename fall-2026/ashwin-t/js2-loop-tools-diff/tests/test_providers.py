"""Fixed URL templates and strict parsers for Greenhouse, Ashby and Lever. Offline."""
from __future__ import annotations

import json
import unittest

from jobloop import providers
from tests.helpers import ashby_body, gh_body, lever_body


class TestEndpoints(unittest.TestCase):
    def test_canonical_urls(self):
        self.assertEqual(providers.endpoint("greenhouse", "klaviyo"),
                         "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true")
        self.assertEqual(providers.endpoint("ashby", "notion"), "https://api.ashbyhq.com/posting-api/job-board/notion")
        self.assertEqual(providers.endpoint("lever", "palantir"), "https://api.lever.co/v0/postings/palantir?mode=json")

    def test_board_names_cannot_smuggle_paths_hosts_or_queries(self):
        for bad in ("../x", "a/b", "klaviyo?x=1", "evil.example", "", "-a", "a-", "A B", "a" * 65, 7, None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                providers.endpoint("greenhouse", bad)

    def test_unknown_provider_is_refused(self):
        with self.assertRaises(ValueError):
            providers.endpoint("workday", "acme")


class TestParsers(unittest.TestCase):
    def test_each_provider_parses_to_the_common_shape_with_board_scoped_keys(self):
        cases = [("greenhouse", gh_body([5])), ("ashby", ashby_body(["5"])), ("lever", lever_body(["5"]))]
        for provider, body in cases:
            with self.subTest(provider=provider):
                [p] = providers.parse(provider, "b", body)
                self.assertEqual((p["key"], p["id"]), (f"{provider}/b/5", "5"))
                self.assertTrue(p["title"])

    def test_empty_listing_parses_as_empty_not_as_an_error(self):
        self.assertEqual(providers.parse("greenhouse", "b", gh_body([])), [])
        self.assertEqual(providers.parse("lever", "b", b"[]"), [])

    def test_malformed_and_wrong_schema_are_errors_never_empty_lists(self):
        cases = [("greenhouse", b"{nope", "malformed-json"), ("greenhouse", b'{"error": "not found"}', "invalid-schema"),
                 ("ashby", b"[]", "invalid-schema"), ("lever", b'{"ok": false}', "invalid-schema"),
                 ("greenhouse", json.dumps({"jobs": [{"id": "1", "title": "x", "content": ""}]}).encode(), "invalid-schema"),
                 ("greenhouse", json.dumps({"jobs": [{"id": True, "title": "x", "content": ""}]}).encode(), "invalid-schema")]
        for provider, body, kind in cases:
            with self.subTest(provider=provider, body=body[:30]):
                with self.assertRaises(providers.ParseError) as ctx:
                    providers.parse(provider, "b", body)
                self.assertEqual(ctx.exception.kind, kind)

    def test_duplicate_ids_within_a_board_are_refused(self):
        with self.assertRaises(providers.ParseError):
            providers.parse("ashby", "b", ashby_body(["1", "1"]))

    def test_greenhouse_without_content_is_refused(self):
        body = json.dumps({"jobs": [{"id": 1, "title": "Software Engineer"}]}).encode()
        with self.assertRaises(providers.ParseError):
            providers.parse("greenhouse", "b", body)


if __name__ == "__main__":
    unittest.main()
