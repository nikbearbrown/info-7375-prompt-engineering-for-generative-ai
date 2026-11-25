"""Greenhouse and Ashby parsing into {system, board, id, title, location, content}, on CONSTRUCTED bodies."""
import unittest

from tests import helpers, js2_helpers as h


class Providers(helpers.ContractTest):
    modules = ("agent2.providers",)

    def test_urls_match_the_gate(self):
        self.assertEqual(self.providers.url_for("greenhouse", "faire"), h.URLS["faire"])
        self.assertEqual(self.providers.url_for("ashby", "poshmark"), h.URLS["ashby_poshmark"])
        with self.assertRaises(ValueError):
            self.providers.url_for("lever", "gopuff")

    def test_greenhouse_parse_keys_ids(self):
        jobs = self.providers.parse("greenhouse", "faire", h.gh_body([h.gh_job(7, location="Chicago, IL")]))
        self.assertEqual(jobs, [{"system": "greenhouse", "board": "faire", "id": "greenhouse:faire:7",
                                 "title": "Data Analyst", "location": "Chicago, IL", "content": "Python and SQL"}])

    def test_ashby_string_ids_are_keyed(self):
        jobs = self.providers.parse("ashby", "poshmark", h.ashby_body([h.ashby_job(5)]))
        self.assertEqual(jobs[0]["id"], "ashby:poshmark:00000000-0000-0000-0000-000000000005")
        self.assertEqual(jobs[0]["location"], "San Francisco, CA")
        self.assertIn("Python", jobs[0]["content"])

    def test_empty_board_parses_to_empty_list(self):
        self.assertEqual(self.providers.parse("greenhouse", "poshmark", b'{"jobs":[],"meta":{"total":0}}'), [])

    def test_bad_responses(self):
        for system, body in [("greenhouse", b"<html>not json</html>"), ("greenhouse", b'{"nojobs": []}'),
                             ("greenhouse", b'{"jobs": "x"}'), ("greenhouse", b'{"jobs": [{"title": "t"}]}'),
                             ("greenhouse", b'{"jobs": [{"id": "7", "title": "t"}]}'),
                             ("ashby", b"Not Found"), ("ashby", b'{"jobs": [{"id": 7, "title": "t"}]}'),
                             ("greenhouse", b"[]")]:
            with self.subTest(system=system, body=body), self.assertRaises(self.providers.BadResponse):
                self.providers.parse(system, "b", body)

    def test_judge_view_fits_the_js1_rule_judge(self):
        job = self.providers.parse("greenhouse", "faire", h.gh_body([h.gh_job(7)]))[0]
        view = self.providers.judge_view(job)
        self.assertEqual(view["location"], {"name": "New York City, NY"})
        self.assertEqual(view["id"], "greenhouse:faire:7")


if __name__ == "__main__":
    unittest.main()
