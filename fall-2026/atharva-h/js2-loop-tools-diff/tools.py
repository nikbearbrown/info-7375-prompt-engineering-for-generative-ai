"""The agent's only tools: an HTTP GET, a file read, a file write, a new run folder, a delete.

Each tool asks the Policy first. The HTTP opener has no cookie handler, so no cookie
can be stored or sent, and every redirect is checked against the policy again.
"""
import os
import socket
import time
import urllib.error
import urllib.request

from policy import PolicyViolation

USER_AGENT = "info7375-js2-loop (read-only; public job boards)"


class TransientError(Exception):
    """A timeout or dropped connection: the error policy may retry these once."""


class Response:
    def __init__(self, url, status, body, elapsed):
        self.url, self.status, self.body, self.elapsed = url, status, body, elapsed


class _CheckedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, policy):
        self.policy = policy

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.policy.check_request("GET", newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Tools:
    def __init__(self, policy):
        self.policy = policy
        self.opener = urllib.request.build_opener(_CheckedRedirect(policy))

    def http_get(self, url, timeout, headers=None):
        headers = dict(headers or {})
        self.policy.check_request("GET", url, headers)
        headers.setdefault("User-Agent", USER_AGENT)
        return self._send(urllib.request.Request(url, headers=headers, method="GET"), timeout)

    def _send(self, request, timeout):
        """The only place bytes leave the machine. Tests replace this, never the check above."""
        url = request.full_url
        start = time.monotonic()
        try:
            with self.opener.open(request, timeout=timeout) as response:
                return Response(url, response.status, response.read(), time.monotonic() - start)
        except urllib.error.HTTPError as e:
            return Response(url, e.code, e.read(), time.monotonic() - start)
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
            reason = getattr(e, "reason", e)
            if isinstance(reason, PolicyViolation):
                raise reason
            raise TransientError(f"{type(reason).__name__}: {reason}") from e

    def read_text(self, path):
        with open(self.policy.check_read(path), encoding="utf-8") as f:
            return f.read()

    def write_bytes(self, path, data, overwrite=False):
        target = self.policy.check_write(path, size=len(data))
        if os.path.lexists(target) and not overwrite:
            raise PolicyViolation(f"refused to overwrite {path}: no overwrite")
        os.makedirs(self.policy.check_write(os.path.dirname(target)), exist_ok=True)
        tmp = target + ".tmp"
        self.policy.check_write(tmp, size=len(data))
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, target)
        return target

    def write_text(self, path, text, overwrite=False):
        return self.write_bytes(path, text.encode("utf-8"), overwrite=overwrite)

    def make_run_dir(self, path):
        target = self.policy.check_new_run_dir(path)
        os.makedirs(target)
        return target

    def delete_run(self, path):
        import shutil
        target = self.policy.check_delete_run(path)
        shutil.rmtree(target)
        return target
