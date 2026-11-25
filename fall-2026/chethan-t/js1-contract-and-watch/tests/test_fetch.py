import http.client
import io
import json
import urllib.request

import pytest

from agent import fetch

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/testboard/jobs?content=true"


class FakeResponse(io.BytesIO):
    status = 200

    def getcode(self):
        return self.status


def test_16_other_host_raises_before_any_request():
    # The no_network fixture turns any request attempt into RuntimeError, not ValueError.
    with pytest.raises(ValueError):
        fetch.fetch_board("https://example.com/jobs")


def test_16b_greenhouse_host_is_accepted_with_network_mocked(monkeypatch, postings):
    requested = []

    def fake_urlopen(req, *args, **kwargs):
        requested.append(getattr(req, "full_url", req))
        body = {"jobs": [postings["swe_boston_plain"]], "meta": {"total": 1}}
        return FakeResponse(json.dumps(body).encode())

    # Covers both `urllib.request.urlopen(...)` and `from urllib.request import urlopen`.
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch, "urlopen", fake_urlopen, raising=False)

    fetch.fetch_board(BOARD_URL)
    assert requested == [BOARD_URL]


class FakeSocket:
    def __init__(self, raw):
        self.raw = raw

    def makefile(self, mode):
        return io.BytesIO(self.raw)


def test_16c_redirect_to_other_host_is_refused(monkeypatch):
    # Contract v2.1: a redirect off boards-api.greenhouse.io is refused
    # before any request reaches the other host. Only the HTTPS connection
    # is faked; urllib's real redirect handling runs.
    contacted = []

    class FakeHTTPSConnection(http.client.HTTPConnection):
        def __init__(self, host, timeout=None, context=None):
            contacted.append(host)
            super().__init__(host, timeout=timeout)

        def request(self, *args, **kwargs):
            pass

        def getresponse(self):
            raw = (b"HTTP/1.1 302 Found\r\n"
                   b"Location: https://evil.example.com/jobs\r\n"
                   b"Content-Length: 0\r\n\r\n")
            response = http.client.HTTPResponse(FakeSocket(raw))
            response.begin()
            return response

    monkeypatch.setattr(http.client, "HTTPSConnection", FakeHTTPSConnection)

    with pytest.raises(ValueError):
        fetch.fetch_board(BOARD_URL)
    assert contacted == ["boards-api.greenhouse.io"]
