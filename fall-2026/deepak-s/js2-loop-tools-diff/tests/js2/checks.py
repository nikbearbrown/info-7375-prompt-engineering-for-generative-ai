"""Checks shared by the boundary tests (B01-B16), the loop tests and the wrong-version tests (W01-W14).

Written by Claude Code (Claude Opus 5.5), 2026-11-10. Each check asserts the behavior GATE.md
requires and prints one evidence line. tests/js2/test_wrong_versions.py runs the same check
with a wrong implementation patched in and requires it to fail.
SEEDED inputs only; no network.
"""
import json
import os
import urllib.request
import urllib.response
from email.message import Message
from io import BytesIO

import pytest

from js2kit import (ASHBY, GH, JSON, LEVER_EU, LEVER_US, SeededTransport, FakeClock, board, board_result,
                    ok, run_dir, run_loop, seeded, summary, trace)
from jobwatch import policy as P
from jobwatch import tools as T

RUN_ID = "20261110T200000Z"


def evidence(case, decision, outcome):
    print(f"{case}: policy {decision}; outcome {outcome}")


def make(workdir, approver=None, transport=None):
    pol = P.Policy(workdir, run_id=RUN_ID)
    return pol, T.Tools(pol, transport=transport or SeededTransport({}), approver=approver)


def expect_fetch_denied(workdir, case, url):
    pol, tools = make(workdir)
    d = pol.check("fetch", url)
    assert d.decision == P.DENY, d
    with pytest.raises(T.PolicyDenied):
        tools.fetch_json(url)
    assert tools.transport.requests == []
    evidence(case, d.decision, "PolicyDenied raised; no request sent")


def expect_write_denied(workdir, case, path):
    pol, tools = make(workdir)
    d = pol.check("write", path)
    assert d.decision == P.DENY, d
    with pytest.raises(T.PolicyDenied):
        tools.write_file(path, b"x")
    evidence(case, d.decision, "PolicyDenied raised; nothing written")


# --- network ------------------------------------------------------------------------------
def check_B01(workdir):
    expect_fetch_denied(workdir, "B01", "https://example.com/x")


def check_B02(workdir):
    expect_fetch_denied(workdir, "B02", "https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs")
    expect_fetch_denied(workdir, "B02b", "https://evil.com/boards-api.greenhouse.io")


def check_B03(workdir):
    expect_fetch_denied(workdir, "B03", "https://boards-api.greenhouse.io@evil.com/")


def check_B04(workdir):
    expect_fetch_denied(workdir, "B04", "http://boards-api.greenhouse.io/v1/boards/stripe/jobs")


def check_B05(workdir):
    pol, _ = make(workdir)
    d = pol.check("fetch", "https://api.lever.co/v0/postings/x", method="POST")
    assert d.decision == P.DENY, d
    evidence("B05", d.decision, "no tool can send POST; policy.check denies the method")


START = "https://boards-api.greenhouse.io/v1/boards/seeded-gh/jobs"
TARGET = "https://api.lever.co/v0/postings/elsewhere?mode=json"


class Seeded302Handler(urllib.request.BaseHandler):
    """SEEDED: answers the allowed URL with a 302 to TARGET, and TARGET with a 200. Runs inside a
    real urllib opener, so the opener's own redirect handler decides whether TARGET is opened."""

    handler_order = 100  # before the real HTTPSHandler, so nothing reaches the network

    def __init__(self):
        self.opened = []

    def https_open(self, req):
        self.opened.append(req.full_url)
        hdrs = Message()
        if req.full_url == START:
            hdrs["Location"] = TARGET
            code, msg, body = 302, "Found", b""
        else:
            hdrs["Content-Type"] = "application/json"
            code, msg, body = 200, "OK", b"[]"
        resp = urllib.response.addinfourl(BytesIO(body), hdrs, req.full_url, code)
        resp.msg = msg
        return resp


