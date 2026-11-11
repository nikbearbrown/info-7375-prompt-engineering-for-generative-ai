"""Attempt-deadline tests for agent/net.py (GATE.md §2 "20 seconds, or remaining time if less";
GATE_ADDENDUM_1.md §4 "Do not claim a hard deadline is enforced if the implementation only checks it
between potentially unbounded operations").

SYNTHETIC: local TCP/TLS servers and a stubbed resolver. No real network. The board host name is used
only as a name; the stub resolver maps it to 127.0.0.1. Written and committed before the fix in net.py.
"""
import http.client
import shutil
import socket
import socketserver
import ssl
import subprocess
import threading
import time

import pytest

from agent.net import TransportError, https_get

NAME = "boards-api.greenhouse.io"
URL = f"https://{NAME}/v1/boards/alpha/jobs?content=true"
REAL_GAI = socket.getaddrinfo
BODY = b'{"jobs": []}'


class _Server:
    """Local TCP server; counts connections and records each request head."""

    def __init__(self, handler, tls=None):
        self.connections, self.requests = 0, []
        outer = self

        class H(socketserver.BaseRequestHandler):
            def handle(self):
                outer.connections += 1
                sock = self.request
                try:
                    if tls is not None:
                        sock = tls.wrap_socket(sock, server_side=True)
                    handler(sock, outer)
                except (OSError, ssl.SSLError):
                    pass

        self.srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


def _read_head(sock):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def _ok(sock, srv):
    srv.requests.append(_read_head(sock))
    sock.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: %d\r\n"
                 b"Connection: close\r\n\r\n" % len(BODY) + BODY)


def _drip(sock, srv):  # sends the status line and headers one byte every 50 ms (about 2 s in total)
    srv.requests.append(_read_head(sock))
    for byte in b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}":
        sock.sendall(bytes([byte]))
        time.sleep(0.05)


def _resolver(monkeypatch, port, *, wait=0.0, release=None):
    """Stub DNS: NAME -> 127.0.0.1:port after `wait` seconds (or until `release` is set)."""
    calls = []

    def gai(host, p, *a, **k):
        if host != NAME:
            return REAL_GAI(host, p, *a, **k)
        calls.append(time.monotonic())
        (release.wait(wait) if release is not None else time.sleep(wait))
        return REAL_GAI("127.0.0.1", port, *a, **k)

    monkeypatch.setattr(socket, "getaddrinfo", gai)
    return calls


def _plain(host, port, timeout):  # the real http.client, without TLS; the host stays the board name
    return http.client.HTTPConnection(host, port, timeout=timeout)


def _get(timeout, factory=_plain):
    return https_get(URL, timeout, time.monotonic() + timeout, conn_factory=factory)


def test_normal_response_keeps_the_board_name_in_the_request(monkeypatch):
    srv = _Server(_ok)
    try:
        _resolver(monkeypatch, srv.port)
        status, headers, body = _get(2.0)
    finally:
        srv.close()
    assert (status, body) == (200, BODY) and headers["content-type"] == "application/json"
    assert srv.connections == 1
    assert srv.requests[0].startswith(b"GET /v1/boards/alpha/jobs?content=true HTTP/1.1\r\n")
    assert f"Host: {NAME}".encode() in srv.requests[0]


def test_slow_dns_is_bounded_by_the_attempt_deadline(monkeypatch):
    srv, release = _Server(_ok), threading.Event()
    try:
        _resolver(monkeypatch, srv.port, wait=1.5, release=release)
        t0 = time.monotonic()
        with pytest.raises(TransportError) as e:
            _get(0.4)
        elapsed = time.monotonic() - t0
    finally:
        release.set()
        srv.close()
    assert e.value.kind == "timeout"
    assert elapsed < 1.0, f"the attempt took {elapsed:.2f} s against a 0.4 s deadline"


def test_a_dns_answer_arriving_after_the_deadline_is_never_connected(monkeypatch):
    srv, release = _Server(_ok), threading.Event()
    try:
        _resolver(monkeypatch, srv.port, wait=1.5, release=release)
        with pytest.raises(TransportError):
            _get(0.4)
        release.set()        # the late DNS answer now arrives
        time.sleep(0.5)      # give an abandoned attempt time to (wrongly) connect
        late = srv.connections
    finally:
        release.set()
        srv.close()
    assert late == 0, "a request was dispatched after its attempt had already timed out"


def test_dripped_headers_are_bounded_by_the_attempt_deadline(monkeypatch):
    srv = _Server(_drip)
    try:
        _resolver(monkeypatch, srv.port)
        t0 = time.monotonic()
        with pytest.raises(TransportError) as e:
            _get(0.5)
        elapsed = time.monotonic() - t0
    finally:
        srv.close()
    assert e.value.kind == "timeout"
    assert elapsed < 1.2, f"the attempt took {elapsed:.2f} s against a 0.5 s deadline"


def test_an_expired_deadline_dispatches_nothing(monkeypatch):
    srv = _Server(_ok)
    try:
        calls = _resolver(monkeypatch, srv.port)
        with pytest.raises(TransportError) as e:
            https_get(URL, 1.0, time.monotonic() - 0.01, conn_factory=_plain)
    finally:
        srv.close()
    assert e.value.kind == "timeout"
    assert srv.connections == 0 and calls == []


# --- TLS: the fix must not change which name the certificate is verified against -----------------

@pytest.fixture
def certs(tmp_path):
    openssl = shutil.which("openssl")
    if not openssl:
        pytest.skip("openssl CLI not available to make a throwaway test certificate")

    def make(cn):
        key, crt = tmp_path / f"{cn}.key", tmp_path / f"{cn}.crt"
        subprocess.run([openssl, "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
                        "-keyout", str(key), "-out", str(crt), "-subj", f"/CN={cn}",
                        "-addext", f"subjectAltName=DNS:{cn}"], check=True, capture_output=True)
        server = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server.load_cert_chain(crt, key)
        client = ssl.create_default_context(cafile=str(crt))
        return server, client

    return make


def _https(client_ctx):
    return lambda host, port, timeout: http.client.HTTPSConnection(host, port, timeout=timeout, context=client_ctx)


def test_tls_is_verified_against_the_board_name(monkeypatch, certs):
    server_ctx, client_ctx = certs(NAME)
    srv = _Server(_ok, tls=server_ctx)
    try:
        _resolver(monkeypatch, srv.port)
        status, _, body = _get(3.0, _https(client_ctx))
    finally:
        srv.close()
    assert (status, body) == (200, BODY)


def test_tls_certificate_for_another_name_is_refused(monkeypatch, certs):
    server_ctx, client_ctx = certs("other.example")
    srv = _Server(_ok, tls=server_ctx)
    try:
        _resolver(monkeypatch, srv.port)
        with pytest.raises(TransportError) as e:
            _get(3.0, _https(client_ctx))
    finally:
        srv.close()
    assert e.value.kind == "other" and "CERTIFICATE_VERIFY_FAILED" in str(e.value)
    assert srv.requests == []  # no request head was sent over the unverified connection
