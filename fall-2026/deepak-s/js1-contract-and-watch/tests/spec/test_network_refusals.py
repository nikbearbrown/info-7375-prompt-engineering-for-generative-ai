"""Cases 7 and 8 (Watch). Written by Claude Code from tests/acceptance/ACCEPTANCE_CASES.md on 2026-10-29, before any implementation. All postings and responses are constructed; the opener is a fake."""
import json
from datetime import timedelta

import pytest

from conftest import BOARD_URL, FIXED_NOW, FakeOpener, board_body, job, run_args, run_cli


@pytest.mark.parametrize("token", ["acme/../x", "acme.evil.com", "ACME", ""])
def test_ac07_bad_board_token_is_refused_before_any_request(workdir, token):
    opener = FakeOpener({})
    assert run_cli(run_args(board=token), opener=opener) == 2
    assert opener.requests == []


def test_ac08_urls_in_posting_data_are_never_requested(workdir):
    other = "https://tracker.example.net/apply?id=401"
    posting = job(401, "AI Engineer", content=f"&lt;a href=&quot;{other}&quot;&gt;Apply&lt;/a&gt;")
    posting["absolute_url"] = other
    for minute, jobs in ((0, []), (1, [posting])):
        opener = FakeOpener({BOARD_URL: (200, board_body(jobs), {})})
        assert run_cli(run_args(), opener=opener, now=FIXED_NOW + timedelta(minutes=minute)) == 0
        assert opener.requests == [{"url": BOARD_URL, "method": "GET", "timeout": 20}]


@pytest.mark.parametrize("status", [301, 302, 304, 307, 308])
def test_ac08_redirect_is_refused_and_not_followed(workdir, status):
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (200, board_body([]), {})})) == 0
    state = workdir / "state" / "acme.json"
    before = state.read_bytes()

    elsewhere = "https://boards-api.greenhouse.io.evil.example.net/v1/boards/acme/jobs"
    opener = FakeOpener({BOARD_URL: (status, b"", {"Location": elsewhere})})
    assert run_cli(run_args(), opener=opener, now=FIXED_NOW + timedelta(minutes=1)) == 3

    assert [r["url"] for r in opener.requests] == [BOARD_URL]
    assert state.read_bytes() == before
    runs = sorted((workdir / "evidence" / "runs").iterdir())
    manifest = json.loads((runs[-1] / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["http_status"] == status
    assert manifest["location_header"] == elsewhere
