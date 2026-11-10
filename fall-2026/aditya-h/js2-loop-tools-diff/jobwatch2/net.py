"""The one network tool: an HTTPS GET with verified TLS. The loop asks the policy before calling it."""
import os
import ssl
import urllib.error
import urllib.request


def _ctx():
    ctx = ssl.create_default_context()
    if not ctx.get_ca_certs() and os.path.exists("/etc/ssl/cert.pem"):  # python.org macOS builds (JS1 lesson)
        ctx = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    return ctx


def http_get(url, timeout):
    """Return (status, body). Raises TimeoutError or ConnectionError on transport failure."""
    req = urllib.request.Request(url, headers={"User-Agent": "info7375-js2-jobwatch (student project)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except TimeoutError:
        raise
    except urllib.error.URLError as e:
        if isinstance(e.reason, TimeoutError):
            raise TimeoutError(str(e.reason)) from e
        raise ConnectionError(str(e.reason)) from e
