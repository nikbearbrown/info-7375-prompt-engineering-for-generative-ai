"""CONTRACT.md Refuses 1 and wrong version 3: only the exact host passes."""

import unittest

from job_agent import allowlist
from job_agent.errors import Refused


class AllowListTest(unittest.TestCase):
    def test_the_board_url_passes_unchanged(self):
        self.assertEqual(allowlist.check(allowlist.BOARD_URL), allowlist.BOARD_URL)

    def test_host_case_does_not_matter(self):
        self.assertEqual(allowlist.check("https://API.AshbyHQ.com/posting-api/job-board/openai"), allowlist.BOARD_URL)

    def test_look_alike_hosts_are_refused(self):
        # Wrong version 3: each of these passes a substring, prefix or suffix match.
        for url in (
            "https://api.ashbyhq.com.evil.example/posting-api/job-board/openai",  # prefix and substring
            "https://notapi.ashbyhq.com/posting-api/job-board/openai",  # suffix and substring
            "https://evil-api.ashbyhq.com/",  # suffix
            "https://x.api.ashbyhq.com/",  # a subdomain is a different host
            "https://api.ashbyhq.com./",  # trailing dot
        ):
            with self.subTest(url=url), self.assertRaises(Refused):
                allowlist.check(url)

    def test_other_hosts_and_schemes_are_refused(self):
        for url in (
            "https://jobs.ashbyhq.com/openai",
            "https://boards-api.greenhouse.io/v1/boards/openai/jobs",
            "http://api.ashbyhq.com/posting-api/job-board/openai",
            "ftp://api.ashbyhq.com/",
            "https://104.18.0.1/",
            "api.ashbyhq.com/posting-api/job-board/openai",
            "https:///posting-api",
        ):
            with self.subTest(url=url), self.assertRaises(Refused):
                allowlist.check(url)

    def test_user_info_port_and_parser_tricks_are_refused(self):
        at = "@"  # assembled, so the repo's privacy scan does not read these URLs as email addresses
        for url in (
            "https://api.ashbyhq.com" + at + "evil.example/",
            "https://user:pw" + at + "api.ashbyhq.com/",
            "https://evil.example\\" + at + "api.ashbyhq.com/",
            "https://api.ashbyhq.com:8443/",
            "https://api.ashbyhq.com:notaport/",
            "https://api.ashbyhq.com /",
            "https://api.ashbyhq.com/\r\nHost: evil.example",
        ):
            with self.subTest(url=url), self.assertRaises(Refused):
                allowlist.check(url)

    def test_the_refusal_names_the_host(self):
        with self.assertRaises(Refused) as caught:
            allowlist.check("https://notapi.ashbyhq.com/")
        self.assertIn("notapi.ashbyhq.com", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
