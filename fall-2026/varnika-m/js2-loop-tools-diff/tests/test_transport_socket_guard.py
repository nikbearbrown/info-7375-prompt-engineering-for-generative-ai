"""The revision I asked for in the review packet (REVIEW-PACKET.md section 6).

My decision on patch 91bfbda: "The test should explicitly verify that the socket is found
through ._sock and fail immediately if that attribute is missing, rather than allowing the
code to silently continue."

The patch reaches the socket through response.fp.raw._sock, a private attribute of
Python's http.client. If a future Python renames it, _socket_of() returns None and the
deadline loses its per-read socket timeout without any error. These tests make that loud.
They use a local server on 127.0.0.1 (no outside network).
"""

import http.server
import socket
import threading
import unittest
import urllib.error
import urllib.request

from agent import tools


class Answer(http.server.BaseHTTPRequestHandler):
    code = 200

    def do_GET(self):
        body = b'{"jobs": [{"id": 1}]}'
        self.send_response(self.code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class NotFound(Answer):
    code = 404


def open_response(handler):
    """The object http_transport gets back from urllib: an HTTPResponse, or the HTTPError around one."""
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.handle_request, daemon=True).start()
    url = "http://127.0.0.1:%d/x" % server.server_address[1]
    try:
        return server, urllib.request.build_opener(tools._NoRedirects).open(url, timeout=5)
    except urllib.error.HTTPError as error:
        return server, error


class SocketIsFoundThroughSock(unittest.TestCase):
    def socket_or_fail(self, response):
        """Fail at once, by name, if the private attribute the patch relies on is not there."""
        raw = response.fp if isinstance(response, urllib.error.HTTPError) else response
        if not hasattr(getattr(getattr(raw, "fp", None), "raw", None), "_sock"):
            self.fail("response.fp.raw._sock is missing on this Python: agent/tools.py _socket_of() would "
                      "silently return None and the per-read deadline would be lost")
        body, sock = tools._socket_of(response)
        self.assertIs(sock, raw.fp.raw._sock, "_socket_of() did not return the socket found through ._sock")
        self.assertIsInstance(sock, socket.socket)
        return sock

    def test_found_for_a_normal_response(self):
        server, response = open_response(Answer)
        self.addCleanup(server.server_close)
        with response:
            self.socket_or_fail(response)

    def test_found_for_an_error_response(self):
        server, response = open_response(NotFound)
        self.addCleanup(server.server_close)
        with response:
            self.assertEqual(response.code, 404)
            self.socket_or_fail(response)

    def test_the_guard_fails_when_the_attribute_is_missing(self):
        """The guard itself: a response whose fp.raw has no _sock must fail the check, not pass it."""
        class NoSock:
            pass

        class Fake:
            fp = type("Buffered", (), {"raw": NoSock()})()

        with self.assertRaises(AssertionError) as caught:
            self.socket_or_fail(Fake())
        self.assertIn("_sock is missing", str(caught.exception))
        self.assertEqual(tools._socket_of(Fake())[1], None)  # what the code would do: continue silently


if __name__ == "__main__":
    unittest.main()
