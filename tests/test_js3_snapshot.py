"""JS3 Step 2: the snapshot URL and the shape of a Greenhouse list WITH descriptions (FILTER.md section 3, text rule X1)."""
import json
import unittest

from jsagent import policy, providers


class SnapshotUrlTest(unittest.TestCase):
    def setUp(self):
        self.allow = policy.load_allowlist()

    def test_greenhouse_snapshot_asks_for_content(self):
        url = providers.snapshot_url("greenhouse", "samsara")
        self.assertEqual(url, "https://boards-api.greenhouse.io/v1/boards/samsara/jobs?content=true")
        policy.check_url(url, self.allow)  # same host, still a GET: the JS2 policy accepts it

    def test_lever_snapshot_is_the_js2_list_url(self):
        self.assertEqual(providers.snapshot_url("lever", "palantir"), providers.list_url("lever", "palantir"))

    def test_js2_list_url_unchanged(self):
        self.assertEqual(providers.list_url("greenhouse", "samsara"), "https://boards-api.greenhouse.io/v1/boards/samsara/jobs")

    def test_bad_board_refused(self):
        for board in ("../x", "Samsara", "a b", ""):
            with self.assertRaises(ValueError):
                providers.snapshot_url("greenhouse", board)


class GreenhouseContentShapeTest(unittest.TestCase):
    def test_escaped_html_content_becomes_plain_text(self):
        body = json.dumps({"jobs": [{"id": 1, "title": "Data Engineer", "location": {"name": "Boston, MA"},
                                     "content": "&lt;p&gt;Python &amp;amp; SQL&lt;/p&gt;&lt;ul&gt;&lt;li&gt;dbt&lt;/li&gt;&lt;/ul&gt;",
                                     "absolute_url": "https://x", "updated_at": ""}], "meta": {"total": 1}})
        [p] = providers.parse_list("greenhouse", body, "samsara")
        self.assertEqual(p["content"], "Python & SQL dbt")

    def test_missing_content_is_empty_not_an_error(self):
        body = json.dumps({"jobs": [{"id": 2, "title": "Data Analyst", "location": {"name": "Remote"}}]})
        [p] = providers.parse_list("greenhouse", body, "toast")
        self.assertEqual(p["content"], "")  # the filter must route this to "cannot tell" (FILTER.md section 3)


if __name__ == "__main__":
    unittest.main()
