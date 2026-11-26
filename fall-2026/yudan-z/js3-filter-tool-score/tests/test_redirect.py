"""GATE revision 2026-11-09 (redirects). Written before the change. Offline: two servers on 127.0.0.1."""
import http.server
import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agent import tools  # noqa: E402


def serve(handler):
    srv = http.server.HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class RedirectTests(unittest.TestCase):
    def test_redirect_is_not_followed(self):
        hits = []

        class Target(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                hits.append(self.path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"jobs": []}')

            def log_message(self, *a):
                pass

        target = serve(Target)

        class Redirector(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", f"http://127.0.0.1:{target.server_port}/elsewhere")
                self.end_headers()

            def log_message(self, *a):
                pass

        red = serve(Redirector)
        try:
            status, _ = tools.http_get(f"http://127.0.0.1:{red.server_port}/jobs", 5)
            self.assertEqual(status, 302)
            self.assertEqual(hits, [])
        finally:
            red.shutdown()
            target.shutdown()

    def test_3xx_is_not_transient(self):
        self.assertFalse(tools.FetchFailed("u", "http", 302).transient)


if __name__ == "__main__":
    unittest.main()
