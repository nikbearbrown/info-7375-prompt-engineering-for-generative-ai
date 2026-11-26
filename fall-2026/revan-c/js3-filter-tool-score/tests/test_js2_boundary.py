"""Boundary tests B01-B16 from GATE.md, "Predicted boundary cases".

Each docstring repeats the prediction Revan wrote in GATE.md (commit f3072e5) before any JS2 code existed.
Tests marked EXTRA are not in GATE.md's table; Claude Code added them while writing the tests.
"""
import http.client
import os

import pytest

from jsloop.fetch import http_get
from jsloop.loop import run_watch
from jsloop.policy import DEMO_SELECTION, NORMAL_SELECTION, PolicyDenied, Workspace, check_request
from js2_support import (DUOLINGO, KLAVIYO, MISSING, PATCHMYPC, FakeClock, FakeFetcher, file_bytes,
                         gh_body, gh_job, good_responses, make_workspace, ok)


def _run(base, selection=NORMAL_SELECTION, responses=None, **kw):
    fetcher = kw.pop("fetcher", None) or FakeFetcher(responses or good_responses())
    clock = kw.pop("clock", None) or FakeClock()
    return run_watch(selection, base_dir=base, fetcher=fetcher, clock=clock, **kw), fetcher


# ---- network -------------------------------------------------------------------------------------

def test_B01_klaviyo_get_allowed_and_counted(tmp_path):
    """B01 predicted: Allow and count one request."""
    assert check_request("GET", KLAVIYO).name == "klaviyo"
    trace, fetcher = _run(make_workspace(tmp_path), ["klaviyo"])
    assert [u for u, _ in fetcher.calls] == [KLAVIYO]
    assert trace["requests_made"] == 1


def test_B02_lever_get_allowed_and_counted(tmp_path):
    """B02 predicted: Allow and count one request."""
    assert check_request("GET", PATCHMYPC).name == "patchmypc"
    trace, fetcher = _run(make_workspace(tmp_path), ["patchmypc"])
    assert [u for u, _ in fetcher.calls] == [PATCHMYPC]
    assert trace["requests_made"] == 1


def test_B03_host_off_allow_list_denied():
    """B03 predicted: Deny: host off the allow-list."""
    with pytest.raises(PolicyDenied) as exc:
        check_request("GET", "https://example.com/jobs")
    assert exc.value.rule == "host"


@pytest.mark.parametrize("url", [
    "https://boards-api.greenhouse.io.evil.com/v1/boards/klaviyo/jobs?content=true",
    "https://evil-boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true",  # EXTRA variant
    "https://api.lever.co.evil.com/v0/postings/patchmypc?mode=json",              # EXTRA variant
])
def test_B03a_look_alike_host_denied(url):
    """B03a predicted: Deny: look-alike host is not the exact allowed hostname."""
    with pytest.raises(PolicyDenied) as exc:
        check_request("GET", url)
    assert exc.value.rule == "host"


@pytest.mark.parametrize("url", [
    "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true",
    "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs",                 # EXTRA: query dropped
    "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true#x",  # EXTRA: fragment
    "https://api.lever.co/v0/postings/patchmypc/apply?mode=json",              # EXTRA: an apply-like path
])
def test_B04_unlisted_endpoint_on_allowed_host_denied(url):
    """B04 predicted: Deny: endpoint off the exact allow-list."""
    with pytest.raises(PolicyDenied) as exc:
        check_request("GET", url)
    assert exc.value.rule == "endpoint"


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_B05_non_get_method_denied(method):
    """B05 predicted: Deny: method is not GET."""
    with pytest.raises(PolicyDenied) as exc:
        check_request(method, KLAVIYO)
    assert exc.value.rule == "method"


@pytest.mark.parametrize("url, rule", [
    ("http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true", "scheme"),
    ("https://boards-api.greenhouse.io:8443/v1/boards/klaviyo/jobs?content=true", "port"),
    ("https://user:pw@boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true", "credentials"),  # EXTRA
])
def test_B06_scheme_port_or_credentials_differ_denied(url, rule):
    """B06 predicted: Deny: scheme or port differs."""
    with pytest.raises(PolicyDenied) as exc:
        check_request("GET", url)
    assert exc.value.rule == rule


