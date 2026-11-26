"""Allow-listed HTTPS fetching for the agent's own requests (CONTRACT §11).

Two layers, both failing closed:

* ``AllowListTransport`` wraps any ``httpx`` transport and refuses, before the inner
  transport sees it, every request that is not HTTPS, carries userinfo, names a host
  not exactly on the allow-list, or uses a port other than the default/443.
* ``build_fetcher`` returns an ``HttpFetcher`` that follows redirects itself (httpx's
  automatic following is off), re-checking every hop against the allow-list, and
  enforces a redirect limit, a body-size cap and a wall-clock timeout. Every failure,
  including a non-2xx status such as 429 (never retried), is returned as a failed
  ``FetchResult`` rather than raised.

The client never reads proxy settings, ``.netrc`` or other environment state
(``trust_env=False``), and only the URLs it is given are requested: links inside a
response body are never followed. URLs echoed into results and events have any
userinfo removed.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Mapping
from typing import Final

import httpx

from job_search_agent.config import HttpSettings
from job_search_agent.errors import HostNotAllowed
from job_search_agent.models import FetchErrorKind, FetchResult
from job_search_agent.ports import EventSink, HttpFetcher, JsonValue

REDIRECT_STATUSES: Final = frozenset({301, 302, 303, 307, 308})
"""Statuses treated as redirects (each hop is re-checked)."""

KEPT_HEADERS: Final = (
    "cache-control",
    "content-encoding",
    "content-length",
    "content-type",
    "date",
    "etag",
    "last-modified",
    "retry-after",
)
"""Response headers copied into ``FetchResult.headers`` (no cookies, no auth)."""

_ALLOWED_PORTS: Final = (None, 443)


def _redact(url: httpx.URL) -> str:
    """Returns ``url`` as a string with any userinfo removed."""
    if url.userinfo:
        url = url.copy_with(userinfo=b"")
    return str(url)


def check_url(url: httpx.URL, allowed_hosts: frozenset[str]) -> None:
    """Raises unless ``url`` may be requested.

    Args:
        url: The candidate URL.
        allowed_hosts: Exact, lowercase host names.

    Raises:
        HostNotAllowed: With reason ``"scheme"``, ``"userinfo"``, ``"host"`` or
            ``"port"``.
    """
    host = url.host.lower()
    if url.scheme != "https":
        raise HostNotAllowed(host, "scheme")
    if url.userinfo:
        raise HostNotAllowed(host, "userinfo")
    if host not in allowed_hosts:
        raise HostNotAllowed(host, "host")
    if url.port not in _ALLOWED_PORTS:
        raise HostNotAllowed(host, "port")


def _normalise_hosts(hosts: Iterable[str]) -> frozenset[str]:
    if isinstance(hosts, str):
        raise TypeError("allowed_hosts must be an iterable of host names, not a str")
    return frozenset(host.lower() for host in hosts)


class AllowListTransport(httpx.BaseTransport):
    """Refuses off-list requests before the inner transport is called.

    Args:
        inner: The transport that actually sends requests.
        allowed_hosts: Exact host names (compared lowercase). An empty set refuses
            everything.
    """

    def __init__(
        self, inner: httpx.BaseTransport, allowed_hosts: Iterable[str]
    ) -> None:
        self._inner = inner
        self._allowed = _normalise_hosts(allowed_hosts)

    @property
    def allowed_hosts(self) -> frozenset[str]:
        """The exact host names this transport lets through."""
        return self._allowed

    def check(self, url: httpx.URL) -> None:
        """Raises ``HostNotAllowed`` unless ``url`` passes the allow-list."""
        check_url(url, self._allowed)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Checks the request URL, then delegates.

        Args:
            request: The outgoing request.

        Returns:
            The inner transport's response.

        Raises:
            HostNotAllowed: If the URL fails the allow-list.
        """
        self.check(request.url)
        return self._inner.handle_request(request)

    def close(self) -> None:
        """Closes the inner transport."""
        self._inner.close()


class _Failure(Exception):  # noqa: N818 - internal control flow only
    """Internal: ends a fetch with an error kind."""

    def __init__(self, kind: FetchErrorKind, detail: str) -> None:
        super().__init__(detail)
        self.kind = kind
        self.detail = detail