def check_B06(workdir):
    handler = Seeded302Handler()
    pol, tools = make(workdir, transport=T.build_transport(extra_handlers=[handler]))
    d = pol.check("fetch", START)
    result = tools.fetch_json(START)
    assert handler.opened == [START], handler.opened
    assert result.status == 302 and result.headers.get("location") == TARGET
    from jobwatch.providers import BoardError, greenhouse

    parsed = greenhouse.parse(result, "greenhouse:seeded-gh")
    assert isinstance(parsed, BoardError) and parsed.kind == "redirect_refused" and not parsed.retryable
    evidence("B06", d.decision + " for the GET to the allowed host",
             "302 returned to the caller, Location not opened; board result FAILED redirect_refused")


def check_B15(workdir):
    expect_fetch_denied(workdir, "B15", "https://api.ashbyhq.com:8443/posting-api/job-board/x")


def check_B16(workdir):
    expect_fetch_denied(workdir, "B16", "https://203.0.113.10/v1/boards/stripe/jobs")


# --- disk ---------------------------------------------------------------------------------
def check_B07(workdir):
    expect_write_denied(workdir, "B07", "runs/../outside.txt")
    assert not (workdir / "outside.txt").exists()


def check_B08(workdir):
    expect_write_denied(workdir, "B08", "runs-evil/x.json")
    expect_write_denied(workdir, "B08b", f"runs/{RUN_ID}-evil/x.json")
    pol, _ = make(workdir)
    d = pol.check("read", "runs-evil/x.json")
    assert d.decision == P.DENY, d
    evidence("B08c (read runs-evil/x.json)", d.decision, "read refused")


def check_B09(workdir):
    outside = workdir.parent / "outside"
    outside.mkdir(exist_ok=True)
    rd = workdir / "runs" / RUN_ID
    rd.mkdir(parents=True, exist_ok=True)
    link = rd / "escape"
    if not link.is_symlink():
        os.symlink(outside, link)
    expect_write_denied(workdir, "B09", f"runs/{RUN_ID}/escape/x.json")
    assert not (outside / "x.json").exists()


def check_B10(workdir):
    expect_write_denied(workdir, "B10", "/tmp/x.json")


def check_B11(workdir):
    pol, tools = make(workdir)
    d = pol.check("read", "config/boards.json")
    assert d.decision == P.ALLOW, d
    assert tools.read_file("config/boards.json") == (workdir / "config" / "boards.json").read_bytes()
    evidence("B11", d.decision, "bytes returned (GATE.md section 5 lists config/ as readable)")


def check_B12(workdir):
    before = (workdir / "config" / "boards.json").read_bytes()
    pol, tools = make(workdir)
    d = pol.check("write", "config/boards.json")
    assert d.decision == P.NEEDS_APPROVAL, d
    with pytest.raises(T.ApprovalDenied):
        tools.write_file("config/boards.json", b"{}")
    assert tools.needs_deepak is True
    assert (workdir / "config" / "boards.json").read_bytes() == before
    evidence("B12", d.decision, "denied (non-interactive, no approver); file unchanged; needs_deepak true")


def check_B12_approved(workdir):
    asked = []
    pol, tools = make(workdir, approver=lambda action: asked.append(action) or True)
    tools.write_file("config/boards.json", b"{}")
    assert len(asked) == 1 and (workdir / "config" / "boards.json").read_bytes() == b"{}"


def check_B13(workdir):
    state = workdir / "state" / "seen.json"
    state.parent.mkdir(exist_ok=True)
    state.write_bytes(b'{"schema_version": 1, "boards": {}}')
    pol, tools = make(workdir)
    d = pol.check("write", "state/seen.json")
    assert d.decision == P.NEEDS_APPROVAL, d
    with pytest.raises(T.ApprovalDenied):
        tools.write_file("state/seen.json", b"{}")
    assert state.read_bytes() == b'{"schema_version": 1, "boards": {}}'
    assert tools.needs_deepak is True
    evidence("B13", d.decision, "denied (non-interactive, no approver); state unchanged; needs_deepak true")


