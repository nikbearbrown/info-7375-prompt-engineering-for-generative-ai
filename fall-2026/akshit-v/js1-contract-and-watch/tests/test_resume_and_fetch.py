"""Refuses (1) and (2): the allow-list and the persona check. No network is used."""
import copy
import unittest

from agent.fetch import HostNotAllowed, _AllowListRedirects, check_allowed, check_board
from agent.resume import is_555_phone, validate_resume
from tests.helpers import JACK


class AllowList(unittest.TestCase):
    def test_board_host_allowed(self):
        check_allowed("https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true")

    def test_other_hosts_refused(self):
        for url in ("https://api.lever.co/v0/postings/figma",
                    "https://boards-api.greenhouse.io.evil.example/v1",
                    "http://boards-api.greenhouse.io/v1/boards/figma/jobs",  # not https
                    "https://www.linkedin.com/jobs"):
            with self.assertRaises(HostNotAllowed, msg=url):
                check_allowed(url)

    def test_redirect_off_allow_list_refused(self):
        with self.assertRaises(HostNotAllowed):
            _AllowListRedirects().redirect_request(None, None, 302, "Found", {}, "https://example.com/elsewhere")

    def test_board_name_must_be_token(self):
        for bad in ("figma/../x", "figma?x=1", "Figma Inc", ""):
            with self.assertRaises(ValueError, msg=bad):
                check_board(bad)


class Persona(unittest.TestCase):
    def test_jack_is_valid(self):
        self.assertEqual(validate_resume(JACK), [])

    def test_real_looking_email_refused_without_echoing_it(self):
        d = copy.deepcopy(JACK)
        d["email"] = "someone.real@gmail.com"
        problems = validate_resume(d)
        self.assertEqual(problems, ["email does not end in @example.com"])
        self.assertNotIn("gmail", " ".join(problems))

    def test_non_555_phone_refused(self):
        d = copy.deepcopy(JACK)
        d["phone"] = "(617) 373-2000"
        self.assertEqual(validate_resume(d), ["phone is not a 555 number"])

    def test_phone_formats(self):
        for ok in ("(617) 555-0142", "617-555-0142", "+1 617 555 0142", "555-0142"):
            self.assertTrue(is_555_phone(ok), ok)
        for bad in ("617-373-2000", "555", "5555555555555"):
            self.assertFalse(is_555_phone(bad), bad)

    def test_missing_and_unexpected_fields(self):
        d = copy.deepcopy(JACK)
        del d["skills"]
        d["ssn"] = "x"
        problems = validate_resume(d)
        self.assertIn("missing field: skills", problems)
        self.assertIn("unexpected field: ssn", problems)


if __name__ == "__main__":
    unittest.main()