class AllowListFetcher:
    """``HttpFetcher`` over an ``AllowListTransport``; build it with ``build_fetcher``.

    Args:
        transport: The allow-list transport.
        timeout_s: Per-operation httpx timeout and overall wall-clock budget.
        max_bytes: Largest accepted (decoded) body.
        max_redirects: Largest number of redirects followed.
        user_agent: ``User-Agent`` header value.
        events: Optional event sink.
        monotonic: Clock for the wall-clock budget (injected by tests).
    """

    def __init__(
        self,
        transport: AllowListTransport,
        *,
        timeout_s: float,
        max_bytes: int,
        max_redirects: int,
        user_agent: str,
        events: EventSink | None = None,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        if timeout_s <= 0 or max_bytes <= 0 or max_redirects < 0:
            raise ValueError("timeout_s, max_bytes must be > 0; max_redirects >= 0")
        self._transport = transport
        self._timeout_s = timeout_s
        self._max_bytes = max_bytes
        self._max_redirects = max_redirects
        self._user_agent = user_agent
        self._events = events
        self._monotonic = monotonic

    def _emit(self, event: str, fields: Mapping[str, JsonValue]) -> None:
        if self._events is not None:
            self._events.emit(event, fields)

    def get(self, url: str) -> FetchResult:
        """Performs one GET; see ``ports.HttpFetcher``.

        Args:
            url: Absolute HTTPS URL on an allow-listed host.

        Returns:
            The result; failures are reported through ``error``.
        """
        start = self._monotonic()
        try:
            parsed = httpx.URL(url)
        except (httpx.InvalidURL, TypeError):
            self._emit("http.rejected", {"host": "", "reason": "invalid_url", "hop": 0})
            return FetchResult(
                requested_url="<invalid url>",
                final_url=None,
                redirect_chain=(),
                status_code=None,
                headers={},
                body=None,
                error=FetchErrorKind.HOST_REJECTED,
                error_detail="invalid_url",
                elapsed_ms=0,
            )
        state = _Exchange(requested=_redact(parsed), current=parsed)
        try:
            self._run(state, start)
        except _Failure as failure:
            state.error = failure.kind
            state.detail = failure.detail
            self._emit(
                "http.error", {"kind": failure.kind.value, "detail": failure.detail}
            )
        elapsed_ms = int((self._monotonic() - start) * 1000)
        if state.error is None:
            self._emit(
                "http.response",
                {
                    "url": _redact(state.current),
                    "status": state.status,
                    "bytes": len(state.body or b""),
                    "elapsed_ms": elapsed_ms,
                },
            )
        return FetchResult(
            requested_url=state.requested,
            final_url=_redact(state.current) if state.status is not None else None,
            redirect_chain=tuple(state.chain),
            status_code=state.status,
            headers=state.headers,
            body=state.body,
            error=state.error,
            error_detail=state.detail,
            elapsed_ms=elapsed_ms,
        )

    def _run(self, state: _Exchange, start: float) -> None:
        deadline = start + self._timeout_s
        with httpx.Client(
            transport=self._transport,
            follow_redirects=False,
            trust_env=False,
            timeout=httpx.Timeout(self._timeout_s),
            headers={"User-Agent": self._user_agent, "Accept": "application/json"},
        ) as client:
            hop = 0
            while True:
                self._check_hop(state.current, hop)
                if self._monotonic() > deadline:
                    raise _Failure(FetchErrorKind.TIMEOUT, "deadline")
                self._emit("http.request", {"url": _redact(state.current), "hop": hop})
                next_url = self._send(client, state, deadline, hop)
                if next_url is None:
                    return
                state.chain.append(_redact(state.current))
                state.current = next_url
                hop += 1

    def _check_hop(self, url: httpx.URL, hop: int) -> None:
        try:
            self._transport.check(url)
        except HostNotAllowed as exc:
            self._emit(
                "http.rejected", {"host": exc.host, "reason": exc.reason, "hop": hop}
            )
            kind = (
                FetchErrorKind.HOST_REJECTED
                if hop == 0
                else FetchErrorKind.REDIRECT_REJECTED
            )
            raise _Failure(kind, f"{exc.reason}: {exc.host}") from None

    def _send(
        self, client: httpx.Client, state: _Exchange, deadline: float, hop: int
    ) -> httpx.URL | None:
        """Sends one request; returns the next URL for a redirect, else None."""
        try:
            with client.stream("GET", state.current) as response:
                state.status = response.status_code
                state.headers = {
                    name: response.headers[name]
                    for name in KEPT_HEADERS
                    if name in response.headers
                }
                if response.status_code in REDIRECT_STATUSES:
                    return self._redirect_target(response, state, hop)
                state.body = self._read_body(response, deadline)
                if not response.is_success:
                    raise _Failure(
                        FetchErrorKind.HTTP_STATUS, f"status {response.status_code}"
                    )
                return None
        except HostNotAllowed as exc:  # the transport's own check (defence in depth)
            kind = (
                FetchErrorKind.HOST_REJECTED
                if hop == 0
                else (FetchErrorKind.REDIRECT_REJECTED)
            )
            raise _Failure(kind, f"{exc.reason}: {exc.host}") from None
        except httpx.TimeoutException:
            raise _Failure(FetchErrorKind.TIMEOUT, "timeout") from None
        except httpx.HTTPError as exc:
            raise _Failure(FetchErrorKind.TRANSPORT, type(exc).__name__) from None

    def _redirect_target(
        self, response: httpx.Response, state: _Exchange, hop: int
    ) -> httpx.URL:
        location = response.headers.get("location")
        if not location:
            raise _Failure(FetchErrorKind.HTTP_STATUS, "redirect without location")
        if hop >= self._max_redirects:
            raise _Failure(
                FetchErrorKind.TOO_MANY_REDIRECTS, f"limit {self._max_redirects}"
            )
        try:
            target = state.current.join(location)
        except httpx.InvalidURL:
            raise _Failure(FetchErrorKind.REDIRECT_REJECTED, "invalid_url") from None
        self._emit(
            "http.redirect",
            {
                "status": response.status_code,
                "from": _redact(state.current),
                "to_host": target.host.lower(),
                "hop": hop,
            },
        )
        return target

    def _read_body(self, response: httpx.Response, deadline: float) -> bytes:
        """Reads the body, enforcing ``max_bytes`` and the overall deadline.

        ``Content-Length`` is the size of the *encoded* body (after any
        ``Content-Encoding`` such as gzip), so a declared length over the cap is an
        early refusal only. The cap itself applies to the *decoded* bytes that
        ``iter_bytes`` yields, which are what is saved and parsed; a small
        compressed body that inflates past the cap is still refused.

        Raises:
            _Failure: ``SIZE_CAP`` or ``TIMEOUT``.
        """
        declared = response.headers.get("content-length")
        if (
            declared is not None
            and declared.isdigit()
            and int(declared) > self._max_bytes
        ):
            raise _Failure(FetchErrorKind.SIZE_CAP, f"limit {self._max_bytes}")
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_bytes():
            total += len(chunk)
            if total > self._max_bytes:
                raise _Failure(FetchErrorKind.SIZE_CAP, f"limit {self._max_bytes}")
            if self._monotonic() > deadline:
                raise _Failure(FetchErrorKind.TIMEOUT, "deadline")
            chunks.append(chunk)
        return b"".join(chunks)


class _Exchange:
    """Mutable bookkeeping for one ``get`` call."""

    def __init__(self, *, requested: str, current: httpx.URL) -> None:
        self.requested = requested
        self.current = current
        self.chain: list[str] = []
        self.status: int | None = None
        self.headers: dict[str, str] = {}
        self.body: bytes | None = None
        self.error: FetchErrorKind | None = None
        self.detail: str | None = None


def build_fetcher(
    allowed_hosts: Iterable[str],
    *,
    user_agent: str,
    inner: httpx.BaseTransport | None = None,
    timeout_s: float = 30.0,
    max_bytes: int = 50_000_000,
    max_redirects: int = 3,
    events: EventSink | None = None,
    monotonic: Callable[[], float] = time.monotonic,
) -> HttpFetcher:
    """Builds the allow-listed fetcher.

    Args:
        allowed_hosts: Exact host names, e.g. ``["boards-api.greenhouse.io"]``.
        user_agent: ``User-Agent`` header value.
        inner: Transport that sends requests; defaults to a TLS-verifying
            ``httpx.HTTPTransport`` with no retries that ignores the environment.
        timeout_s: Per-operation timeout and overall wall-clock budget.
        max_bytes: Body-size cap (decoded bytes).
        max_redirects: Redirects followed before ``TOO_MANY_REDIRECTS``.
        events: Optional sink for ``http.*`` events.
        monotonic: Clock for the wall-clock budget.

    Returns:
        An ``HttpFetcher``.

    Raises:
        ValueError: If a limit is out of range.
        TypeError: If ``allowed_hosts`` is a bare string.
    """
    transport = AllowListTransport(
        inner
        if inner is not None
        else httpx.HTTPTransport(verify=True, retries=0, trust_env=False),
        allowed_hosts,
    )
    return AllowListFetcher(
        transport,
        timeout_s=timeout_s,
        max_bytes=max_bytes,
        max_redirects=max_redirects,
        user_agent=user_agent,
        events=events,
        monotonic=monotonic,
    )


def build_fetcher_from_settings(
    settings: HttpSettings,
    *,
    inner: httpx.BaseTransport | None = None,
    events: EventSink | None = None,
) -> HttpFetcher:
    """Builds the fetcher from the ``[http]`` config section.

    Args:
        settings: The validated ``[http]`` settings.
        inner: Optional inner transport (tests).
        events: Optional event sink.

    Returns:
        An ``HttpFetcher``.
    """
    return build_fetcher(
        settings.allowed_hosts,
        user_agent=settings.user_agent,
        inner=inner,
        timeout_s=settings.timeout_s,
        max_bytes=settings.max_bytes,
        max_redirects=settings.max_redirects,
        events=events,
    )
