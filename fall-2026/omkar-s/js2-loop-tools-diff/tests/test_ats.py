"""ATS adapters: URL building and the documented field mapping (constructed fixtures)."""
import unittest

from agent import ats, policy, rule
from tests.helpers import PERSONA, fixture_bytes
from agent import persona


class Urls(unittest.TestCase):
    def test_urls_are_on_the_allow_list(self):
        for a, s in (("greenhouse", "klaviyo"), ("ashby", "linear"), ("lever", "spotify"), ("ashby", "Jasper AI")):
            self.assertEqual(policy.check_request("GET", ats.board_url(a, s))["decision"], policy.ALLOW)

    def test_slug_cannot_inject_a_path_or_host(self):
        for bad in ("../x", "a/b", "evil.example/", "a?b=1", "", "x" * 80, "@evil"):
            with self.assertRaises(ats.BadSlug, msg=bad):
                ats.board_url("greenhouse", bad)

    def test_unknown_ats(self):
        with self.assertRaises(ats.BadSlug):
            ats.board_url("workday", "x")

    def test_board_key_case_folds(self):
        self.assertEqual(ats.board_key("Greenhouse", " Klaviyo "), ats.board_key("greenhouse", "klaviyo"))


class Parse(unittest.TestCase):
    def setUp(self):
        self.resume = persona.load(PERSONA)

    def test_greenhouse(self):
        ps = ats.parse("greenhouse", fixture_bytes("greenhouse-2.json"))
        self.assertEqual([p["id"] for p in ps], ["101", "102"])
        self.assertEqual(rule.judge(ps[0], self.resume)["verdict"], "relevant")
        self.assertEqual(rule.judge(ps[1], self.resume)["verdict"], "not_relevant")

    def test_ashby_mapping(self):
        ps = ats.parse("ashby", fixture_bytes("ashby-2.json"))
        self.assertEqual([p["id"] for p in ps], ["a-1", "a-2"])  # unlisted a-3 dropped
        self.assertEqual(ps[0]["location"]["name"], "North America; Remote (United States)")
        self.assertEqual(ps[1]["location"]["name"], "Europe; London; Remote (European Union)")
        self.assertEqual(rule.judge(ps[0], self.resume)["verdict"], "relevant")  # US remote, TS/Node/PostgreSQL
        self.assertEqual(rule.judge(ps[1], self.resume)["verdict"], "not_relevant")

    def test_lever_mapping(self):
        ps = ats.parse("lever", fixture_bytes("lever-2.json"))
        self.assertEqual(ps[0]["location"]["name"], "New York, NY; Boston, MA")
        self.assertEqual(ps[0]["offices"], [{"location": "United States"}])
        self.assertIn("Java and Docker", ps[0]["content"])
        self.assertEqual(rule.judge(ps[0], self.resume)["verdict"], "relevant")
        self.assertEqual(ps[1]["location"]["name"], "London; Remote (GB)")
        self.assertEqual(rule.judge(ps[1], self.resume)["verdict"], "not_relevant")

    def test_empty_list_parses_to_empty_list_not_none(self):
        self.assertEqual(ats.parse("greenhouse", fixture_bytes("greenhouse-empty.json")), [])
        self.assertEqual(ats.parse("lever", b"[]"), [])

    def test_bad_bodies(self):
        for a, body in (("greenhouse", b"not json"), ("greenhouse", b"[]"), ("ashby", b'{"x":1}'),
                        ("lever", b'{"jobs":[]}'), ("greenhouse", b'{"jobs":[{"title":"no id"}]}')):
            with self.assertRaises(ats.BadResponse, msg=(a, body)):
                ats.parse(a, body)


if __name__ == "__main__":
    unittest.main()
