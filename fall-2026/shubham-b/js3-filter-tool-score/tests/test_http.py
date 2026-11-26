"""Tests for the allow-listed fetcher (CONTRACT §11, PLAN §3.3).

The inner transport is a recording ``httpx.MockTransport``; every rejection test also
asserts that it received no request at all.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import httpx
import pytest

from job_search_agent.config import load_config
from job_search_agent.errors import HostNotAllowed
from job_search_agent.http import (
    AllowListTransport,
    build_fetcher,
    build_fetcher_from_settings,
)
from job_search_agent.models import FetchErrorKind
from job_search_agent.ports import HttpFetcher, JsonValue
from tests.conftest import REPO_ROOT
from tests.fakes import RecordingTransport, Reply, mock_transport

HOST = "boards-api.greenhouse.io"
JOBS = f"https://{HOST}/v1/boards/stripe/jobs?content=true"
UA = "job-search-agent/test"


class Events:
    """Recording ``EventSink``."""

    def __init__(self) -> None:
        self.items: list[tuple[str, dict[str, JsonValue]]] = []

    def emit(self, event: str, fields: Mapping[str, JsonValue]) -> None:
        self.items.append((event, dict(fields)))

    def names(self) -> list[str]:
        return [name for name, _ in self.items]


def _fetcher(
    inner: httpx.BaseTransport, events: Events | None = None, **kwargs: Any
) -> HttpFetcher:
    return build_fetcher([HOST], user_agent=UA, inner=inner, events=events, **kwargs)


def _redirect(location: str, status: int = 302) -> Reply:
    return Reply(status, b"", {"location": location})


def test_allowed_host_https_ok() -> None:
    inner = mock_transport({JOBS: Reply(200, b'{"jobs": []}', {"etag": "x"})})
    events = Events()
    result = _fetcher(inner, events).get(JOBS)
    assert result.ok
    assert result.error is None
    assert result.status_code == 200
    assert result.body == b'{"jobs": []}'
    assert result.final_url == JOBS
    assert result.redirect_chain == ()
    assert result.headers["etag"] == "x"
    assert len(inner.requests) == 1
    assert inner.requests[0].headers["user-agent"] == UA
    assert events.names() == ["http.request", "http.response"]


def _assert_rejected(
    url: str, kind: FetchErrorKind = FetchErrorKind.HOST_REJECTED
) -> RecordingTransport:
    inner = mock_transport(lambda _req: httpx.Response(200, content=b"{}"))
    events = Events()
    result = _fetcher(inner, events).get(url)
    assert result.error is kind
    assert not result.ok
    assert result.body is None
    assert result.status_code is None
    assert inner.requests == []
    assert "http.request" not in events.names()
    return inner


def test_http_scheme_rejected() -> None:
    _assert_rejected(f"http://{HOST}/v1/boards/stripe/jobs")


@pytest.mark.parametrize(
    "url",
    ["https://example.com/", "https://api.greenhouse.io/x", "ftp://x/", "not a url"],
)
def test_off_list_host_rejected(url: str) -> None:
    _assert_rejected(url)


@pytest.mark.parametrize(
    "host",
    [
        "boards-api.greenhouse.io.evil.com",
        "xboards-api.greenhouse.io",
        "boards.greenhouse.io",
        "boards-api.greenhouse.io.",
        "evil.com#boards-api.greenhouse.io",
    ],
)
def test_lookalike_hosts_rejected(host: str) -> None:
    _assert_rejected(f"https://{host}/v1/boards/stripe/jobs")


@pytest.mark.parametrize(
    "url",
    [
        f"https://user:secret@{HOST}/v1/boards/stripe/jobs",
        f"https://{HOST}@evil.com/v1/boards/stripe/jobs",
        f"https://token@{HOST}/",
    ],
)
def test_userinfo_trick_rejected(url: str) -> None:
    inner = mock_transport(lambda _req: httpx.Response(200))
    result = _fetcher(inner).get(url)
    assert result.error is FetchErrorKind.HOST_REJECTED
    assert inner.requests == []
    assert "secret" not in result.requested_url
    assert "token" not in result.requested_url
    assert "secret" not in (result.error_detail or "")


@pytest.mark.parametrize("port", [80, 444, 8443])
def test_nonstandard_port_rejected(port: int) -> None:
    _assert_rejected(f"https://{HOST}:{port}/v1/boards/stripe/jobs")


def test_explicit_443_allowed() -> None:
    inner = mock_transport(lambda _req: httpx.Response(200, content=b"{}"))
    assert _fetcher(inner).get(f"https://{HOST}:443/v1/x").ok


def test_transport_checks_independently() -> None:
    """The transport refuses even when used directly, without the fetcher."""
    inner = mock_transport(lambda _req: httpx.Response(200))
    transport = AllowListTransport(inner, [HOST.upper()])
    assert transport.allowed_hosts == {HOST}
    with httpx.Client(transport=transport) as client:
        with pytest.raises(HostNotAllowed) as info:
            client.get("https://evil.example/")
        assert info.value.reason == "host"
        assert client.get(JOBS).status_code == 200
    assert [r.url.host for r in inner.requests] == [HOST]


def test_empty_allow_list_refuses_everything() -> None:
    inner = mock_transport(lambda _req: httpx.Response(200))
    result = build_fetcher([], user_agent=UA, inner=inner).get(JOBS)
    assert result.error is FetchErrorKind.HOST_REJECTED
    assert inner.requests == []
    with pytest.raises(TypeError):
        build_fetcher(HOST, user_agent=UA, inner=inner)


@pytest.mark.parametrize(
    "location",
    [
        "https://evil.example/jobs",
        f"http://{HOST}/v1/boards/stripe/jobs",
        f"https://{HOST}:8443/v1/boards/stripe/jobs",
        f"https://u:p@{HOST}/v1/boards/stripe/jobs",
        "//evil.example/jobs",
    ],
)
def test_redirect_to_off_list_host_rejected_as_fetch_failed(location: str) -> None:
    inner = mock_transport({JOBS: _redirect(location)})
    events = Events()
    result = _fetcher(inner, events).get(JOBS)
    assert result.error is FetchErrorKind.REDIRECT_REJECTED
    assert result.body is None
    assert [str(r.url) for r in inner.requests] == [JOBS]  # target never requested
    assert "http.rejected" in events.names()
    assert "p@" not in str(events.items)


def test_redirect_within_allowlist_followed_and_traced() -> None:
    second = f"https://{HOST}/v1/boards/stripe/jobs?content=true&page=2"
    inner = mock_transport(
        {JOBS: _redirect("/v1/boards/stripe/jobs?content=true&page=2", 301),
         second: Reply(200, b'{"jobs": []}')}
    )  # fmt: skip
    events = Events()
    result = _fetcher(inner, events).get(JOBS)
    assert result.ok
    assert result.final_url == second
    assert result.redirect_chain == (JOBS,)
    assert [str(r.url) for r in inner.requests] == [JOBS, second]
    assert events.names() == [
        "http.request",
        "http.redirect",
        "http.request",
        "http.response",
    ]
    redirect = events.items[1][1]
    assert redirect["to_host"] == HOST
    assert redirect["status"] == 301


def test_too_many_redirects() -> None:
    def loop(request: httpx.Request) -> httpx.Response:
        hop = int(request.url.params.get("n", "0"))
        return httpx.Response(302, headers={"location": f"/r?n={hop + 1}"})

    inner = mock_transport(loop)
    result = _fetcher(inner, max_redirects=2).get(f"https://{HOST}/r?n=0")
    assert result.error is FetchErrorKind.TOO_MANY_REDIRECTS
    assert len(inner.requests) == 3  # the original plus two followed redirects
    zero = mock_transport({JOBS: _redirect(f"https://{HOST}/x")})
    result = _fetcher(zero, max_redirects=0).get(JOBS)
    assert result.error is FetchErrorKind.TOO_MANY_REDIRECTS
    assert len(zero.requests) == 1


def test_redirect_without_location_is_fetch_failed() -> None:
    inner = mock_transport({JOBS: Reply(302)})
    assert _fetcher(inner).get(JOBS).error is FetchErrorKind.HTTP_STATUS


@pytest.mark.parametrize("status", [404, 500, 429, 403, 304])
def test_non_2xx_is_fetch_failed(status: int) -> None:
    inner = mock_transport({JOBS: Reply(status, b"nope")})
    result = _fetcher(inner).get(JOBS)
    assert result.error is FetchErrorKind.HTTP_STATUS
    assert result.status_code == status
    assert result.body == b"nope"
    assert not result.ok


def test_429_not_retried() -> None:
    inner = mock_transport({JOBS: Reply(429, b"", {"retry-after": "60"})})
    result = _fetcher(inner).get(JOBS)
    assert result.error is FetchErrorKind.HTTP_STATUS
    assert result.headers["retry-after"] == "60"
    assert len(inner.requests) == 1


@pytest.mark.parametrize(
    "exc", [httpx.ReadTimeout, httpx.ConnectTimeout, httpx.PoolTimeout]
)
def test_timeout_is_fetch_failed(exc: Callable[..., Exception]) -> None:
    def slow(request: httpx.Request) -> httpx.Response:
        raise exc("timed out", request=request)

    result = _fetcher(mock_transport(slow)).get(JOBS)
    assert result.error is FetchErrorKind.TIMEOUT
    assert result.status_code is None


def test_wall_clock_deadline_is_timeout() -> None:
    ticks = iter([0.0, 0.0, 100.0, 100.0, 100.0])
    inner = mock_transport({JOBS: Reply(200, b"{}")})
    result = _fetcher(inner, timeout_s=5.0, monotonic=lambda: next(ticks)).get(JOBS)
    assert result.error is FetchErrorKind.TIMEOUT


def test_connect_error_is_transport_failure() -> None:
    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    result = _fetcher(mock_transport(down)).get(JOBS)
    assert result.error is FetchErrorKind.TRANSPORT


def test_body_size_cap() -> None:
    big = mock_transport({JOBS: Reply(200, b"x" * 101)})
    result = _fetcher(big, max_bytes=100).get(JOBS)
    assert result.error is FetchErrorKind.SIZE_CAP
    assert result.body is None
    exact = mock_transport({JOBS: Reply(200, b"x" * 100)})
    assert _fetcher(exact, max_bytes=100).get(JOBS).ok

    def streamed(_request: httpx.Request) -> httpx.Response:
        chunks = iter([b"x" * 60, b"x" * 60])
        return httpx.Response(200, content=chunks)  # no content-length

    result = _fetcher(mock_transport(streamed), max_bytes=100).get(JOBS)
    assert result.error is FetchErrorKind.SIZE_CAP


def test_links_in_content_never_requested() -> None:
    body = (
        b'{"jobs": [{"id": 1, "content": "&lt;a href=\\"https://evil.example/x\\"'
        b'&gt;apply&lt;/a&gt; https://boards.greenhouse.io/stripe/jobs/1"}]}'
    )
    inner = mock_transport({JOBS: Reply(200, body, {"link": "<https://evil.example>"})})
    result = _fetcher(inner).get(JOBS)
    assert result.ok
    assert [str(r.url) for r in inner.requests] == [JOBS]


def test_invalid_limits_rejected() -> None:
    inner = mock_transport(lambda _req: httpx.Response(200))
    limits: list[dict[str, Any]] = [
        {"timeout_s": 0},
        {"max_bytes": 0},
        {"max_redirects": -1},
    ]
    for kwargs in limits:
        with pytest.raises(ValueError, match="must be"):
            _fetcher(inner, **kwargs)


def test_build_from_config_settings() -> None:
    settings = load_config(REPO_ROOT / "config" / "agent.toml").http
    inner = mock_transport({JOBS: Reply(200, b"{}")})
    fetcher = build_fetcher_from_settings(settings, inner=inner)
    assert fetcher.get(JOBS).ok
    assert inner.requests[0].headers["user-agent"] == settings.user_agent
    assert fetcher.get("https://example.com/").error is FetchErrorKind.HOST_REJECTED
    assert len(inner.requests) == 1
