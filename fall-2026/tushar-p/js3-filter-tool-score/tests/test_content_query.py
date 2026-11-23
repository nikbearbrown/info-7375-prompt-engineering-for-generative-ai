"""JS3 gate change (FILTER.md "Expected sources", dated 2026-11-21).

The single exact query `content=true` is allowed on the Greenhouse listing route only.
Every other query, and any query on Ashby, stays denied before transport. All responses
here are synthetic.
"""

import json

import pytest

from agent import loop
from agent.config import parse_config
from agent.errors import ConfigError, RequestDenied
from agent.providers import Board, fetch_url, listing_url
from agent.transport import Response, send
from support import FakeClock, TransportSpy

STRIPE = Board("greenhouse", "stripe")
STRIPE_TEXT = Board("greenhouse", "stripe", content=True)
NOTION = Board("ashby", "notion")
GH_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
ASHBY_URL = "https://api.ashbyhq.com/posting-api/job-board/notion"
TIMEOUT = 10


def assert_denied_before_transport(board, url):
    spy = TransportSpy()
    with pytest.raises(RequestDenied):
        send(board, "GET", url, transport=spy, timeout=TIMEOUT)
    assert spy.calls == []


def test_greenhouse_content_true_allowed():
    spy = TransportSpy()
    response = send(STRIPE, "GET", GH_URL + "?content=true", transport=spy, timeout=TIMEOUT)
    assert spy.calls == [("GET", GH_URL + "?content=true", TIMEOUT)]
    assert response.status == 200


@pytest.mark.parametrize("query", ["?content=false", "?foo=1", "?content=true&x=1"])
def test_greenhouse_other_queries_denied(query):
    assert_denied_before_transport(STRIPE, GH_URL + query)


@pytest.mark.parametrize("query", ["?", "?content=True", "?CONTENT=true", "?content=true#x",
                                   "?x=1&content=true", "?content=true?", "?content=true&content=true"])
def test_greenhouse_near_miss_queries_denied(query):
    """Boundary cases: only the exact spelling passes."""
    assert_denied_before_transport(STRIPE, GH_URL + query)


def test_ashby_content_true_denied():
    assert_denied_before_transport(NOTION, ASHBY_URL + "?content=true")


def test_content_query_does_not_widen_route_or_host():
    """The query is allowed only on the configured board's listing route and host."""
    assert_denied_before_transport(STRIPE, "https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true")
    assert_denied_before_transport(STRIPE, GH_URL + "/123?content=true")
    assert_denied_before_transport(STRIPE, "https://example.com/v1/boards/stripe/jobs?content=true")
    assert_denied_before_transport(STRIPE, GH_URL.replace("https://", "http://") + "?content=true")
    spy = TransportSpy()
    with pytest.raises(RequestDenied):
        send(STRIPE, "POST", GH_URL + "?content=true", transport=spy, timeout=TIMEOUT)
    assert spy.calls == []


def test_fetch_url_adds_query_only_when_board_opts_in():
    assert listing_url(STRIPE_TEXT) == GH_URL  # the listing URL itself is unchanged (P01)
    assert fetch_url(STRIPE_TEXT) == GH_URL + "?content=true"
    assert fetch_url(STRIPE) == GH_URL
    assert fetch_url(NOTION) == ASHBY_URL


def test_config_content_flag_greenhouse_only():
    cfg = parse_config(json.dumps({"boards": [
        {"provider": "greenhouse", "token": "stripe", "content": True},
        {"provider": "ashby", "token": "notion"}]}).encode())
    assert [b.content for b in cfg.boards] == [True, False]
    with pytest.raises(ConfigError):
        parse_config(b'{"boards": [{"provider": "ashby", "token": "notion", "content": true}]}')
    with pytest.raises(ConfigError):
        parse_config(b'{"boards": [{"provider": "greenhouse", "token": "stripe", "content": "true"}]}')
    with pytest.raises(ConfigError):
        parse_config(b'{"boards": [{"provider": "greenhouse", "token": "stripe", "query": "x=1"}]}')


def test_content_flag_does_not_defeat_duplicate_detection():
    cfg = parse_config(json.dumps({"boards": [
        {"provider": "greenhouse", "token": "stripe", "content": True},
        {"provider": "greenhouse", "token": "stripe"}]}).encode())
    assert len(cfg.boards) == 1 and len(cfg.duplicates) == 1


def test_loop_requests_content_url_for_opted_in_board(tmp_path):
    config = tmp_path / "boards.json"
    config.write_text(json.dumps({"boards": [{"provider": "greenhouse", "token": "stripe", "content": True}]}))
    url = GH_URL + "?content=true"
    body = json.dumps({"_synthetic": True, "jobs": [{"id": 1, "content": "&lt;p&gt;x&lt;/p&gt;"}]}).encode()
    clock = FakeClock()
    spy = TransportSpy(routes={url: [Response(url, 200, (("Content-Type", "application/json"),), body)]},
                       clock=clock)
    out = tmp_path / "out"
    out.mkdir()
    result = loop.run(config, out, transport=spy, clock=clock, sleep=clock.sleep, run_id="run-test-1")
    assert result.exit == "finished"
    assert spy.urls() == [url]
    raw = out / "runs" / "run-test-1" / "raw" / "greenhouse" / "stripe" / "attempt-1.raw"
    assert raw.read_bytes() == body
