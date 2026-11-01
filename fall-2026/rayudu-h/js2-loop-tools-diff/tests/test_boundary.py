"""The 20 boundary cases in BOUNDARY-TESTS.md, numbered the same. Predictions were committed before this code.

No real network: request checks run before any socket is opened; redirect and repeat cases use fakes.
"""
import os
import urllib.request

import pytest

from conftest import ROOT, ashby_board
from jsagent import loop, net
from jsagent.policy import Policy, Refused

P = Policy(ROOT)


def allowed(fn, *args):
    fn(*args)
    return True


def refused(fn, *args):
    with pytest.raises(Refused):
        fn(*args)
    return True


def test_01_greenhouse_get_allowed():
    assert allowed(P.check_request, "GET", "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true")


def test_02_ashby_get_allowed():
    assert allowed(P.check_request, "GET", "https://api.ashbyhq.com/posting-api/job-board/notion")


def test_03_off_list_host_refused_before_any_request():
    assert refused(net.fetch, P, "https://api.lever.co/v0/postings/palantir", 5)


def test_04_plain_http_refused():
    assert refused(net.fetch, P, "http://boards-api.greenhouse.io/v1/boards/anthropic/jobs", 5)


def test_05_host_suffix_trick_refused():
    assert refused(net.fetch, P, "https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs", 5)


def test_06_post_refused():
    assert refused(P.check_request, "POST", "https://api.ashbyhq.com/posting-api/job-board/notion")


def test_07_redirect_to_off_list_host_refused_before_following(monkeypatch):
    """A fake opener redirects; the policy's redirect hook must refuse before the new URL is opened."""
    opened = []

    class FakeOpener:
        def __init__(self, handler):
            self.handler = handler

        def open(self, req, timeout):
            opened.append(req.full_url)
            self.handler().redirect_request(req, None, 302, "Found", {}, "https://evil.example/steal")
            raise AssertionError("redirect was followed")

    monkeypatch.setattr(urllib.request, "build_opener", lambda h: FakeOpener(h))
    assert refused(net.fetch, P, "https://api.ashbyhq.com/posting-api/job-board/notion", 5)
    assert opened == ["https://api.ashbyhq.com/posting-api/job-board/notion"]


def test_08_following_a_posting_link_refused():
    assert refused(net.fetch, P, "https://jobs.ashbyhq.com/notion/1fc309c8-da20-4ff2-84c7-8b863ece2b0a", 5)


def test_09_write_inside_runs_allowed():
    assert P.check_write("runs/2026-11-01T000000/report.md").is_relative_to(ROOT / "runs")


def test_10_write_inside_state_allowed():
    assert P.check_write("state/seen.json") == (ROOT / "state" / "seen.json").resolve()


def test_11_dotdot_escape_refused():
    assert refused(P.check_write, "runs/../../escape.txt")


def test_12_prefix_trick_refused():
    assert refused(P.check_write, "runs-evil/x.txt")


def test_13_symlink_escape_refused(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    link = ROOT / "runs" / "link-test-13"
    link.parent.mkdir(exist_ok=True)
    if link.is_symlink():
        link.unlink()
    os.symlink(outside, link)
    try:
        assert refused(P.check_write, "runs/link-test-13/x.txt")
    finally:
        link.unlink()


def test_14_absolute_path_outside_refused():
    assert refused(P.check_write, "/tmp/x.txt")


def test_15_read_persona_allowed():
    assert allowed(P.check_read, "persona/priya-nair.resume.json")


def test_16_write_to_read_only_persona_refused():
    assert refused(P.check_write, "persona/priya-nair.resume.json")


def test_17_read_outside_folder_refused():
    assert refused(P.check_read, "../js1-contract-and-watch/CONTRACT.md")


def test_18_reset_state_without_approval_refused():
    assert refused(P.check_reset_state, "state/seen.json")


def test_19_reset_state_with_approval_allowed():
    assert allowed(Policy(ROOT, {"reset-state"}).check_reset_state, "state/seen.json")


def test_20_same_get_twice_in_one_run_second_not_sent(tmp_path, resume):
    calls = []

    def fake_fetch(policy, url, timeout):
        calls.append(url)
        return ashby_board(("a1", "AI Engineer", "Python"))

    boards = [{"system": "ashby", "board": "notion"}, {"system": "ashby", "board": "notion"}]
    run_dir = ROOT / "runs" / "pytest-test-20"
    out = loop.run(boards, resume, Policy(ROOT), tmp_state(tmp_path), run_dir,
                   use_claude=False, fetch=fake_fetch, sleep=lambda s: None)
    try:
        assert calls == ["https://api.ashbyhq.com/posting-api/job-board/notion"]
        assert out["boards"][1]["status"] == "failed" and "repeat" in out["boards"][1]["reason"]
        assert any(e["event"] == "refused-repeat" for e in out["trace"])
    finally:
        _rm(run_dir)
        _rm(ROOT / "runs" / f"pytest-state-{tmp_path.name}")


def tmp_state(tmp_path):
    """Tests keep state under runs/ (a write root) so the real state/ is never touched."""
    d = ROOT / "runs" / f"pytest-state-{tmp_path.name}"
    d.mkdir(parents=True, exist_ok=True)
    return d / "seen.json"


def _rm(path):
    import shutil
    shutil.rmtree(path, ignore_errors=True)
