"""Test helpers: a transport spy, a fake HTTPS handler, an open() spy, and an "out" root."""

import builtins
import email.message
import io
import os
import urllib.request
import urllib.response
from pathlib import Path

from agent.transport import Response


class TransportSpy:
    """Records every transport call. Returns a canned response, or delegates to `inner`."""

    def __init__(self, response: Response | None = None, inner=None):
        self.response = response
        self.inner = inner
        self.calls: list[tuple[str, str, float]] = []

    def __call__(self, method, url, timeout):
        self.calls.append((method, url, timeout))
        if self.inner is not None:
            return self.inner(method, url, timeout)
        if self.response is not None:
            return self.response
        return Response(url, 200, (("Content-Type", "application/json"),), b'{"jobs": []}')


class FakeHTTPSHandler(urllib.request.BaseHandler):
    """Stands in for urllib's HTTPSHandler: answers every request with one canned response
    and records each request it receives, so a followed redirect would show up here."""

    def __init__(self, status: int, reason: str, headers: dict, body: bytes = b""):
        self.status, self.reason, self.headers, self.body = status, reason, headers, body
        self.requests: list[tuple[str, str]] = []

    def https_open(self, req):
        self.requests.append((req.get_method(), req.full_url))
        message = email.message.Message()
        for key, value in self.headers.items():
            message[key] = value
        response = urllib.response.addinfourl(io.BytesIO(self.body), message, req.full_url, code=self.status)
        response.msg = self.reason
        return response


class OpenSpy:
    """Records os.open, builtins.open and io.open calls, passing them through."""

    def __init__(self, monkeypatch):
        self.calls: list[tuple[str, str]] = []
        real_os_open, real_open = os.open, builtins.open

        def os_open(path, flags, *args, **kwargs):
            self.calls.append(("os.open", os.fspath(path)))
            return real_os_open(path, flags, *args, **kwargs)

        def py_open(file, *args, **kwargs):
            self.calls.append(("open", os.fspath(file) if not isinstance(file, int) else str(file)))
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr(os, "open", os_open)
        monkeypatch.setattr(builtins, "open", py_open)
        monkeypatch.setattr(io, "open", py_open)


def make_out_root(tmp_path: Path) -> Path:
    """A temporary output root named "out"."""
    root = tmp_path / "out"
    root.mkdir()
    return root