class _RedirectingConnection:
    """Stands in for http.client.HTTPSConnection; every request gets a 302 to another host."""
    instances = []

    def __init__(self, host, timeout=None, **kw):
        self.host, self.timeout, self.requests = host, timeout, []
        _RedirectingConnection.instances.append(self)

    def request(self, method, path, headers=None):
        self.requests.append((method, path))

    def getresponse(self):
        class _Resp:
            status = 302

            def getheader(self, name, default=None):
                return "https://evil.example/jobs" if name.lower() == "location" else default

            def read(self):
                return b"moved"
        return _Resp()

    def close(self):
        pass


def test_B07_redirect_is_refused_and_not_followed(monkeypatch, tmp_path):
    """B07 predicted: Deny the redirect; make no second request."""
    _RedirectingConnection.instances = []
    monkeypatch.setattr(http.client, "HTTPSConnection", _RedirectingConnection)
    result = http_get(KLAVIYO, timeout=8)
    assert result.status == 302
    assert "redirect" in result.error and "evil.example" in result.error
    assert len(_RedirectingConnection.instances) == 1
    assert len(_RedirectingConnection.instances[0].requests) == 1

    # In the loop, the redirected board fails; the run counts exactly one request for it.
    responses = good_responses() | {KLAVIYO: result}
    trace, fetcher = _run(make_workspace(tmp_path), responses=responses)
    board = trace["boards"][0]
    assert board["outcome"] == "failed" and board["http_status"] == 302
    assert [u for u, _ in fetcher.calls].count(KLAVIYO) == 1
    assert trace["status"] == "incomplete"


# ---- files ---------------------------------------------------------------------------------------

def test_B08_dotdot_escape_denied(tmp_path):
    """B08 predicted: Deny: resolved path escapes the output folder."""
    ws = Workspace(make_workspace(tmp_path))
    with pytest.raises(PolicyDenied) as exc:
        ws.write_new("runs/js2/../outside.json", b"x")
    assert exc.value.rule == "outside-write-roots"
    assert not (ws.base / "runs" / "outside.json").exists()


def test_B09_sibling_prefix_denied(tmp_path):
    """B09 predicted: Deny: sibling prefix is not containment."""
    ws = Workspace(make_workspace(tmp_path))
    with pytest.raises(PolicyDenied) as exc:
        ws.write_new("runs/js2-evil/result.json", b"x")
    assert exc.value.rule == "outside-write-roots"
    assert not (ws.base / "runs" / "js2-evil").exists()


