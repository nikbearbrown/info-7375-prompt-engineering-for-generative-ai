"""Turning each system's answer into jobs the rule can read. Every response here is CONSTRUCTED."""
import json
import unittest

from agent import ats, rule
from tests.fakes import LEVER_404, PERSONA, ashby, greenhouse, lever


class AtsTests(unittest.TestCase):
    def test_board_urls_use_the_three_allowed_hosts(self):
        self.assertTrue(ats.board_url("greenhouse", "pinterest").startswith("https://boards-api.greenhouse.io/"))
        self.assertTrue(ats.board_url("lever", "spotify").startswith("https://api.lever.co/"))
        self.assertTrue(ats.board_url("ashby", "ramp").startswith("https://api.ashbyhq.com/"))
        with self.assertRaises(ats.BadData):
            ats.board_url("workday", "x")

    def test_each_system_gives_jobs_the_rule_can_judge(self):
        for system, body in (("greenhouse", greenhouse(1)), ("lever", lever("a")), ("ashby", ashby("x"))):
            jobs = ats.parse(system, body)
            self.assertEqual(len(jobs), 1, system)
            self.assertTrue(rule.judge(jobs[0], PERSONA).checks["location"], f"{system}: a US location is kept")

    def test_lever_404_body_is_bad_data_not_an_empty_list(self):
        with self.assertRaises(ats.BadData):
            ats.parse("lever", LEVER_404)

    def test_wrong_shapes_and_non_json_are_bad_data(self):
        for system, body in (("greenhouse", b"[]"), ("ashby", b'{"apiVersion": "1"}'), ("lever", b"not json")):
            with self.assertRaises(ats.BadData, msg=system):
                ats.parse(system, body)

    def test_ashby_skips_unlisted_jobs(self):
        data = json.loads(ashby("x", "y"))
        data["jobs"][1]["isListed"] = False
        self.assertEqual([j["id"] for j in ats.parse("ashby", json.dumps(data).encode())], ["x"])


if __name__ == "__main__":
    unittest.main()
