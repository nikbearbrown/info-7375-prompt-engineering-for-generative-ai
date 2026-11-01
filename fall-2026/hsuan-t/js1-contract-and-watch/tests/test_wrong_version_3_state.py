"""CONTRACT Wrong version 3 — state not saved, or not read.

A first run looks normal either way; the bug only shows on the second run, when old postings come
back as "new". So every test here runs at least twice, and also covers the two ways state can go
wrong quietly: a broken file treated as empty, and state saved even though judging never finished.
"""

import json
from pathlib import Path

import pytest
from fakes import FakeFetcher, START, board, by_id, job, run_once

from job_agent.common.errors import WatchError
from job_agent.judges import rule
from job_agent.pipeline import run


def test_second_run_reports_only_the_3_new_of_5(paths):
    first = run_once(paths, board(*(job(i) for i in [1, 2, 3, 4, 5])), n=0)
    second = run_once(paths, board(*(job(i) for i in [4, 5, 6, 7, 8])), n=1)   # 4, 5 repeat

    assert first["baseline"] is True and first["verdicts"] == []               # R13: baseline = 0
    assert sorted(by_id(second)) == [6, 7, 8]
    seen = json.loads(paths.state("stripe").read_text())["seen_ids"]
    assert seen == [1, 2, 3, 4, 5, 6, 7, 8]                                    # union, not replace


def test_run_with_nothing_new_reports_zero(paths):
    run_once(paths, board(job(1), job(2)), n=0)
    assert run_once(paths, board(job(1), job(2)), n=1)["verdicts"] == []


def test_posting_that_drops_off_and_returns_is_not_new_again(paths):
    run_once(paths, board(job(1), job(2)), n=0)
    run_once(paths, board(job(1)), n=1)                     # 2 disappears for a run
    assert run_once(paths, board(job(1), job(2)), n=2)["verdicts"] == []


@pytest.mark.parametrize("broken", [
    "not json {",
    '{"board": "stripe", "seen_ids": [1]}',                                   # missing last_run_at
    '{"board": "stripe", "seen_ids": ["1"], "last_run_at": "x"}',             # ids not integers
    '{"board": "airbnb", "seen_ids": [1], "last_run_at": "x"}',               # another board's file
])
def test_broken_state_stops_before_fetching(paths, broken):
    state = paths.state("stripe")
    state.parent.mkdir(parents=True)
    state.write_text(broken)
    fetcher = FakeFetcher(board(job(1)))
    with pytest.raises(WatchError):
        run("stripe", paths.default_resume, paths.default_profile, paths, now=START, fetcher=fetcher)
    assert fetcher.urls == []                       # stopped before any request
    assert state.read_text() == broken              # not silently replaced by a fresh baseline


def test_state_is_not_saved_when_judging_crashes(paths, monkeypatch):
    run_once(paths, board(job(1)), n=0)
    before = paths.state("stripe").read_text()

    def crash(*_):
        raise RuntimeError("judge crashed")
    monkeypatch.setattr(rule, "judge", crash)
    with pytest.raises(RuntimeError):
        run_once(paths, board(job(1), job(2)), n=1)
    # 2 must still count as new next time, because it was never judged.
    assert paths.state("stripe").read_text() == before


def test_junk_board_response_does_not_touch_state(paths):
    run_once(paths, board(job(1)), n=0)
    before = paths.state("stripe").read_text()
    for n, body in enumerate([b"<html>502 Bad Gateway</html>", b'{"no_jobs": []}'], start=1):
        with pytest.raises(WatchError):
            run_once(paths, body, n=n)
    assert paths.state("stripe").read_text() == before


def test_live_run_saves_the_raw_response_byte_for_byte(paths):
    body = board(job(1), job(2))
    doc = run_once(paths, body, n=0)
    # tmp_path is outside the repo, so raw_response is an absolute path here.
    assert Path(doc["raw_response"]).read_bytes() == body                      # R10
