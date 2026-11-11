"""Review packet test (REVIEW-PACKET.md): the real network tool must keep its timeout.

GATE.md section 2 says a request gets at most 30 s, or the seconds left in the run,
and W12 says a request never gets more seconds than are left. The loop tests use a
fake network, so they cannot see what tools.http_transport really does. These tests
use a local server on 127.0.0.1 (no outside network) that sends its body one byte at
a time, each byte well inside the socket timeout.

Written before the patch, and expected to fail before it.
"""

import http.server
import threading
import time
import unittest

from agent.tools import FetchError, http_transport

BODY = b'{"jobs": []}' + b" " * 188  # 200 bytes


class Trickle(http.server.BaseHTTPRequestHandler):
    delay = 0.25  # seconds between bytes: 200 bytes take 50 s

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(BODY)))
        self.end_headers()
        try:
            for i in range(len(BODY)):
                self.wfile.write(BODY[i:i + 1])
                self.wfile.flush()
                time.sleep(self.delay)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the client gave up, as it should

    def log_message(self, *args):
        pass


class Quick(Trickle):
    delay = 0

    def do_GET(self):
        body = b'{"jobs": [' + b",".join(b'{"id": %d}' % i for i in range(5000)) + b"]}"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        Quick.sent = body


def serve_once(handler):
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.handle_request, daemon=True).start()
    return server, "http://127.0.0.1:%d/v1/boards/x/jobs" % server.server_address[1]


def call_in_thread(url, timeout, max_bytes=20000000):
    outcome = {}

    def target():
        started = time.monotonic()
        try:
            outcome["response"] = http_transport(url, timeout, max_bytes)
        except FetchError as error:
            outcome["error"] = error
        outcome["seconds"] = time.monotonic() - started

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread, outcome


class TransportDeadline(unittest.TestCase):
    def test_slow_trickle_body_stops_at_the_timeout(self):
        """Predicted before the patch: FAILS. The call is still running after 6 s, with a 1 s timeout."""
        server, url = serve_once(Trickle)
        self.addCleanup(server.server_close)
        thread, outcome = call_in_thread(url, timeout=1.0)
        thread.join(6)
        self.assertFalse(thread.is_alive(), "http_transport was still reading after 6 s with timeout=1.0")
        self.assertIn("error", outcome, "a 50 s body was accepted with a 1 s timeout")
        self.assertEqual(outcome["error"].kind, "timeout")
        self.assertLess(outcome["seconds"], 2.0)

    def test_quick_body_is_returned_byte_for_byte(self):
        """Predicted before the patch: passes. The patch must not break a normal response."""
        server, url = serve_once(Quick)
        self.addCleanup(server.server_close)
        thread, outcome = call_in_thread(url, timeout=5.0)
        thread.join(6)
        self.assertNotIn("error", outcome)
        self.assertEqual(outcome["response"].status, 200)
        self.assertEqual(outcome["response"].body, Quick.sent)

    def test_byte_budget_on_a_real_socket(self):
        """Predicted before the patch: passes."""
        server, url = serve_once(Quick)
        self.addCleanup(server.server_close)
        thread, outcome = call_in_thread(url, timeout=5.0, max_bytes=1000)
        thread.join(6)
        self.assertEqual(outcome["error"].kind, "too_large")


if __name__ == "__main__":
    unittest.main()
