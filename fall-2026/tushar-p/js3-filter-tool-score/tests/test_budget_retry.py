"""Attempts, retries, and timing (GATE "Board failure policy"; F8–F13; Wrong versions)."""

import socket

import pytest

from agent.budget import ATTEMPTS, NETWORK_WINDOW, Budget
from agent.errors import TransportTimeout
from agent.providers import listing_url
from agent.transport import UrllibTransport, build_opener
from support import (INVALID, LINEAR, NOTION, STRIPE, FakeClock, FakeHTTPSHandler, Slow, SlowBody,
                     board_entry, dns_failure, ok, read_summary, read_trace, run_agent, status, timeout)


def fetch_events(out, board):
    return [e for e in read_trace(out) if e["operation"] == "fetch" and e["board"] == board.key]


def test_404_gets_one_attempt(tmp_path):
    """Wrong versions: "The loop retries a 404" -> the 404 gets one attempt (F9)."""
    clock = FakeClock()
    result, spy, out = run_agent(tmp_path, [INVALID], {INVALID: [status(INVALID, 404), ok(INVALID, [1])]},
                                 clock=clock)
    assert spy.urls() == [listing_url(INVALID)]
    assert clock.sleeps == []
    entry = board_entry(read_summary(out), INVALID)
    assert entry["attempts"] == 1 and entry["failure"]["kind"] == "http-404"
    assert entry["fetched"] is None and entry["new"] is None
    assert result.exit == "incomplete"


def test_timeout_retried_once_and_both_attempts_counted(tmp_path):
    """Wrong versions: "forgets to count a timeout retry" -> both attempts count (F8, F9)."""
    clock = FakeClock()
    result, spy, out = run_agent(tmp_path, [STRIPE], {STRIPE: [timeout(), ok(STRIPE, [1, 2])]}, clock=clock)
    assert result.exit == "finished"
    assert len(spy.calls) == 2
    summary = read_summary(out)
    assert summary["attempts_used"] == 2
    assert board_entry(summary, STRIPE)["attempts"] == 2
    events = fetch_events(out, STRIPE)
    assert [e["attempt"] for e in events] == [1, 2]
    assert events[0]["outcome"] == "timeout" and events[0]["next"].startswith("wait 1 s")
    assert clock.sleeps == [1]


@pytest.mark.parametrize("steps", [
    [timeout(), timeout()],
    [lambda: status(STRIPE, 503), timeout()],
    [lambda: status(STRIPE, 502), lambda: status(STRIPE, 503)],
], ids=["timeout-timeout", "503-timeout", "502-503"])
def test_at_most_one_retry(tmp_path, steps):
    """Wrong versions: "A transient failure gets at most one retry, and both attempts count." """
    clock = FakeClock()
    unused = ok(STRIPE, [1])
    result, spy, out = run_agent(tmp_path, [STRIPE], {STRIPE: steps + [unused]}, clock=clock)
    assert len(spy.calls) == 2
    assert clock.sleeps == [1]
    entry = board_entry(read_summary(out), STRIPE)
    assert entry["status"] == "failed" and entry["attempts"] == 2
    assert entry["failure"]["first_failure"] is not None
    assert result.exit == "incomplete"


def test_5xx_retried_and_raw_body_saved(tmp_path):
    """Board failure policy: an HTTP 5xx gets one retry after a 1-second wait; bytes are saved."""
    clock = FakeClock()
    result, spy, out = run_agent(tmp_path, [STRIPE],
                                 {STRIPE: [status(STRIPE, 503, b"upstream down"), ok(STRIPE, [5])]}, clock=clock)
    assert result.exit == "finished" and len(spy.calls) == 2 and clock.sleeps == [1]
    first = fetch_events(out, STRIPE)[0]
    assert first["status"] == 503
    assert (out / first["raw_path"]).read_bytes() == b"upstream down"


