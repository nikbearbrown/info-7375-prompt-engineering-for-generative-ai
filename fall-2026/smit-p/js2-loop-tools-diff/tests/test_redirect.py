"""A redirect must not take the agent to a host the policy never checked.

Written before the fix: urllib follows 3xx redirects by default, so an allowed host could
send the agent anywhere. Uses a throwaway local HTTP server; the transport is called
directly, below the policy, to see what the transport itself does with a 302.
"""

import http.server
import threading
import unittest

from agent import fetch


class Redirector(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/elsewhere":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"jobs": [], "followed": true}')
            return
        self.send_response(302)
        self.send_header("Location", "/elsewhere")
        self.end_headers()

    def log_message(self, *args):
        pass


class RedirectNotFollowed(unittest.TestCase):
    def setUp(self):
        self.server = http.server.HTTPServer(("127.0.0.1", 0), Redirector)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/jobs"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_302_is_returned_not_followed(self):
        resp = fetch.LiveTransport().get(self.url, {"User-Agent": fetch.USER_AGENT})
        self.assertEqual(resp.http_status, 302)
        self.assertNotIn(b"followed", resp.body)


if __name__ == "__main__":
    unittest.main()
