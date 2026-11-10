"""The live HTTPS GET used by the loop. It never follows redirects and bounds the whole request.

`http.client` is used instead of urllib so that a 3xx is simply returned (and refused by
the loop) rather than followed. TLS is verified with the system's default context.
A watchdog closes the socket at the request deadline, so a slow server that drips bytes
cannot stretch one request past its budget (GATE.md section 2).
"""
from __future__ import annotations

import http.client
import socket
import ssl
import threading
import time
from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import urlsplit

USER_AGENT = "info7375-js2-jobloop (fictional-persona job watch; read-only)"
MAX_BODY_BYTES = 32 * 1024 * 1024
CHUNK = 64 * 1024


@dataclass
class Response:
    status: int
    headers: dict
    body: bytes
    elapsed: float = 0.0
    note: str = ""


@dataclass
class TransportFailure(Exception):
    """No usable HTTP response. kind: timeout, connection-reset, tls, connection-error, too-large."""
    kind: str
    message: str
    elapsed: float = 0.0
    extra: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.kind}: {self.message}"


def https_get(url: str, timeout: float, clock: Callable = time.monotonic) -> Response:
    """GET `url`. `timeout` bounds the whole request: connect, headers and body."""
    start = clock()
    deadline = start + timeout
    parts = urlsplit(url)
    path = parts.path + (f"?{parts.query}" if parts.query else "")
    conn = http.client.HTTPSConnection(parts.hostname, 443, timeout=max(0.001, timeout),
                                       context=ssl.create_default_context())
    expired = threading.Event()

    def _abort():
        expired.set()
        sock = conn.sock
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    watchdog = threading.Timer(max(0.001, timeout), _abort)
    watchdog.daemon = True
    watchdog.start()
    try:
        conn.request("GET", path, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
        resp = conn.getresponse()
        headers = {k.lower(): v for k, v in resp.getheaders()}
        chunks, total = [], 0
        while True:
            remaining = deadline - clock()
            if remaining <= 0 or expired.is_set():
                raise socket.timeout("request deadline reached while reading the body")
            if conn.sock is not None:
                conn.sock.settimeout(remaining)
            chunk = resp.read(CHUNK)
            if expired.is_set():
                raise socket.timeout("request deadline reached while reading the body")
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BODY_BYTES:
                raise TransportFailure("too-large", f"body exceeded {MAX_BODY_BYTES} bytes",
                                       clock() - start)
            chunks.append(chunk)
        return Response(resp.status, headers, b"".join(chunks), clock() - start)
    except TransportFailure:
        raise
    except ssl.SSLCertVerificationError as exc:
        raise TransportFailure("tls", f"TLS verification failed: {exc}", clock() - start) from None
    except ssl.SSLError as exc:
        raise TransportFailure("tls", f"TLS error: {exc}", clock() - start) from None
    except (socket.timeout, TimeoutError) as exc:
        raise TransportFailure("timeout", f"timed out after {timeout:.1f}s: {exc}", clock() - start) from None
    except ConnectionResetError as exc:
        raise TransportFailure("connection-reset", str(exc), clock() - start) from None
    except (OSError, http.client.HTTPException) as exc:
        if expired.is_set():
            raise TransportFailure("timeout", f"timed out after {timeout:.1f}s", clock() - start) from None
        raise TransportFailure("connection-error", f"{type(exc).__name__}: {exc}", clock() - start) from None
    finally:
        watchdog.cancel()
        conn.close()