@pytest.mark.parametrize("step,kind", [
    (status(STRIPE, 429), "http-4xx"),
    (status(STRIPE, 400), "http-4xx"),
    (status(STRIPE, 302, b"moved", (("Location", "https://example.com/"),)), "redirect"),
    (dns_failure(), "transport-error"),
    (status(STRIPE, 200, b'{"jobs": "nope"}'), "malformed"),
], ids=["429", "400", "302", "dns-error", "malformed"])
def test_non_retryable_failures_get_one_attempt(tmp_path, step, kind):
    """F9: DNS errors, connection resets, 429, other 4xx, and 3xx are board failures with no retry."""
    clock = FakeClock()
    _, spy, out = run_agent(tmp_path, [STRIPE], {STRIPE: [step, ok(STRIPE, [1])]}, clock=clock)
    assert len(spy.calls) == 1
    assert clock.sleeps == []
    assert board_entry(read_summary(out), STRIPE)["failure"]["kind"] == kind


def test_retry_waits_one_second_then_retries_at_the_boundary(tmp_path):
    """Wrong versions: "the retry skips the wait" -> the retry waits 1 second (F11 boundary:
    exactly 2 s of network time left before the wait, exactly 1 s after it)."""
    clock = FakeClock()
    result, spy, out = run_agent(
        tmp_path, [NOTION, STRIPE],
        {NOTION: [Slow(46.0, ok(NOTION, ["a"]))],            # 12 s of network time left
         STRIPE: [Slow(10.0, timeout()), ok(STRIPE, [1])]},  # 2.0 s left -> wait -> 1.0 s left
        clock=clock)
    assert result.exit == "finished"
    assert clock.sleeps == [1]
    assert [t for _, _, t in spy.calls] == [10, 10, pytest.approx(1.0)]


def test_budget_rechecked_after_the_wait(tmp_path):
    """Wrong versions: "rechecks the budget" -> after the wait, F11's 1-second minimum is checked
    again; an overslept wait leaves too little time, so the retry is pending (F13)."""
    clock = FakeClock(oversleep=0.5)
    result, spy, out = run_agent(
        tmp_path, [NOTION, STRIPE],
        {NOTION: [Slow(46.0, ok(NOTION, ["a"]))], STRIPE: [Slow(10.0, timeout()), ok(STRIPE, [1])]},
        clock=clock)
    assert clock.sleeps == [1]
    assert len(spy.calls) == 2  # notion + stripe's first attempt; no retry started
    assert result.exit == "budget-exhausted"
    summary = read_summary(out)
    assert summary["budget_limit_hit"] == NETWORK_WINDOW
    assert {"board": STRIPE.key, "pending": "retry"} in summary["pending"]


def test_retry_pending_when_budget_short(tmp_path):
    """F11 + F13: with under 2 s of network time left, no wait starts; the retry is pending,
    the original failure stays in the trace, and the run exits budget-exhausted."""
    clock = FakeClock()
    result, spy, out = run_agent(
        tmp_path, [NOTION, STRIPE, LINEAR],
        {NOTION: [Slow(46.5, ok(NOTION, ["a"]))], STRIPE: [Slow(10.0, timeout()), ok(STRIPE, [1])],
         LINEAR: [ok(LINEAR, ["z"])]},
        clock=clock)
    assert clock.sleeps == []
    assert len(spy.calls) == 2
    assert result.exit == "budget-exhausted" and result.code == 4
    summary = read_summary(out)
    assert summary["pending"] == [{"board": STRIPE.key, "pending": "retry"},
                                  {"board": LINEAR.key, "pending": "board"}]
    stripe_events = fetch_events(out, STRIPE)
    assert stripe_events[0]["outcome"] == "timeout" and "retry pending" in stripe_events[0]["next"]
    assert board_entry(summary, STRIPE)["fetched"] is None
    assert summary["state"]["written"] is True  # F5: budget-exhausted still commits staged boards


def test_attempt_timeout_is_min_of_10_and_time_left(tmp_path):
    """Wrong versions: "A slow request gets the whole run budget" -> each attempt gets the smaller
    of 10 seconds and the time left in the network window (F10): 10, 10, then 58 - 53.5 = 4.5."""
    clock = FakeClock()
    _, spy, _ = run_agent(tmp_path, [NOTION, STRIPE, LINEAR],
                          {NOTION: [ok(NOTION, ["a"])], STRIPE: [Slow(53.5, ok(STRIPE, [1]))],
                           LINEAR: [ok(LINEAR, ["b"])]},
                          clock=clock)
    assert [t for _, _, t in spy.calls] == [10, 10, pytest.approx(4.5)]


