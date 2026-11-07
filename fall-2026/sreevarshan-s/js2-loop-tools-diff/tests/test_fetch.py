import os
import socket
import unittest
import urllib.error
from unittest import mock

from js2 import fetch, policy
from tests.helpers import FakeResponse, SandboxTestCase, greenhouse_body, http_error, lever_body

URLOPEN = "js2.fetch.urllib.request.urlopen"


class FetchErrorTest(SandboxTestCase):
    def assert_error(self, exc, status_code, retriable, kind):
        self.assertEqual(exc.status_code, status_code)
        self.assertIs(exc.retriable, retriable)
        self.assertEqual(exc.kind, kind)
        self.assertEqual(exc.board, "greenhouse:stripe")

    def test_4xx_is_not_retriable(self):
        with mock.patch(URLOPEN, side_effect=http_error("u", 404)):
            with self.assertRaises(fetch.BoardFetchError) as cm:
                fetch.fetch_greenhouse("stripe")
        self.assert_error(cm.exception, 404, False, "http")

    def test_5xx_is_retriable(self):
        with mock.patch(URLOPEN, side_effect=http_error("u", 503)):
            with self.assertRaises(fetch.BoardFetchError) as cm:
                fetch.fetch_greenhouse("stripe")
        self.assert_error(cm.exception, 503, True, "http")

    def test_timeout_is_retriable(self):
        for exc in (socket.timeout("timed out"), TimeoutError(), urllib.error.URLError(socket.timeout())):
            with mock.patch(URLOPEN, side_effect=exc):
                with self.assertRaises(fetch.BoardFetchError) as cm:
                    fetch.fetch_greenhouse("stripe")
            self.assert_error(cm.exception, None, True, "timeout")

    def test_non_json_body_is_not_retriable(self):
        with mock.patch(URLOPEN, return_value=FakeResponse(b"<html>oops</html>")):
            with self.assertRaises(fetch.BoardFetchError) as cm:
                fetch.fetch_greenhouse("stripe")
        self.assert_error(cm.exception, 200, False, "bad_json")


class FetchSuccessTest(SandboxTestCase):
    def test_raw_response_saved_byte_for_byte(self):
        body =b'{"jobs": [{"id": 1}], "note": "caf\xc3\xa9 \xe2\x80\x94"}  \n'
        with mock.patch(URLOPEN, return_value=FakeResponse(body)):
            result = fetch.fetch_greenhouse("stripe")
        self.assertTrue(result["raw_path"].startswith(os.path.join(self.output, "raw") + os.sep))
        self.assertTrue(result["raw_path"].endswith("-greenhouse-stripe.json"))
        with open(result["raw_path"], "rb") as f:
            self.assertEqual(f.read(), body)
        self.assertEqual(result["data"]["jobs"], [{"id": 1}])

    def test_request_url_and_user_agent(self):
        with mock.patch(URLOPEN, return_value=FakeResponse(lever_body("a"))) as urlopen:
            fetch.fetch_lever("spotify", timeout=7)
        self.assertEqual(urlopen.call_count, 1)
        req = urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.lever.co/v0/postings/spotify?mode=json")
        self.assertEqual(req.get_header("User-agent"), "INFO7375-JS2-student-agent")
        self.assertEqual(req.get_method(), "GET")
        self.assertEqual(urlopen.call_args[1]["timeout"], 7)

    def test_token_cannot_change_host(self):
        self.assertEqual(fetch.greenhouse_url("x/../@evil.com"),
                         "https://boards-api.greenhouse.io/v1/boards/x%2F..%2F%40evil.com/jobs")


class FetchPolicyOrderTest(SandboxTestCase):
    def test_blocked_request_never_touches_network(self):
        with mock.patch("js2.policy.allow_request", return_value=False), \
                mock.patch(URLOPEN) as urlopen, \
                mock.patch("socket.socket.connect") as connect:
            with self.assertRaises(fetch.BoardFetchError) as cm:
                fetch.fetch_greenhouse("stripe")
        urlopen.assert_not_called()
        connect.assert_not_called()
        self.assertEqual(cm.exception.kind, "blocked")
        self.assertFalse(cm.exception.retriable)

    def test_allow_request_checked_before_urlopen(self):
        calls = []
        real_allow = policy.allow_request

        def allow(url):
            calls.append("allow_request")
            return real_allow(url)

        def urlopen(*a, **k):
            calls.append("urlopen")
            return FakeResponse(greenhouse_body(1))

        with mock.patch("js2.policy.allow_request", side_effect=allow), mock.patch(URLOPEN, side_effect=urlopen):
            fetch.fetch_greenhouse("stripe")
        self.assertEqual(calls, ["allow_request", "urlopen"])


if __name__ == "__main__":
    unittest.main()
