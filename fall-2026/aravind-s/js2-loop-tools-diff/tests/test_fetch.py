"""CONTRACT.md Refuses 1 and 4: the fetch checks the allow-list before any connection, follows no
redirect and ignores proxy settings. No test here touches the network: a recording opener stands in."""

import io
import os
import unittest
import urllib.error
import urllib.request
from email.message import Message
from unittest import mock

from job_agent import fetch
from job_agent.errors import Refused


class _Reply:
    def __init__(self, status, body):
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = "application/json"
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class RecordingOpener:
    def __init__(self, status=200, body=b'{"jobs": []}', error=None):
        self.calls, self.status, self.body, self.error = [], status, body, error

    def open(self, request, timeout=None):
        self.calls.append({"url": request.full_url, "method": request.get_method(),
                           "agent": request.get_header("User-agent"), "timeout": timeout})
        if self.error is not None:
            raise self.error
        return _Reply(self.status, self.body)


class FetchTest(unittest.TestCase):
    def test_a_refused_url_opens_no_connection(self):
        for url in ("https://api.ashbyhq.com.evil.example/", "https://notapi.ashbyhq.com/", "http://api.ashbyhq.com/"):
            opener = RecordingOpener()
            with self.subTest(url=url):
                with self.assertRaises(Refused):
                    fetch.get(url, opener=opener)
                self.assertEqual(opener.calls, [], "the opener was used for a refused URL")

    def test_the_board_url_is_fetched_once_with_get(self):
        opener = RecordingOpener(body=b'{"jobs": [1]}')
        reply = fetch.get(fetch.allowlist.BOARD_URL, opener=opener)
        self.assertEqual(len(opener.calls), 1)
        self.assertEqual(opener.calls[0]["url"], fetch.allowlist.BOARD_URL)
        self.assertEqual(opener.calls[0]["method"], "GET")
        self.assertEqual(opener.calls[0]["agent"], fetch.USER_AGENT)
        self.assertEqual(opener.calls[0]["timeout"], fetch.TIMEOUT_SECONDS)
        self.assertEqual(reply.body, b'{"jobs": [1]}')
        self.assertEqual(reply.status, 200)
        self.assertTrue(reply.received_at.endswith("Z"))

    def test_an_error_status_is_still_a_response(self):
        error = urllib.error.HTTPError(fetch.allowlist.BOARD_URL, 503, "Service Unavailable", Message(), io.BytesIO(b"down"))
        reply = fetch.get(fetch.allowlist.BOARD_URL, opener=RecordingOpener(error=error))
        self.assertEqual((reply.status, reply.body), (503, b"down"))

    def test_redirects_are_refused_not_followed(self):
        handler = fetch.NoRedirects()
        request = urllib.request.Request(fetch.allowlist.BOARD_URL)
        with self.assertRaises(Refused) as caught:
            handler.redirect_request(request, None, 302, "Found", Message(), "https://evil.example/")
        self.assertIn("evil.example", str(caught.exception))

    def test_the_opener_ignores_proxy_settings_and_has_only_our_redirect_handler(self):
        with mock.patch.dict(os.environ, {"HTTPS_PROXY": "http://127.0.0.1:9", "https_proxy": "http://127.0.0.1:9"}):
            opener = fetch.build_opener()
        # An empty ProxyHandler registers nothing; what must not be there is one that routes through a proxy.
        routed = [h for h in opener.handlers if isinstance(h, urllib.request.ProxyHandler) and h.proxies]
        self.assertEqual(routed, [])
        redirects = [h for h in opener.handlers if isinstance(h, urllib.request.HTTPRedirectHandler)]
        self.assertTrue(redirects and all(isinstance(h, fetch.NoRedirects) for h in redirects))


if __name__ == "__main__":
    unittest.main()
