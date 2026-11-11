"""One HTTPS GET, never following redirects, within a hard attempt deadline.

How the deadline is enforced (GATE.md §2; GATE_ADDENDUM_1.md §4):
- The whole attempt (DNS resolution, connect, TLS handshake, request, status line, headers, body)
  runs in a worker thread. The caller waits at most until the deadline. If the worker is still
  running then, the caller raises TransportError("timeout") and returns. The caller's wait is
  bounded even while the worker is blocked inside getaddrinfo, which cannot be interrupted.
- The worker checks for cancellation and for the deadline after DNS and immediately before
  connecting, so a DNS answer that arrives after the deadline is not connected and its request is
  not sent. (The window between that check and the connect is a few instructions, not zero.) It
  also checks between body chunks.
- The connect hook is http.client's `_create_connection` attribute (CPython 3.12), which is not a
  public API. If it is missing, the attempt fails closed as TransportError("other").
- Inside the worker, every socket operation is also limited to the time left, so an abandoned
  worker ends on its own within about one timeout. A worker blocked in getaddrinfo ends only when
  the OS resolver returns; it is a daemon thread and does not delay process exit.
- Host name, Host header, SNI and certificate verification all still use the board name; only the
  TCP connect uses the resolved address.
"""
import http.client
import socket
import ssl
import threading
import time
from urllib.parse import urlsplit

USER_AGENT = "js2-loop-tools-diff/1.0 (INFO 7375 coursework; read-only)"


class TransportError(Exception):
    def __init__(self, kind, detail):
        super().__init__(f"{kind}: {detail}")
        self.kind = kind  # "timeout" | "connection" (both retryable) | "other" (not retryable)


def https_get(url, timeout_s, deadline, *, conn_factory=http.client.HTTPSConnection, clock=time.monotonic):
    if deadline - clock() <= 0:
        raise TransportError("timeout", "attempt deadline reached before dispatch")
    box, cancelled = {"phase": "start"}, threading.Event()
    worker = threading.Thread(target=_run, args=(url, timeout_s, deadline, conn_factory, clock, cancelled, box),
                              name="js2-http-attempt", daemon=True)
    worker.start()
    worker.join(max(0.0, deadline - clock()))
    if worker.is_alive():
        cancelled.set()
        raise TransportError("timeout", f"attempt deadline reached during {box['phase']} (attempt abandoned)")
    if "error" in box:
        raise box["error"]
    return box["result"]


def _run(url, timeout_s, deadline, conn_factory, clock, cancelled, box):
    try:
        box["result"] = _attempt(url, timeout_s, deadline, conn_factory, clock, cancelled, box)
    except BaseException as e:  # re-raised in the caller's thread, unchanged
        box["error"] = e


def _connector(deadline, clock, cancelled, box):
    """Replaces http.client's socket.create_connection: resolve, re-check, then connect to the address."""
    def connect(address, timeout, source_address=None):
        host, port = address
        box["phase"] = "DNS resolution"
        infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
        last = OSError(f"getaddrinfo returned no addresses for {host}")
        for *_, sockaddr in infos:
            left = deadline - clock()
            if cancelled.is_set() or left <= 0:
                raise TransportError("timeout", "attempt deadline reached during DNS resolution; not connected")
            box["phase"] = "connect"
            try:
                return socket.create_connection(sockaddr[:2], min(timeout, left), source_address)
            except OSError as e:
                last = e
        raise last
    return connect


def _attempt(url, timeout_s, deadline, conn_factory, clock, cancelled, box):
    parts = urlsplit(url)
    target = parts.path + (f"?{parts.query}" if parts.query else "")
    conn = conn_factory(parts.hostname, parts.port, timeout=timeout_s)
    if not hasattr(conn, "_create_connection"):  # fail closed rather than fall back to an unbounded connect
        raise TransportError("other", "HTTP client lacks the connection hook; refusing an unbounded connect")
    conn._create_connection = _connector(deadline, clock, cancelled, box)
    try:
        conn.request("GET", target, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        box["phase"] = "status line and headers"
        resp = conn.getresponse()
        status, headers = resp.status, {k.lower(): v for k, v in resp.getheaders()}
        if 300 <= status < 400:  # never read on, never follow: the caller refuses it
            return status, headers, b""
        box["phase"] = "body"
        chunks = []
        while True:
            left = deadline - clock()
            if left <= 0 or cancelled.is_set():
                raise TransportError("timeout", "attempt deadline reached while reading the body")
            if conn.sock is not None:
                conn.sock.settimeout(left)
            chunk = resp.read(65536)
            if not chunk:
                break
            chunks.append(chunk)
        return status, headers, b"".join(chunks)
    except TransportError:
        raise
    except (socket.timeout, TimeoutError) as e:
        raise TransportError("timeout", str(e) or "socket timeout") from None
    except (ConnectionResetError, ConnectionAbortedError, http.client.RemoteDisconnected, BrokenPipeError) as e:
        raise TransportError("connection", f"{type(e).__name__}: {e}") from None
    except (ssl.SSLError, socket.gaierror, OSError, http.client.HTTPException) as e:
        raise TransportError("other", f"{type(e).__name__}: {e}") from None
    finally:
        conn.close()