def test_closed_network_window_starts_no_new_attempt(tmp_path):
    """GATE + F10: at 58 s the network window closes; later boards stay pending (budget-exhausted)."""
    clock = FakeClock()
    result, spy, out = run_agent(tmp_path, [NOTION, STRIPE],
                                 {NOTION: [Slow(58.0, ok(NOTION, ["a"]))], STRIPE: [ok(STRIPE, [1])]}, clock=clock)
    assert spy.urls() == [listing_url(NOTION)]
    assert result.exit == "budget-exhausted"
    summary = read_summary(out)
    assert summary["budget_limit_hit"] == NETWORK_WINDOW
    assert summary["pending"] == [{"board": STRIPE.key, "pending": "board"}]


def test_budget_attempt_limit_and_retry_boundaries():
    """GATE "12 HTTP attempts" + F11 boundaries, on the Budget object directly."""
    clock = FakeClock()
    budget = Budget(clock, clock.sleep)
    for _ in range(12):
        assert budget.check_attempt() is None
        budget.record_attempt()
    assert budget.check_attempt() == ATTEMPTS
    assert budget.check_retry_before_wait() == ATTEMPTS
    assert budget.check_retry_after_wait() == ATTEMPTS
    with pytest.raises(RuntimeError):
        budget.record_attempt()

    fresh = Budget(clock, clock.sleep)
    clock.advance(56.0)                      # exactly 2.0 s left
    assert fresh.check_retry_before_wait() is None
    clock.advance(0.001)                     # 1.999 s left
    assert fresh.check_retry_before_wait() == NETWORK_WINDOW
    clock.advance(0.999)                     # exactly 1.0 s left
    assert fresh.check_retry_after_wait() is None
    clock.advance(0.001)
    assert fresh.check_retry_after_wait() == NETWORK_WINDOW
    assert fresh.attempt_timeout() == pytest.approx(0.999)


def test_slow_chunked_body_read_stops_at_the_deadline():
    """Wrong versions: "A slow response read gets the whole run budget" -> the read respects
    the time left in the attempt (F12 deadline-bounded chunked read)."""
    clock = FakeClock()
    slow = SlowBody(clock, chunks=5, per_read=3.0)       # would need 15 s in total
    handler = FakeHTTPSHandler(200, "OK", {"Content-Type": "application/json"}, slow)
    transport = UrllibTransport(build_opener(https_handler=handler), clock=clock)
    start = clock()
    with pytest.raises(TransportTimeout):
        transport("GET", listing_url(STRIPE), 10)
    assert slow.reads == 4                               # reads start at 0, 3, 6, 9 s; none at 12 s
    assert clock() - start == pytest.approx(12.0)


def test_chunked_body_within_deadline_completes():
    """F12 control: the same chunked read finishes when it fits inside the attempt."""
    clock = FakeClock()
    slow = SlowBody(clock, chunks=5, per_read=1.0, chunk=b"ab")
    handler = FakeHTTPSHandler(200, "OK", {}, slow)
    response = UrllibTransport(build_opener(https_handler=handler), clock=clock)("GET", listing_url(STRIPE), 10)
    assert response.status == 200 and response.body == b"ab" * 5


def test_dns_lookup_overrun_aborts_the_attempt(monkeypatch):
    """F12: getaddrinfo is not bounded, but its elapsed time counts; the deadline is rechecked
    when it returns and an expired attempt never connects."""
    clock = FakeClock()
    lookups = []

    def slow_getaddrinfo(host, port, *args, **kwargs):
        lookups.append((host, port))
        clock.advance(11.0)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.1", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", slow_getaddrinfo)
    with pytest.raises(TransportTimeout, match="during the DNS lookup"):
        UrllibTransport(clock=clock)("GET", listing_url(STRIPE), 10)
    assert lookups == [("boards-api.greenhouse.io", 443)]
    # conftest makes socket.connect raise AssertionError, so reaching connect would fail differently.


def test_dns_within_deadline_goes_on_to_connect(monkeypatch):
    """F12 control: when the lookup returns in time, the attempt continues to the TCP connect
    (which the offline conftest blocks), showing the recheck is what stops an expired attempt."""
    clock = FakeClock()
    monkeypatch.setattr(socket, "getaddrinfo",
                        lambda host, port, *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.1", 443))])
    with pytest.raises(AssertionError, match="network access attempted"):
        UrllibTransport(clock=clock)("GET", listing_url(STRIPE), 10)
