"""GATE A2: a board below its written floor is a failed board (review-packet test).

Written and committed before the patch, from the finished-wrong-answer runs
``2026-11-09T08-16-13Z`` and ``2026-11-09T08-16-16Z`` (``greenhouse/ramp``: one stale
posting, reported FINISHED). Every response here is CONSTRUCTED.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from job_search_agent.models import RunStatus
from job_search_agent.watch import BoardState, LoopExit, WatchPlan
from tests.watch.harness import (
    ASHBY,
    GH,
    UUID,
    Project,
    ashby_body,
    gh_body,
    ok,
)

LINEAR_IDS = [f"00000000-0000-4000-8000-{i:012d}" for i in range(6)]


def _plan(*boards: dict[str, Any]) -> WatchPlan:
    return WatchPlan.model_validate(
        {
            "budget": {"max_boards": 6, "max_requests": 10, "max_seconds": 180},
            "retry": {"max_retries": 1, "pause_s": 2.0, "min_seconds_left": 5.0},
            "policy": {
                "allowed_hosts": ["boards-api.greenhouse.io", "api.ashbyhq.com"],
                "write_root": "data/watch",
            },
            "boards": list(boards),
        }
    )


RAMP_ON_GREENHOUSE = {"provider": "greenhouse", "token": "ramp", "min_postings": 20}
LINEAR = {"provider": "ashby", "token": "linear", "min_postings": 5}


def test_stale_board_below_its_floor_is_failed_not_finished(p: Project) -> None:
    report = p.run(
        _plan(RAMP_ON_GREENHOUSE, LINEAR),
        {
            GH.format("ramp"): ok(gh_body(8042562003)),
            ASHBY.format("linear"): ok(ashby_body(*LINEAR_IDS)),
        },
    )
    ramp, linear = report.boards
    assert ramp.state is BoardState.FAILED
    assert ramp.run_status is RunStatus.INVALID_RESPONSE
    assert ramp.note == "below_floor"
    assert linear.state is BoardState.OK
    assert report.exit is LoopExit.INCOMPLETE
    assert not p.state("greenhouse-ramp").exists()
    assert "below_floor" in (p.loop_dir(report) / "report.md").read_text()


def test_shrunken_board_keeps_its_saved_state(p: Project) -> None:
    plan = _plan(RAMP_ON_GREENHOUSE, LINEAR)
    linear = ASHBY.format("linear")
    p.run(
        plan,
        {
            GH.format("ramp"): ok(gh_body(*range(1, 31))),
            linear: ok(ashby_body(*LINEAR_IDS)),
        },
    )
    before = p.state("greenhouse-ramp").read_bytes()
    second = p.run(
        plan,
        {GH.format("ramp"): ok(gh_body(1, 2)), linear: ok(ashby_body(*LINEAR_IDS))},
    )
    assert second.boards[0].note == "below_floor"
    assert p.state("greenhouse-ramp").read_bytes() == before


def test_board_exactly_at_its_floor_is_ok(p: Project) -> None:
    report = p.run(
        _plan(LINEAR), {ASHBY.format("linear"): ok(ashby_body(*LINEAR_IDS[:5]))}
    )
    assert report.exit is LoopExit.FINISHED


def test_board_without_a_floor_has_no_floor(p: Project) -> None:
    board = {"provider": "ashby", "token": "ramp"}
    report = p.run(_plan(board), {ASHBY.format("ramp"): ok(ashby_body(UUID))})
    assert report.exit is LoopExit.FINISHED


def test_empty_board_with_a_floor_stays_empty_response(p: Project) -> None:
    body = json.dumps({"jobs": [], "meta": {"total": 0}}).encode()
    report = p.run(
        _plan(RAMP_ON_GREENHOUSE, LINEAR),
        {
            GH.format("ramp"): ok(body),
            ASHBY.format("linear"): ok(ashby_body(*LINEAR_IDS)),
        },
    )
    assert report.boards[0].run_status is RunStatus.EMPTY_RESPONSE


@pytest.mark.parametrize("floor", [0, -1])
def test_floor_must_be_positive(floor: int) -> None:
    with pytest.raises(ValidationError):
        _plan({"provider": "ashby", "token": "ramp", "min_postings": floor})


def test_pending_retry_from_an_old_raw_below_the_floor(p: Project) -> None:
    url = ASHBY.format("linear")
    plan_no_floor = _plan({"provider": "ashby", "token": "linear"})
    plan_with_floor = _plan(LINEAR)

    p.run(plan_no_floor, {url: ok(ashby_body(*LINEAR_IDS[:3]))})

    p.run(plan_no_floor, {url: ok(ashby_body(*LINEAR_IDS[:4]))})

    five_ids = [
        LINEAR_IDS[0],
        LINEAR_IDS[1],
        LINEAR_IDS[2],
        LINEAR_IDS[4],
        LINEAR_IDS[5],
    ]
    report3 = p.run(plan_with_floor, {url: ok(ashby_body(*five_ids))})

    board = report3.boards[0]
    assert board.state is BoardState.OK
    assert board.note != "below_floor"

    events_path = p.root / board.run_folder / "events.jsonl"
    events = [json.loads(line) for line in events_path.read_text().splitlines()]
    retry_event = next(e for e in events if e.get("event") == "pending.retry")
    assert retry_event["posting_from"] == "saved_raw"
