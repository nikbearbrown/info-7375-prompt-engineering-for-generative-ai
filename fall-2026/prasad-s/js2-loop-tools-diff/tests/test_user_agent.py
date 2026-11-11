"""Every request the tool layer sends names the project, never Python's default (JS2-CP5c).

Defect reproduced 2026-11-06 (smoke run and curl): api.ashbyhq.com sits behind
Cloudflare, which answers User-Agent "Python-urllib/3.13" with 403, error 1010
"browser_signature_banned", for every board. An honest project identity gets
200 for notion and 404 for js2nosuchboard.

Two levels, neither of which sends anything:
- the loop: a full run over the five boards, retries included, records the
  Request object each attempt hands to the patched _send;
- the wire: the real _send, with urllib's HTTPS handler opening a recording
  subclass of http.client.HTTPSConnection that never connects, shows the
  headers urllib would put on the wire after its own defaults are applied
  (urllib adds "Python-urllib/3.x" only when a request carries no User-Agent).
"""

import http.client
import socket
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

from test_loop import AS, GH, NOT_FOUND_ASHBY, LoopCase, ashby_body, ashby_job, gh_body, gh_job, ok, status, timeout

from agent import tool_layer
from agent.policy import Policy

USER_AGENT = "js2-loop-tools-diff/0.7 (INFO 7375 course project)"
STRIPE_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
NOTION_URL = "https://api.ashbyhq.com/posting-api/job-board/notion?includeCompensation=true"


def user_agents(request):
    """Every User-Agent value on a urllib Request, whatever its case."""
    return [value for name, value in request.header_items() if name.lower() == "user-agent"]


class LoopRequestsCarryTheProjectIdentity(LoopCase):
    def setUp(self):
        super().setUp()
        self.requests = []
        record = self.fake_send

        def fake_send(request, timeout):
            self.requests.append(request)
            return record(request, timeout)

        patcher = mock.patch.object(tool_layer, "_send", fake_send)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_every_attempt_on_every_board_sends_exactly_the_project_user_agent(self):
        self.on(GH, "stripe", status(503), ok(gh_body(gh_job(1))))
        self.on(AS, "notion", timeout(), ok(ashby_body(ashby_job("n-1"))))
        self.on(GH, "duolingo", ok(gh_body(gh_job(2))))
        self.on(GH, "robinhood", ok(gh_body(gh_job(3))))
        self.on(AS, "js2nosuchboard", NOT_FOUND_ASHBY)
        report = self.go()
        self.assertEqual(report["exit"]["kind"], "finished")
        self.assertEqual(len(self.requests), 7)  # five boards, two of them retried
        for request in self.requests:
            with self.subTest(url=request.full_url):
                self.assertEqual(user_agents(request), [USER_AGENT])


class _Recorded(ConnectionError):
    pass


class WireHeadersCarryTheProjectIdentity(unittest.TestCase):
    """The real _send down to http.client; the connection records and stops there."""

    def setUp(self):
        self.sent = []
        sent = self.sent

        class RecordingConnection(http.client.HTTPSConnection):
            """The real class, so urllib finds every attribute it reads; it never connects."""

            def request(self, method, url, body=None, headers=None, **kwargs):
                sent.append((self.host, method, url, dict(headers or {})))

            def getresponse(self):
                raise _Recorded("recorded; nothing sent")  # an OSError, so fetch reports a connection error

        # urllib still runs its request preprocessing (which adds its default User-Agent
        # when none is set) and do_open's header merge; only the connection class differs.
        def https_open(handler, req):
            return handler.do_open(RecordingConnection, req, context=handler._context)

        no_socket = mock.Mock(side_effect=AssertionError("a socket would have been opened"))
        for patcher in (mock.patch.object(urllib.request.HTTPSHandler, "https_open", https_open),
                        mock.patch.object(socket, "create_connection", no_socket)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_wire_user_agent_is_the_project_identity_never_pythons_default(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tools = tool_layer.ToolLayer(Policy(Path(tmp.name), [("boards-api.greenhouse.io", "stripe"),
                                                            ("api.ashbyhq.com", "notion")]))
        for url in (STRIPE_URL, NOTION_URL):
            with self.assertRaises(tool_layer.FetchError):
                tools.fetch(url)
        self.assertEqual(len(self.sent), 2)
        for host, method, selector, headers in self.sent:
            with self.subTest(host=host):
                values = [v for k, v in headers.items() if k.lower() == "user-agent"]
                self.assertEqual(values, [USER_AGENT])
                self.assertFalse(any(v.startswith("Python-urllib") for v in headers.values()))


if __name__ == "__main__":
    unittest.main()