def check_B14(workdir):
    pol, tools = make(workdir)
    path = os.path.expanduser("~/.ssh/id_rsa")
    d = pol.check("read", path)
    assert d.decision == P.DENY, d
    with pytest.raises(T.PolicyDenied):
        tools.read_file(path)
    evidence("B14", d.decision, "PolicyDenied raised; file not opened")


# --- loop checks used by W06-W14 ----------------------------------------------------------
def write_boards(workdir, boards):
    (workdir / "config" / "boards.json").write_text(json.dumps({"boards": boards}), encoding="utf-8")


def check_failed_board_not_zero(workdir):
    """W06: a 404 board has count null and new_ids null, never 0."""
    write_boards(workdir, [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io"),
                           board("greenhouse", "seeded-bad", "boards-api.greenhouse.io")])
    t = SeededTransport({GH.format("seeded-gh"): ok(seeded("SEEDED_greenhouse_two_jobs.json")),
                         GH.format("seeded-bad"): (404, seeded("SEEDED_greenhouse_404.json"), JSON)})
    assert run_loop(t) == 3
    bad = board_result(summary(workdir), "greenhouse:seeded-bad")
    assert bad["status"] == "FAILED" and bad["count"] is None and bad["new_ids"] is None, bad
    assert bad["reason"] == "http_404"


def check_timeout_twice_incomplete(workdir):
    """W07: a board that times out twice is FAILED and the run is INCOMPLETE, not FINISHED."""
    write_boards(workdir, [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io"),
                           board("lever", "seeded-lv", "api.eu.lever.co")])
    clock = FakeClock()
    t = SeededTransport({GH.format("seeded-gh"): ok(seeded("SEEDED_greenhouse_two_jobs.json")),
                         LEVER_EU.format("seeded-lv"): "timeout"}, clock=clock)
    code = run_loop(t, clock=clock)
    s = summary(workdir)
    lv = board_result(s, "lever:seeded-lv")
    assert lv["status"] == "FAILED" and lv["reason"] == "timeout" and lv["retries_used"] == 1, lv
    assert [r["url"] for r in t.requests].count(LEVER_EU.format("seeded-lv")) == 2
    assert code == 3 and s["exit"] == "INCOMPLETE"


def check_retries_counted(workdir):
    """W08: with max_requests 3 and three 5xx boards, the retry of board 2 is not sent."""
    budgets = json.loads((workdir / "config" / "budgets.json").read_text(encoding="utf-8"))
    budgets["max_requests"] = 3
    (workdir / "config" / "budgets.json").write_text(json.dumps(budgets), encoding="utf-8")
    write_boards(workdir, [board("greenhouse", f"seeded-5xx-{i}", "boards-api.greenhouse.io") for i in range(3)])
    t = SeededTransport({GH.format(f"seeded-5xx-{i}"): (503, b"", {}) for i in range(3)})
    code = run_loop(t)
    s = summary(workdir)
    assert len(t.requests) <= 3, t.requests
    assert code == 4 and s["exit"] == "BUDGET_EXHAUSTED" and s["budget_exhausted"]["budget"] == "max_requests"


def check_404_not_retried(workdir):
    """W09: a 404 is fetched once; no retry and no REPEAT."""
    write_boards(workdir, [board("greenhouse", "seeded-bad", "boards-api.greenhouse.io")])
    t = SeededTransport({GH.format("seeded-bad"): (404, seeded("SEEDED_greenhouse_404.json"), JSON)})
    run_loop(t)
    bad = board_result(summary(workdir), "greenhouse:seeded-bad")
    assert len(t.requests) == 1
    assert bad["reason"] == "http_404" and bad["retries_used"] == 0, bad
    assert not any(line["outcome"] == "REPEAT" for line in trace(workdir))


