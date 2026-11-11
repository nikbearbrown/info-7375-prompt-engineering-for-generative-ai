"""GATE.md §1 — the four exits, and W1.

The property under test is not "the counts are right". W1's counts are all
right. It is "the status is derived from what was observed", which is the only
thing that makes `finished` mean anything.
"""

from __future__ import annotations

import pytest

from agent import loop as loop_mod
from agent import report as report_mod
from agent.errors import DisallowedHost
from agent.trace import Trace
from tests import wrong_versions as wrong
from tests.conftest import ASHBY_OK, GREENHOUSE_OK, LEVER_OK, fetcher_from

GH_URL = "https://boards-api.greenhouse.io/v1/boards/reddit/jobs"
LV_URL = "https://api.lever.co/v0/postings/spotify?mode=json"
AS_URL = "https://api.ashbyhq.com/posting-api/job-board/ramp"

PLAN_3 = [
    {"board": "greenhouse:reddit", "provider": "greenhouse", "token": "reddit"},
    {"board": "lever:spotify", "provider": "lever", "token": "spotify"},
    {"board": "ashby:ramp", "provider": "ashby", "token": "ramp"},
]

ALL_OK = {GH_URL: GREENHOUSE_OK, LV_URL: LEVER_OK, AS_URL: ASHBY_OK}


def do_run(project, policy, plan, mapping, *, budget=None, failures=None):
    budget = budget or loop_mod.Budget(boards=6, requests=12, seconds=90, retries_per_board=2)
    trace = Trace(path=project / "evidence" / "runs" / "trace.jsonl")
    return loop_mod.run(
        plan,
        policy=policy,
        budget=budget,
        raw_dir=project / "evidence" / "raw",
        trace=trace,
        fetcher=fetcher_from(mapping, failures=failures),
        sleep=lambda _s: None,
    )


def test_three_boards_across_three_systems_exit_finished(project, policy):
    result = do_run(project, policy, PLAN_3, ALL_OK)
    status, complete = report_mod.exit_status(result)
    assert (status, complete) == ("finished", True)
    assert {o.provider for o in result.outcomes} == {"greenhouse", "lever", "ashby"}
    assert all(o.observed for o in result.outcomes)


def test_a_failed_board_makes_the_run_incomplete(project, policy):
    plan = PLAN_3 + [
        {"board": "greenhouse:nope", "provider": "greenhouse", "token": "nope",
         "deliberate_failure": True}
    ]
    result = do_run(project, policy, plan, ALL_OK)
    status, complete = report_mod.exit_status(result)
    assert (status, complete) == ("incomplete", False)


def test_a_failed_board_never_appears_as_zero_new(project, policy, persona):
    """W1. The failed board must have no count at all, not a count of 0."""
    plan = PLAN_3 + [
        {"board": "greenhouse:nope", "provider": "greenhouse", "token": "nope"}
    ]
    result = do_run(project, policy, plan, ALL_OK)
    report = report_mod.build(
        result, policy=policy, mode="constructed", label=None, new_entries=[],
        is_first_run=False, state_before_sha=None, state_after_sha=None,
        state_path=project / "evidence" / "state" / "seen.json",
    )
    failed = [r for r in report["boards"] if r["status"] != "ok"]
    assert failed, "the constructed plan must contain a failing board"
    for row in failed:
        assert row["postings_seen"] is None, "a failed board must have no count"
        assert row["error_class"]
    assert report["exit_status"] == "incomplete"
    assert report["complete"] is False


def test_the_same_check_catches_W1(project, policy, persona):
    result = do_run(
        project, policy,
        PLAN_3 + [{"board": "greenhouse:nope", "provider": "greenhouse", "token": "nope"}],
        ALL_OK,
    )
    bad = wrong.report_failure_as_zero(result, policy=policy, resume=persona)
    # W1's counts are all defensible; what it gets wrong is the claim.
    assert bad["exit_status"] == "finished"
    assert bad["complete"] is True
    assert [r["postings_seen"] for r in bad["boards"] if r["status"] != "ok"] == [0]
    # and the real derivation disagrees with it, which is the point
    assert report_mod.exit_status(result)[0] == "incomplete"


def test_exit_status_is_derived_not_asserted(project, policy):
    """There is no code path that sets `finished` directly.

    Checked structurally: `exit_status` is the only place the string appears in
    agent/report.py outside the STATUSES tuple and the human summary.
    """
    from pathlib import Path

    src = Path(report_mod.__file__).read_text(encoding="utf-8")
    assignments = [
        line for line in src.splitlines()
        if '"finished"' in line and "return" not in line and "STATUSES" not in line
        and "exit_status" not in line
    ]
    assert assignments == [], f"'finished' is assigned outside the derivation: {assignments}"


def test_budget_exhausted_on_boards(project, policy):
    budget = loop_mod.Budget(boards=2, requests=12, seconds=90, retries_per_board=2)
    result = do_run(project, policy, PLAN_3, ALL_OK, budget=budget)
    status, complete = report_mod.exit_status(result)
    assert (status, complete) == ("budget_exhausted", False)
    assert result.budget_hit == "boards"
    assert result.skipped == ["ashby:ramp"]


def test_budget_exhausted_on_requests(project, policy):
    budget = loop_mod.Budget(boards=6, requests=2, seconds=90, retries_per_board=2)
    result = do_run(project, policy, PLAN_3, ALL_OK, budget=budget)
    status, _ = report_mod.exit_status(result)
    assert status == "budget_exhausted"
    assert result.budget_hit == "requests"
    assert result.trace.requests_used() <= 2


def test_a_policy_refusal_aborts_the_run_with_error(project, policy):
    """A refusal is a bug in the plan, not a fault in the world."""

    def rogue(policy_, url, *, timeout=20.0):
        # a plan or code bug: the loop tries a host nobody allow-listed
        return policy_.check_request("GET", "https://evil.example/jobs")

    trace = Trace(path=project / "evidence" / "runs" / "trace.jsonl")
    budget = loop_mod.Budget(boards=6, requests=12, seconds=90, retries_per_board=2)
    with pytest.raises(DisallowedHost):
        loop_mod.run(
            PLAN_3, policy=policy, budget=budget,
            raw_dir=project / "evidence" / "raw", trace=trace, fetcher=rogue,
            sleep=lambda _s: None,
        )
    assert trace.final_outcome_per_board()["greenhouse:reddit"] == "policy"
    # and were the trace handed to the derivation, it would say `error`
    class _R:
        outcomes, planned, budget_hit, skipped = [], 3, None, []
        seconds_used, started_at = 0.0, ""
    _R.trace = trace
    assert report_mod.exit_status(_R)[0] == "error"


def test_the_escalate_line_appears_whenever_the_run_is_not_finished(project, policy):
    result = do_run(
        project, policy,
        PLAN_3 + [{"board": "greenhouse:nope", "provider": "greenhouse", "token": "nope"}],
        ALL_OK,
    )
    report = report_mod.build(
        result, policy=policy, mode="constructed", label=None, new_entries=[],
        is_first_run=False, state_before_sha=None, state_after_sha=None,
        state_path="x",
    )
    summary = report_mod.human_summary(report)
    assert "ESCALATE:" in summary
    assert "NOT complete" in summary
