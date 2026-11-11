"""GATE.md §3 (the repeat rule) and §2 (budgets), plus W3 and W4."""

from __future__ import annotations

import pytest

from agent import cli as cli_mod
from agent import loop as loop_mod
from agent import report as report_mod
from agent.errors import RepeatedAction, TransientFailure
from agent.trace import Trace
from tests import wrong_versions as wrong
from tests.conftest import GREENHOUSE_OK, fetcher_from

GH_URL = "https://boards-api.greenhouse.io/v1/boards/reddit/jobs"
ONE = [{"board": "greenhouse:reddit", "provider": "greenhouse", "token": "reddit"}]


def test_the_same_action_twice_in_one_run_is_refused(project, policy):
    """W4. Two plan entries that resolve to one URL are one action written twice."""
    plan = ONE + [
        {"board": "greenhouse:reddit-again", "provider": "greenhouse", "token": "reddit"}
    ]
    trace = Trace(path=project / "evidence" / "runs" / "t.jsonl")
    budget = loop_mod.Budget(boards=6, requests=12, seconds=90, retries_per_board=2)
    with pytest.raises(RepeatedAction):
        loop_mod.run(
            plan, policy=policy, budget=budget,
            raw_dir=project / "evidence" / "raw", trace=trace,
            fetcher=fetcher_from({GH_URL: GREENHOUSE_OK}), sleep=lambda _s: None,
        )
    assert trace.final_outcome_per_board()["greenhouse:reddit-again"] == "policy"


def test_W4_lets_the_duplicate_through(project):
    """The wrong version issues it twice without complaint."""
    bad = wrong.NoRepeatPolicy(
        project_root=project, output_root=(project / "evidence").resolve()
    )
    bad.note_action("GET", GH_URL)
    bad.note_action("GET", GH_URL)  # no exception: that is the bug


def test_the_repeat_rule_is_per_run_not_forever(policy):
    policy.note_action("GET", GH_URL)
    with pytest.raises(RepeatedAction):
        policy.note_action("GET", GH_URL)
    policy.forget_actions()
    policy.note_action("GET", GH_URL)  # a new run may fetch it again


def test_two_urls_on_the_same_board_are_two_actions(policy):
    policy.note_action("GET", GH_URL)
    policy.note_action("GET", GH_URL + "?page=2")  # different action, allowed


def test_a_flapping_board_cannot_exceed_the_request_budget(project, policy):
    """W3. The real loop caps a permanently flapping board."""
    def flap():
        raise TransientFailure("timeout")

    budget = loop_mod.Budget(boards=6, requests=4, seconds=90, retries_per_board=2)
    trace = Trace(path=project / "evidence" / "runs" / "t.jsonl")
    plan = [
        {"board": f"greenhouse:b{i}", "provider": "greenhouse", "token": f"b{i}"}
        for i in range(4)
    ]
    urls = {f"https://boards-api.greenhouse.io/v1/boards/b{i}/jobs": flap for i in range(4)}
    result = loop_mod.run(
        plan, policy=policy, budget=budget, raw_dir=project / "evidence" / "raw",
        trace=trace, fetcher=fetcher_from({}, failures=urls), sleep=lambda _s: None,
    )
    assert result.trace.requests_used() <= budget.requests
    assert result.budget_hit == "requests"
    assert report_mod.exit_status(result)[0] == "budget_exhausted"


def test_W3_would_not_be_capped(project, policy):
    """The wrong version keeps retrying until its own arbitrary ceiling."""
    def flap(_policy, _url, **_kw):
        raise TransientFailure("timeout")

    attempts = wrong.flap_without_counting_requests(
        flap, policy, GH_URL, max_attempts=25
    )
    assert attempts == 25, "nothing in W3 is bounded by the request budget"


def test_the_seconds_budget_stops_the_loop(project, policy):
    ticks = iter([0.0, 0.0, 100.0, 100.0, 100.0, 100.0])
    budget = loop_mod.Budget(boards=6, requests=12, seconds=90, retries_per_board=2)
    trace = Trace(path=project / "evidence" / "runs" / "t.jsonl")
    plan = ONE + [{"board": "lever:spotify", "provider": "lever", "token": "spotify"}]
    result = loop_mod.run(
        plan, policy=policy, budget=budget, raw_dir=project / "evidence" / "raw",
        trace=trace, fetcher=fetcher_from({GH_URL: GREENHOUSE_OK}),
        sleep=lambda _s: None, clock=lambda: next(ticks),
    )
    assert result.budget_hit == "seconds"
    assert "lever:spotify" in result.skipped


def test_no_command_line_flag_can_raise_a_budget():
    """GATE.md §2: a limit any caller can raise is not a limit."""
    parser = cli_mod.build_parser()
    text = parser.format_help()
    for sub in ("watch",):
        assert sub in text
    all_flags = []
    for action in parser._subparsers._group_actions[0].choices["watch"]._actions:
        all_flags.extend(action.option_strings)
    for flag in all_flags:
        assert "max" not in flag, f"{flag} looks like it widens a budget"
        assert "budget" not in flag or flag == "--budget", flag
    assert "--budget" in all_flags, "the budget file is selectable; its contents are not"
