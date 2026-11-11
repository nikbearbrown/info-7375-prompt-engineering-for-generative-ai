"""GATE.md §4 — classify first, then act. And never invent a value."""

from __future__ import annotations

import pytest

from agent import loop as loop_mod
from agent import report as report_mod
from agent.errors import PermanentFailure, SchemaFailure, TransientFailure
from agent.trace import Trace
from tests.conftest import GREENHOUSE_OK, fetcher_from

GH_URL = "https://boards-api.greenhouse.io/v1/boards/reddit/jobs"
ONE = [{"board": "greenhouse:reddit", "provider": "greenhouse", "token": "reddit"}]


def run_one(project, policy, *, failures=None, mapping=None, budget=None):
    budget = budget or loop_mod.Budget(boards=6, requests=12, seconds=90, retries_per_board=2)
    slept = []
    trace = Trace(path=project / "evidence" / "runs" / "t.jsonl")
    result = loop_mod.run(
        ONE, policy=policy, budget=budget,
        raw_dir=project / "evidence" / "raw", trace=trace,
        fetcher=fetcher_from(mapping if mapping is not None else {GH_URL: GREENHOUSE_OK},
                             failures=failures),
        sleep=slept.append,
    )
    return result, slept


def always(exc_factory):
    def raise_it():
        raise exc_factory()
    return {GH_URL: raise_it}


def test_transient_is_retried_exactly_twice_with_backoff(project, policy):
    result, slept = run_one(
        project, policy, failures=always(lambda: TransientFailure("timeout"))
    )
    outcome = result.outcomes[0]
    assert outcome.status == "transient"
    assert outcome.attempts == 3, "first attempt plus two retries"
    assert slept == [1.0, 3.0], "backoff 1s then 3s, in that order"
    retried = [o.retry_scheduled for o in result.trace.observations]
    assert retried == [True, True, False]


def test_permanent_is_not_retried(project, policy):
    result, slept = run_one(
        project, policy, failures=always(lambda: PermanentFailure("HTTP 404"))
    )
    assert result.outcomes[0].status == "permanent"
    assert result.outcomes[0].attempts == 1, "retrying a board that does not exist cannot succeed"
    assert slept == []


def test_schema_is_not_retried_and_is_not_read_as_no_jobs(project, policy):
    """The class that must never be silently read as an empty board."""
    result, slept = run_one(
        project, policy, failures=always(lambda: SchemaFailure("no jobs array"))
    )
    outcome = result.outcomes[0]
    assert outcome.status == "schema"
    assert outcome.attempts == 1
    assert slept == []
    assert outcome.postings == [], "no postings"
    report = report_mod.build(
        result, policy=policy, mode="constructed", label=None, new_entries=[],
        is_first_run=False, state_before_sha=None, state_after_sha=None, state_path="x",
    )
    row = report["boards"][0]
    assert row["postings_seen"] is None, "a schema failure has no count, not a count of zero"
    assert report["exit_status"] == "incomplete"


def test_a_failed_board_is_never_written_to_the_state_baseline(project, policy):
    """The cross-check's baseline would be destroyed by a 0 written for a failure."""
    from agent import state as state_mod

    result, _ = run_one(
        project, policy, failures=always(lambda: PermanentFailure("HTTP 404"))
    )
    observed = [o for o in result.outcomes if o.observed]
    assert observed == []
    board_counts = {o.board: len(o.postings) for o in observed}
    assert board_counts == {}, "nothing to record; a failure contributes no count"
    path = project / "evidence" / "state" / "seen.json"
    state, _first = state_mod.load(path)
    state = state_mod.save(path, state, postings=[], board_counts=board_counts)
    assert state["boards"] == {}


def test_a_deliberate_failure_is_labelled_as_such_in_the_report(project, policy):
    budget = loop_mod.Budget(boards=6, requests=12, seconds=90, retries_per_board=2)
    trace = Trace(path=project / "evidence" / "runs" / "t2.jsonl")
    plan = [
        {"board": "greenhouse:reddit", "provider": "greenhouse", "token": "reddit"},
        {"board": "greenhouse:nope", "provider": "greenhouse", "token": "nope",
         "deliberate_failure": True},
    ]
    result = loop_mod.run(
        plan, policy=policy, budget=budget, raw_dir=project / "evidence" / "raw",
        trace=trace, fetcher=fetcher_from({GH_URL: GREENHOUSE_OK}), sleep=lambda _s: None,
    )
    report = report_mod.build(
        result, policy=policy, mode="constructed", label=None, new_entries=[],
        is_first_run=False, state_before_sha=None, state_after_sha=None, state_path="x",
    )
    rows = {r["board"]: r for r in report["boards"]}
    assert rows["greenhouse:nope"]["deliberate_failure"] is True
    assert rows["greenhouse:nope"]["status"] == "permanent"
    assert rows["greenhouse:reddit"]["postings_seen"] == 3
    assert "DELIBERATE" in report_mod.human_summary(report)


def test_classification_comes_from_the_exception_class_not_a_message(project, policy):
    """No code decides what to do by reading an error string."""
    from pathlib import Path

    src = Path(loop_mod.__file__).read_text(encoding="utf-8")
    assert "str(exc)" in src, "the message is recorded…"
    assert ".classification" in src, "…but the decision uses the class"
    for forbidden in ('in str(exc)', 'exc.args[0] =='):
        assert forbidden not in src, f"loop.py inspects the message: {forbidden}"