def check_html_200_fails(workdir):
    """W10: a Lever 200 with an HTML body is FAILED non_json after one retry, never [] / count 0."""
    write_boards(workdir, [board("lever", "seeded-lv", "api.eu.lever.co")])
    html = (200, seeded("SEEDED_lever_html_200.html"), {"Content-Type": "text/html; charset=utf-8"})
    t = SeededTransport({LEVER_EU.format("seeded-lv"): html})
    code = run_loop(t)
    lv = board_result(summary(workdir), "lever:seeded-lv")
    assert lv["status"] == "FAILED" and lv["reason"] == "non_json" and lv["count"] is None, lv
    assert len(t.requests) == 2 and code == 3


def check_html_200_with_json_content_type_fails(workdir):
    """W10, second form: the content-type says JSON but the body is HTML."""
    write_boards(workdir, [board("lever", "seeded-lv", "api.eu.lever.co")])
    t = SeededTransport({LEVER_EU.format("seeded-lv"): (200, seeded("SEEDED_lever_html_200.html"), JSON)})
    run_loop(t)
    lv = board_result(summary(workdir), "lever:seeded-lv")
    assert lv["status"] == "FAILED" and lv["reason"] == "non_json" and lv["count"] is None, lv


def two_runs_lever_6_then_0(workdir, second_host="api.lever.co"):
    """Run 1: lever:seeded-lv on the EU host with 6 postings. Run 2: same board on `second_host`, 0 postings."""
    from datetime import timedelta
    from js2kit import NOW

    write_boards(workdir, [board("lever", "seeded-lv", "api.eu.lever.co")])
    assert run_loop(SeededTransport({LEVER_EU.format("seeded-lv"): ok(seeded("SEEDED_lever_six.json"))})) == 0
    write_boards(workdir, [board("lever", "seeded-lv", second_host)])
    later = NOW + timedelta(minutes=5)
    url = (LEVER_US if second_host == "api.lever.co" else LEVER_EU).format("seeded-lv")
    code = run_loop(SeededTransport({url: ok(seeded("SEEDED_lever_empty.json"))}), now=later)
    return code, later


def check_verify_flags_suspect(workdir, capsys):
    """W11: the loop ends FINISHED on the empty 200; verify flags SUSPECT and exits 2."""
    from jobwatch import cli

    code, later = two_runs_lever_6_then_0(workdir)
    assert code == 0 and summary(workdir, later)["exit"] == "FINISHED"
    capsys.readouterr()
    assert cli.main(["verify", str(run_dir(workdir, later).relative_to(workdir))]) == 2
    out = capsys.readouterr().out
    assert "SUSPECT" in out and "lever:seeded-lv" in out, out


def check_identity_ignores_host(workdir):
    """W12: moving a board from the EU host to the US host keeps its state key; run 2 is not a baseline."""
    code, later = two_runs_lever_6_then_0(workdir)
    state = json.loads((workdir / "state" / "seen.json").read_text(encoding="utf-8"))
    assert list(state["boards"]) == ["lever:seeded-lv"], state["boards"].keys()
    lv = board_result(summary(workdir, later), "lever:seeded-lv")
    assert lv["baseline"] is False, lv


def check_duplicate_board_is_error(workdir):
    """W13: one (system, slug) twice, with two hosts, ends ERROR before any fetch."""
    write_boards(workdir, [board("lever", "seeded-lv", "api.eu.lever.co"), board("lever", "seeded-lv", "api.lever.co")])
    t = SeededTransport({})
    assert run_loop(t) == 1
    assert t.requests == [] and summary(workdir)["exit"] == "ERROR"


def check_host_system_mismatch_is_error(workdir):
    """W14: {system: greenhouse, host: api.lever.co} ends ERROR before any fetch."""
    write_boards(workdir, [board("greenhouse", "seeded-gh", "api.lever.co")])
    t = SeededTransport({})
    assert run_loop(t) == 1
    s = summary(workdir)
    assert t.requests == [] and s["exit"] == "ERROR" and "does not belong" in s["error"]["error"]
