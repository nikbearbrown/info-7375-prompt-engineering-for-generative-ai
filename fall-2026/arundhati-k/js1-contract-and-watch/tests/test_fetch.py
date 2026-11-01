import io
import unittest
import urllib.request

from jsagent.fetch import AllowListRedirectHandler, HostNotAllowed, board_url, check_url, fetch


class FakeResponse(io.BytesIO):
    def __init__(self, url, body=b'{"jobs": []}'):
        super().__init__(body)
        self._url = url

    def geturl(self):
        return self._url


class RecordingOpener:
    def __init__(self, final_url=None):
        self.requests, self.final_url = [], final_url

    def open(self, request, timeout=None):
        self.requests.append(request)
        return FakeResponse(self.final_url or request.full_url)


class AllowListTests(unittest.TestCase):
    def test_board_url_is_on_allow_list(self):
        self.assertEqual(check_url(board_url("stripe")), "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true")

    def test_other_hosts_refused(self):
        for url in ["https://api.lever.co/v0/postings/stripe", "https://boards-api.greenhouse.io.evil.example/x",
                    "https://stripe.com/jobs", "https://user:pw@boards-api.greenhouse.io/v1/boards/stripe/jobs"]:
            with self.subTest(url=url), self.assertRaises(HostNotAllowed):
                check_url(url)

    def test_plain_http_refused(self):
        with self.assertRaises(HostNotAllowed):
            check_url("http://boards-api.greenhouse.io/v1/boards/stripe/jobs")

    def test_fetch_refuses_before_any_request(self):
        opener = RecordingOpener()
        with self.assertRaises(HostNotAllowed):
            fetch("https://example.com/jobs", opener=opener)
        self.assertEqual(opener.requests, [])

    def test_fetch_is_get_only(self):
        opener = RecordingOpener()
        fetch(board_url("stripe"), opener=opener)
        self.assertEqual([r.get_method() for r in opener.requests], ["GET"])

    def test_board_slug_cannot_smuggle_a_path(self):
        for bad in ["stripe/../../x", "Stripe", "stripe?x=1", ""]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                board_url(bad)


class RedirectTests(unittest.TestCase):
    def setUp(self):
        self.handler = AllowListRedirectHandler()
        self.req = urllib.request.Request(board_url("stripe"))

    def test_redirect_off_allow_list_refused(self):
        with self.assertRaises(HostNotAllowed):
            self.handler.redirect_request(self.req, None, 302, "Found", {}, "https://evil.example.com/jobs")

    def test_redirect_within_allow_list_followed(self):
        new = self.handler.redirect_request(self.req, None, 301, "Moved", {}, "https://boards-api.greenhouse.io/v1/boards/stripe/jobs")
        self.assertEqual(new.full_url, "https://boards-api.greenhouse.io/v1/boards/stripe/jobs")

    def test_final_url_off_allow_list_refused(self):
        with self.assertRaises(HostNotAllowed):
            fetch(board_url("stripe"), opener=RecordingOpener(final_url="https://evil.example.com/"))


if __name__ == "__main__":
    unittest.main()
