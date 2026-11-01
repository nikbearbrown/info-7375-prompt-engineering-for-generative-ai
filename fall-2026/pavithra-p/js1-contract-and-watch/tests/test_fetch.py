"""CONTRACT.md Refuses 1 (allow-listed host only) and 3 (no applying, messaging or logging in)."""
import unittest
import urllib.request

from agent import fetch


class SpyOpener:
    """Records every request instead of connecting."""

    def __init__(self, body=b'{"jobs": []}'):
        self.requests, self.body = [], body

    def open(self, request, timeout=None):
        self.requests.append(request)
        spy = self

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return spy.body

        return Response()


class FetchTests(unittest.TestCase):
    def test_fetch_refuses_other_hosts(self):
        spy = SpyOpener()
        for url in ("https://example.com/jobs", "https://api.lever.co/v0/postings/x",
                    "https://boards-api.greenhouse.io.evil.example/v1/boards/pinterest/jobs"):
            with self.assertRaises(fetch.RefusedHost):
                fetch.fetch(url, opener=spy)
        self.assertEqual(spy.requests, [], "a refused host must never be contacted")

    def test_fetch_refuses_plain_http(self):
        with self.assertRaises(fetch.RefusedHost):
            fetch.fetch("http://boards-api.greenhouse.io/v1/boards/pinterest/jobs", opener=SpyOpener())

    def test_fetch_sends_only_get_requests(self):
        spy = SpyOpener(b'{"jobs": [{"id": 1}]}')
        body = fetch.fetch("https://boards-api.greenhouse.io/v1/boards/pinterest/jobs?content=true", opener=spy)
        self.assertEqual(body, b'{"jobs": [{"id": 1}]}')
        (request,) = spy.requests
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data, "the agent never sends a body (no applying or messaging)")
        self.assertNotIn("Authorization", request.headers, "the agent never logs in")

    def test_redirect_to_other_host_refused(self):
        handler = fetch._AllowListRedirects()
        request = urllib.request.Request("https://boards-api.greenhouse.io/v1/boards/pinterest/jobs")
        with self.assertRaises(fetch.RefusedHost):
            handler.redirect_request(request, None, 302, "Found", {}, "https://tracker.example.com/x")


if __name__ == "__main__":
    unittest.main()
