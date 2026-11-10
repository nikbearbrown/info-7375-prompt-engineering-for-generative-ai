"""One HTTPS GET, never following redirects, with a deadline that also bounds the body read.

The socket timeout is reset before every read to the time left until the attempt deadline, and the
deadline is checked between chunks. Not bounded: DNS resolution inside getaddrinfo (disclosed).
"""
import http.client
import socket
import ssl
import time
from urllib.parse import urlsplit

USER_AGENT = "js2-loop-tools-diff/1.0 (INFO 7375 coursework; read-only)"


class TransportError(Exception):
    def __init__(self, kind, detail):
        super().__init__(f"{kind}: {detail}")
        self.kind = kind  # "timeout" | "connection" (both retryable) | "other" (not retryable)


def https_get(url, timeout_s, deadline, *, conn_factory=http.client.HTTPSConnection, clock=time.monotonic):
    parts = urlsplit(url)
    target = parts.path + (f"?{parts.query}" if parts.query else "")
    conn = conn_factory(parts.hostname, parts.port, timeout=timeout_s)
    try:
        conn.request("GET", target, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        resp = conn.getresponse()
        status, headers = resp.status, {k.lower(): v for k, v in resp.getheaders()}
        if 300 <= status < 400:  # never read on, never follow: the caller refuses it
            return status, headers, b""
        chunks = []
        while True:
            left = deadline - clock()
            if left <= 0:
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
