"""GATE.md, Permission policy and Error policy, at the network door: fetch.get_board checks the request
before any connection, keeps error answers, refuses redirects, and says which failures are transient.
No test here touches the network: a recording opener stands in."""

import io
import os
import socket
import ssl
import unittest
import urllib.error
import urllib.request
from email.message import Message
from unittest import mock

from job_agent import fetch, gate
from job_agent.errors import BoardNoAnswer, Redirected, Refused

GOOD = "https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true"


class _Reply:
    def __init__(self, status, chunks, on_read=None):
        self.status, self.chunks, self.on_read = status, list(chunks), on_read
        self.headers = Message()
        self.headers["Content-Type"] = "application/json"

    def read(self, size=-1):
        if self.on_read:
            self.on_read()
        return self.chunks.pop(0) if self.chunks else b""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class RecordingOpener:
    def __init__(self, reply=None, error=None):
        self.calls, self.reply, self.error = [], reply, error

    def open(self, request, timeout=None):
        self.calls.append({"url": request.full_url, "method": request.get_method(), "timeout": timeout,
                           "agent": request.get_header("User-agent")})
        if self.error is not None:
            raise self.error
        return self.reply


class GetBoardTest(unittest.TestCase):
    def test_a_refused_request_opens_no_connection(self):
        for url in ("https://evil.example/v1/boards/verkada/jobs?content=true",
                    "https://api.lever.co.evil.example/v0/postings/palantir?mode=json",
                    "http://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true",
                    "https://api.lever.co/v0/postings/palantir/abc123/apply"):
            opener = RecordingOpener(_Reply(200, [b"[]"]))
            with self.subTest(url=url):
                with self.assertRaises(Refused):
                    fetch.get_board(url, opener=opener)
                self.assertEqual(opener.calls, [])

    def test_a_get_with_the_gate_timeout_and_a_plain_user_agent(self):
        opener = RecordingOpener(_Reply(200, [b'{"jobs": ', b"[]}"]))
        response = fetch.get_board(GOOD, opener=opener)
        self.assertEqual(response.body, b'{"jobs": []}')
        self.assertEqual(response.status, 200)
        call = opener.calls[0]
        self.assertEqual((call["method"], call["timeout"]), ("GET", gate.REQUEST_TIMEOUT))
        self.assertIn("never applies", call["agent"])

    def test_an_error_status_is_an_answer_and_is_kept(self):
        error = urllib.error.HTTPError(GOOD, 404, "Not Found", Message(), io.BytesIO(b'{"status":404}'))
        response = fetch.get_board(GOOD, opener=RecordingOpener(error=error))
        self.assertEqual((response.status, response.body), (404, b'{"status":404}'))

    def test_timeouts_and_dropped_or_refused_connections_are_transient(self):
        for error in (TimeoutError("timed out"), socket.timeout("timed out"), ConnectionResetError(),
                      urllib.error.URLError(ConnectionRefusedError()), urllib.error.URLError(socket.gaierror(8, "x")),
                      urllib.error.URLError(socket.timeout("timed out"))):
            with self.subTest(error=repr(error)):
                with self.assertRaises(BoardNoAnswer) as caught:
                    fetch.get_board(GOOD, opener=RecordingOpener(error=error))
                self.assertTrue(caught.exception.transient)

    def test_a_tls_failure_is_not_transient(self):
        for error in (urllib.error.URLError(ssl.SSLCertVerificationError("certificate verify failed")),
                      urllib.error.URLError("unknown url type")):
            with self.subTest(error=repr(error)):
                with self.assertRaises(BoardNoAnswer) as caught:
                    fetch.get_board(GOOD, opener=RecordingOpener(error=error))
                self.assertFalse(caught.exception.transient)

    def test_an_answer_that_takes_longer_than_one_request_may_is_a_transient_no_answer(self):
        now = [0.0]
        reply = _Reply(200, [b"x"] * 10, on_read=lambda: now.__setitem__(0, now[0] + 10.0))
        with self.assertRaises(BoardNoAnswer) as caught:
            fetch.get_board(GOOD, opener=RecordingOpener(reply), monotonic=lambda: now[0])
        self.assertTrue(caught.exception.transient)
        self.assertIn(f"longer than {gate.REQUEST_TIMEOUT} s", str(caught.exception))

    def test_a_redirect_is_refused_and_never_followed(self):
        handler = fetch.RefuseRedirects()
        request = urllib.request.Request(GOOD)
        with self.assertRaises(Redirected):
            handler.redirect_request(request, None, 302, "Found", Message(), "https://evil.example/")

    def test_the_board_opener_refuses_redirects_and_ignores_proxy_settings(self):
        env = {"HTTPS_PROXY": "http://proxy.example:8080", "https_proxy": "http://proxy.example:8080"}
        with mock.patch.dict(os.environ, env):
            handlers = fetch.board_opener().handlers
        self.assertTrue(any(isinstance(h, fetch.RefuseRedirects) for h in handlers))
        # ProxyHandler({}) keeps urllib from adding the default one, which would read HTTPS_PROXY.
        self.assertEqual([h for h in handlers if isinstance(h, urllib.request.ProxyHandler) and h.proxies], [])


if __name__ == "__main__":
    unittest.main()
