import unittest
import urllib.request

from js1 import fetch
from js1.allowlist import HostNotAllowed, check_url


class AllowListTests(unittest.TestCase):
    def test_board_url_is_allowed(self):
        url = "https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true"
        self.assertEqual(check_url(url), url)

    def test_refuses_other_hosts(self):
        for url in [
            "https://api.lever.co/v0/postings/palantir?mode=json",
            "https://boards.greenhouse.io/databricks",
            "https://boards-api.greenhouse.io.evil.example/v1/boards/databricks/jobs",
            "https://evil.example/boards-api.greenhouse.io/v1/boards/databricks/jobs",
            "https://boards-api.greenhouse.io@evil.example/v1/boards/databricks/jobs",
            "http://boards-api.greenhouse.io/v1/boards/databricks/jobs",
            "https://boards-api.greenhouse.io:8443/v1/boards/databricks/jobs",
        ]:
            with self.subTest(url=url), self.assertRaises(HostNotAllowed):
                check_url(url)

    def test_fetch_refuses_before_any_network_call(self):
        calls = []

        class Opener:
            def open(self, *a, **k):
                calls.append(a)
                raise AssertionError("network must not be reached")

        original = fetch.BOARD_URL
        fetch.BOARD_URL = "https://api.lever.co/v0/postings/{token}?mode=json"
        try:
            with self.assertRaises(HostNotAllowed):
                fetch.fetch_board("databricks", opener=Opener())
        finally:
            fetch.BOARD_URL = original
        self.assertEqual(calls, [])

    def test_redirect_off_the_allow_list_is_refused(self):
        handler = fetch._AllowListRedirects()
        req = urllib.request.Request(fetch.board_url("databricks"))
        with self.assertRaises(HostNotAllowed):
            handler.redirect_request(req, None, 302, "Found", {}, "https://evil.example/jobs")

    def test_board_token_cannot_change_the_path(self):
        for token in ["databricks/../x", "databricks?x=1", "", "Databricks"]:
            with self.subTest(token=token), self.assertRaises(ValueError):
                fetch.board_url(token)


if __name__ == "__main__":
    unittest.main()
