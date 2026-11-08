"""The HTTPS transport (GATE.md 'Budgets' and 'Permission policy').

Each request gets a deadline for the FULL response, not just for connecting. A
redirect is returned to the caller, never followed. These tests replace the network
connection with a fake one; nothing is sent."""

import unittest

from jobwatch import net
from tests.fakes import FakeClock


class FakeSock:
    def __init__(self):
        self.timeouts = []

    def settimeout(self, value):
        self.timeouts.append(value)


class FakeResponse:
    def __init__(self, clock, status, chunks, seconds_per_chunk, headers):
        self.clock, self.status, self.chunks = clock, status, list(chunks)
        self.seconds_per_chunk, self.headers = seconds_per_chunk, headers
        self.reads = 0

    def getheader(self, name, default=None):
        return self.headers.get(name, default)

    def read(self, amount=None):
        self.reads += 1
        if not self.chunks:
            return b""
        self.clock.advance(self.seconds_per_chunk)
        return self.chunks.pop(0)


class FakeConnectionFactory:
    def __init__(self, clock, status=200, chunks=(b"{}",), seconds_per_chunk=0.1, headers=None, error=None):
        self.clock, self.status, self.chunks = clock, status, chunks
        self.seconds_per_chunk = seconds_per_chunk
        self.headers = {"Content-Type": "application/json"} if headers is None else headers
        self.error = error
        self.connections = []

    def __call__(self, host, timeout):
        factory = self

        class Connection:
            def __init__(self):
                self.host, self.timeout, self.requests = host, timeout, []
                self.sock = FakeSock()
                self.response = None

            def request(self, method, target, headers=None):
                if factory.error:
                    raise factory.error
                self.requests.append((method, target, headers or {}))

            def getresponse(self):
                self.response = FakeResponse(factory.clock, factory.status, factory.chunks,
                                             factory.seconds_per_chunk, factory.headers)
                return self.response

            def close(self):
                pass

        connection = Connection()
        self.connections.append(connection)
        return connection


URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"


class HttpsGetTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()

    def test_returns_the_whole_body_when_it_arrives_before_the_deadline(self):
        factory = FakeConnectionFactory(self.clock, chunks=(b'{"jo', b'bs":[]}'))
        response = net.https_get(URL, self.clock() + 5, clock=self.clock, connection_factory=factory)
        self.assertEqual(response, net.Response(200, b'{"jobs":[]}', "application/json", None))
        [connection] = factory.connections
        self.assertEqual(connection.host, "boards-api.greenhouse.io")
        self.assertEqual(connection.requests[0][:2], ("GET", "/v1/boards/anthropic/jobs?content=true"))

    def test_a_body_still_arriving_at_the_deadline_raises_timeout_and_stops_reading(self):
        factory = FakeConnectionFactory(self.clock, chunks=[b"x"] * 10, seconds_per_chunk=1.0)
        with self.assertRaises(net.Timeout):
            net.https_get(URL, self.clock() + 5, clock=self.clock, connection_factory=factory)
        self.assertLessEqual(factory.connections[0].response.reads, 6)

    def test_a_redirect_is_returned_and_not_followed(self):
        factory = FakeConnectionFactory(self.clock, status=301, chunks=(b"moved",),
                                        headers={"Location": "https://example.com/jobs", "Content-Type": "text/plain"})
        response = net.https_get(URL, self.clock() + 5, clock=self.clock, connection_factory=factory)
        self.assertEqual((response.status, response.location), (301, "https://example.com/jobs"))
        self.assertEqual(len(factory.connections), 1)

    def test_a_deadline_already_passed_raises_timeout_without_connecting(self):
        factory = FakeConnectionFactory(self.clock)
        with self.assertRaises(net.Timeout):
            net.https_get(URL, self.clock(), clock=self.clock, connection_factory=factory)
        self.assertEqual(factory.connections, [])

    def test_the_socket_never_waits_longer_than_the_time_left(self):
        factory = FakeConnectionFactory(self.clock, chunks=[b"a", b"b", b"c"], seconds_per_chunk=1.0)
        net.https_get(URL, self.clock() + 5, clock=self.clock, connection_factory=factory)
        [connection] = factory.connections
        self.assertLessEqual(connection.timeout, 5)
        self.assertTrue(connection.sock.timeouts)
        self.assertTrue(all(0 < t <= 5 for t in connection.sock.timeouts), connection.sock.timeouts)
        self.assertLess(connection.sock.timeouts[-1], connection.sock.timeouts[0])

    def test_a_connection_error_becomes_connection_failed(self):
        factory = FakeConnectionFactory(self.clock, error=OSError("connection refused (simulated)"))
        with self.assertRaises(net.ConnectionFailed):
            net.https_get(URL, self.clock() + 5, clock=self.clock, connection_factory=factory)

    def test_only_https_urls_are_accepted(self):
        with self.assertRaises(ValueError):
            net.https_get("http://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true",
                          self.clock() + 5, clock=self.clock, connection_factory=FakeConnectionFactory(self.clock))


if __name__ == "__main__":
    unittest.main()