@pytest.mark.parametrize("how", ["directory link", "file link"])
def test_B10_symlink_escape_denied(tmp_path, how):
    """B10 predicted: Deny: resolved path escapes the folder."""
    base = make_workspace(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (base / "runs" / "js2").mkdir(parents=True)
    if how == "directory link":
        os.symlink(outside, base / "runs" / "js2" / "link")
        target = "runs/js2/link/result.json"
    else:
        os.symlink(outside / "result.json", base / "runs" / "js2" / "result.json")
        target = "runs/js2/result.json"
    ws = Workspace(base)
    with pytest.raises(PolicyDenied) as exc:
        ws.write_new(target, b"x")
    assert exc.value.rule == "outside-write-roots"
    assert list(outside.iterdir()) == []


def test_B11_seeded_fixture_read_allowed_but_not_write(tmp_path):
    """B11 predicted: Allow read only; do not grant write."""
    base = make_workspace(tmp_path)
    fixture = base / "fixtures" / "js2" / "klaviyo_seeded.json"
    fixture.write_bytes(gh_body(gh_job(1)))
    ws = Workspace(base)
    assert ws.read_bytes("fixtures/js2/klaviyo_seeded.json") == fixture.read_bytes()
    with pytest.raises(PolicyDenied):
        ws.check_write("fixtures/js2/klaviyo_seeded.json")


def test_B11_read_outside_read_roots_denied(tmp_path):
    """EXTRA (not in GATE.md's table): reading a file outside the read roots is denied."""
    base = make_workspace(tmp_path)
    (base / "CONTRACT.md").write_text("not an agent input")
    with pytest.raises(PolicyDenied) as exc:
        Workspace(base).read_bytes("CONTRACT.md")
    assert exc.value.rule == "outside-read-roots"


def test_B12_write_to_seeded_fixture_denied(tmp_path):
    """B12 predicted: Deny: input read permission is not output write permission."""
    base = make_workspace(tmp_path)
    fixture = base / "fixtures" / "js2" / "klaviyo_seeded.json"
    fixture.write_bytes(gh_body(gh_job(1)))
    before = fixture.read_bytes()
    ws = Workspace(base)
    with pytest.raises(PolicyDenied) as exc:
        ws.write_new("fixtures/js2/klaviyo_seeded-2.json", b"x")
    assert exc.value.rule == "read-only"
    with pytest.raises(PolicyDenied):
        ws.replace("fixtures/js2/klaviyo_seeded.json", b"overwritten", approve_state_write=True)
    assert fixture.read_bytes() == before


def test_B13_run_without_approval_observes_but_never_writes_state(tmp_path):
    """B13 predicted: Allow observation and trace writes; deny any state write and report state_updated: false."""
    base = make_workspace(tmp_path)
    trace, fetcher = _run(base)
    assert len(fetcher.calls) == 3
    assert trace["status"] == "finished"
    assert trace["state_updated"] is False
    assert (base / trace["trace_path"]).exists()
    assert not (base / "state" / "js2" / "seen_ids.json").exists()
    with pytest.raises(PolicyDenied) as exc:
        Workspace(base).replace("state/js2/seen_ids.json", b"{}")
    assert exc.value.rule == "needs-approval"
    assert not (base / "state" / "js2" / "seen_ids.json").exists()


def test_B14_state_write_with_approval_allowed_inside_state(tmp_path):
    """B14 predicted: Allow if the resolved path stays in state/js2/."""
    base = make_workspace(tmp_path)
    trace, _ = _run(base, approve_state_write=True)
    assert trace["state_updated"] is True
    assert (base / "state" / "js2" / "seen_ids.json").exists()
    # The flag grants only state/js2: it does not open a path that escapes it.
    with pytest.raises(PolicyDenied):
        Workspace(base).replace("state/js2/../escaped.json", b"{}", approve_state_write=True)


def test_B15_deliberate_failure_board_needs_demo_mode(tmp_path):
    """B15 predicted: Deny at preflight."""
    with pytest.raises(PolicyDenied) as exc:
        check_request("GET", MISSING)
    assert exc.value.rule == "demo-only"
    trace, fetcher = _run(make_workspace(tmp_path), DEMO_SELECTION,
                          responses=good_responses() | {MISSING: ok(b"")})
    assert trace["status"] == "error"
    assert fetcher.calls == []


def test_B16_request_not_started_with_under_10_seconds_left(tmp_path):
    """B16 predicted: Do not send it; report budget-exhausted because fewer than 10 seconds remain."""
    clock = FakeClock()
    # Klaviyo's request takes 40 s of the 45 s deadline, so Duolingo's would start at second 40.
    fetcher = FakeFetcher(good_responses(), clock=clock, advance_by={KLAVIYO: 40})
    trace, _ = _run(make_workspace(tmp_path), fetcher=fetcher, clock=clock)
    assert [u for u, _ in fetcher.calls] == [KLAVIYO]
    assert trace["status"] == "budget-exhausted"
    assert trace["stop_reason"]["limit"] == "seconds"
    assert [b["outcome"] for b in trace["boards"]] == ["ok", "not_attempted", "not_attempted"]
    assert DUOLINGO not in [u for u, _ in fetcher.calls]
