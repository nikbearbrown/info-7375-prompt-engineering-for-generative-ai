"""Independent review findings 1 and 6 (REVIEW-FINDINGS.md), in the real network tool. Written before the fixes.

Local servers on 127.0.0.1 only. No outside network.
"""

import os
import socket
import threading
import unittest
from unittest import mock

from agent.tools import FetchError, http_transport


def raw_server(reply):
    """A server that answers one request with these exact bytes, then closes the connection."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    seen = []

    def serve():
        conn, _ = listener.accept()
        seen.append(conn.recv(65536))
        conn.sendall(reply)
        conn.close()
        listener.close()

    threading.Thread(target=serve, daemon=True).start()
    return "http://127.0.0.1:%d/x" % listener.getsockname()[1], seen


def call(url, timeout=3):
    try:
        return http_transport(url, timeout, 1000000)
    except FetchError as error:
        return error


class Finding1ProtocolErrors(unittest.TestCase):
    """GATE.md section 4: a connection error is a transient failure, never an unexpected crash, and a cut-off body
    is not a complete one."""

    def test_truncated_chunked_body_is_a_connection_error(self):
        url, _ = raw_server(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n100\r\n" + b"x" * 20)
        result = call(url)
        self.assertIsInstance(result, FetchError)
        self.assertEqual(result.kind, "connection")

    def test_garbage_status_line_is_a_connection_error(self):
        url, _ = raw_server(b"garbage\r\n\r\n")
        result = call(url)
        self.assertIsInstance(result, FetchError)
        self.assertEqual(result.kind, "connection")

    def test_body_shorter_than_its_content_length_is_not_accepted(self):
        url, _ = raw_server(b"HTTP/1.1 200 OK\r\nContent-Length: 5000\r\n\r\n" + b'{"jobs": [{"id": 1')
        result = call(url)
        self.assertIsInstance(result, FetchError, "a cut-off body came back as a complete response")
        self.assertEqual(result.kind, "connection")


class Finding6NoProxy(unittest.TestCase):
    """GATE.md section 5: only the allowed hosts, and no credentials. A proxy from the environment is neither."""

    def test_a_proxy_in_the_environment_is_not_used(self):
        proxy_url, proxy_saw = raw_server(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
        direct_url, direct_saw = raw_server(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\n{}")
        proxy = proxy_url.replace("http://", "http://alice:secret@").rsplit("/", 1)[0]
        env = {"HTTP_PROXY": proxy, "http_proxy": proxy, "HTTPS_PROXY": proxy, "https_proxy": proxy}
        with mock.patch.dict(os.environ, env):
            for name in ("NO_PROXY", "no_proxy"):
                os.environ.pop(name, None)
            result = call(direct_url)
        self.assertNotIsInstance(result, FetchError)
        self.assertEqual(result.status, 200, "the request went through the proxy")
        self.assertEqual(len(direct_saw), 1)
        self.assertNotIn(b"Proxy-Authorization", b"".join(proxy_saw))


if __name__ == "__main__":
    unittest.main()
