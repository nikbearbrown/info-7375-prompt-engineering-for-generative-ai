"""The request deadline against a REAL socket (GATE.md 'Budgets': each request gets at
most five seconds to receive the full response).

A local server on 127.0.0.1 answers over plain HTTP; a connection factory swaps
http.client.HTTPSConnection for HTTPConnection, so everything except TLS is the real
code path. Nothing leaves this machine. These tests take a few seconds of real time."""

import http.client
import socket
import threading
import time
import unittest

from jobwatch import net

URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"
HEAD = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n"


class LocalServer:
    """Accepts connections, reads the request, then runs `behaviour(conn, stop)`."""

    def __init__(self, behaviour):
        self.listener = socket.create_server(("127.0.0.1", 0))
        self.port = self.listener.getsockname()[1]
        self.accepted = 0
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._serve, args=(behaviour,), daemon=True)
        self.thread.start()

    def _serve(self, behaviour):
        self.listener.settimeout(0.2)
        while not self.stop.is_set():
            try:
                conn, _ = self.listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            self.accepted += 1
            with conn:
                conn.recv(65536)
                try:
                    behaviour(conn, self.stop)
                except OSError:
                    pass

    def factory(self, host, timeout):
        return http.client.HTTPConnection("127.0.0.1", self.port, timeout=timeout)

    def close(self):
        self.stop.set()
        self.listener.close()
        self.thread.join(timeout=10)


def trickle(conn, stop):
    """Headers, then one byte every 0.2 s for 6 s: no single wait is long, but the whole
    body takes far longer than the deadline."""
    conn.sendall(HEAD)
    end = time.monotonic() + 6
    while time.monotonic() < end and not stop.is_set():
        conn.sendall(b" ")
        time.sleep(0.2)


def stall(conn, stop):
    """Headers, a byte every 0.2 s for 1 s, then silence for 6 s. The silence starts when
    less time is left than the socket was first given, so only a timeout renewed before
    each receive stops it at the deadline."""
    conn.sendall(HEAD)
    end = time.monotonic() + 1.0
    while time.monotonic() < end and not stop.is_set():
        conn.sendall(b" ")
        time.sleep(0.2)
    stop.wait(6)


def whole(conn, stop):
    body = b'{"jobs": []}'
    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: "
                 + str(len(body)).encode() + b"\r\n\r\n" + body)


def moved(conn, stop):
    conn.sendall(b"HTTP/1.1 301 Moved Permanently\r\nLocation: https://example.com/jobs\r\n"
                 b"Content-Length: 0\r\nConnection: close\r\n\r\n")


class RealSocketDeadlineTest(unittest.TestCase):
    def serve(self, behaviour):
        server = LocalServer(behaviour)
        self.addCleanup(server.close)
        return server

    def test_a_trickling_body_is_abandoned_at_the_deadline(self):
        server = self.serve(trickle)
        started = time.monotonic()
        with self.assertRaises(net.Timeout):
            net.https_get(URL, started + 1.5, connection_factory=server.factory)
        self.assertLess(time.monotonic() - started, 2.2)

    def test_a_stalled_body_is_abandoned_at_the_deadline(self):
        server = self.serve(stall)
        started = time.monotonic()
        with self.assertRaises(net.Timeout):
            net.https_get(URL, started + 1.5, connection_factory=server.factory)
        self.assertLess(time.monotonic() - started, 2.2)

    def test_a_prompt_response_is_read_whole(self):
        server = self.serve(whole)
        response = net.https_get(URL, time.monotonic() + 5, connection_factory=server.factory)
        self.assertEqual((response.status, response.body, response.content_type), (200, b'{"jobs": []}', "application/json"))

    def test_a_real_redirect_is_returned_on_one_connection(self):
        server = self.serve(moved)
        response = net.https_get(URL, time.monotonic() + 5, connection_factory=server.factory)
        self.assertEqual((response.status, response.location), (301, "https://example.com/jobs"))
        self.assertEqual(server.accepted, 1)


if __name__ == "__main__":
    unittest.main()
