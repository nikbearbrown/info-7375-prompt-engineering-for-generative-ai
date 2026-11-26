"""The only module that touches the network. Every request goes through policy.check_request().

Redirects are refused (never followed). TLS verification stays on; the python.org macOS build
ships without a CA bundle, so fall back to the OS bundle (same fix as JS1, 2026-10-25).
"""
import os
import socket
import ssl
import time
import urllib.error
import urllib.request

from . import policy

USER_AGENT = "js2-loop-tools-diff/1.0 (INFO 7375 coursework; read-only)"


class Redirected(Exception):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Redirected(f"redirect {code} to {newurl!r} refused (not followed)")


def _tls_context():
    ctx = ssl.create_default_context()
    paths = ssl.get_default_verify_paths()
    if not (paths.cafile or paths.capath) and not os.environ.get("SSL_CERT_FILE"):
        for bundle in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
            if os.path.exists(bundle):
                ctx.load_verify_locations(cafile=bundle)
                break
    return ctx


class Response:
    """What one attempt produced. `error_kind` is None on a completed HTTP exchange."""

    def __init__(self, status=None, body=b"", error_kind=None, error=None, elapsed=0.0, decision=None):
        self.status, self.body, self.error_kind, self.error = status, body, error_kind, error
        self.elapsed, self.decision = elapsed, decision


def get(url, timeout, max_bytes):
    """One GET attempt. Raises policy.PolicyDenied before any I/O if the policy says no.
    Network failures are returned as a Response with error_kind, not raised."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    decision = policy.check_request("GET", url, headers)
    if decision["decision"] != policy.ALLOW:
        raise policy.PolicyDenied(decision)
    opener = urllib.request.build_opener(_NoRedirect, urllib.request.HTTPSHandler(context=_tls_context()))
    req = urllib.request.Request(url, headers=headers, method="GET")
    t0 = time.monotonic()
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read(max_bytes + 1)
            status = resp.status
    except Redirected as e:
        refused = dict(decision, decision=policy.DENY, reason=str(e))
        raise policy.PolicyDenied(refused)
    except urllib.error.HTTPError as e:
        body = e.read(max_bytes + 1) if e.fp else b""
        return Response(e.code, body, None, None, time.monotonic() - t0, decision)
    except (socket.timeout, TimeoutError) as e:
        return Response(None, b"", "timeout", repr(e), time.monotonic() - t0, decision)
    except urllib.error.URLError as e:
        kind = "timeout" if isinstance(e.reason, (socket.timeout, TimeoutError)) else "network"
        return Response(None, b"", kind, repr(e.reason), time.monotonic() - t0, decision)
    except (ConnectionError, OSError) as e:
        return Response(None, b"", "network", repr(e), time.monotonic() - t0, decision)
    if len(body) > max_bytes:
        return Response(status, body[:max_bytes], "too_large", f"> {max_bytes} bytes",
                        time.monotonic() - t0, decision)
    return Response(status, body, None, None, time.monotonic() - t0, decision)
