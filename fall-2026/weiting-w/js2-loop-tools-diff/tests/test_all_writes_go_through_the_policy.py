"""GATE.md §5's central sentence, tested instead of trusted.

> "Every network call and every file write in the package goes through it;
>  there is no second path."

Written on 2026-11-09 while generating `reports/boundary-tests.md`, because
writing that sentence down next to the table made me want to check it rather
than quote it. It was **false**: saved responses went through
`Policy.check_write`, but the run report and the trace did not. Both are files
the agent creates, so both were a second path.

The 19 boundary cases in GATE.md §5.5 could not have caught this. They test
whether the policy *decides* correctly, and it does. This is the different
question of whether every caller *asks* — and the first evidence of it was
accidental: a run pointed at a scratch directory outside the project refused to
save its response and then wrote its trace there anyway.

These tests are not among the 19 predicted cases. They were written after the
freeze, they are labelled as such here, and the gate's §8 records it.
"""

from __future__ import annotations

import pytest

from agent import loop as loop_mod
from agent import report as report_mod
from agent.errors import PathEscapes
from agent.trace import Trace
from tests.conftest import GREENHOUSE_OK, fetcher_from

URL = "https://boards-api.greenhouse.io/v1/boards/constructed/jobs"
PLAN = [{"board": "greenhouse:constructed", "provider": "greenhouse", "token": "constructed"}]


def test_a_trace_outside_the_output_root_is_refused(project, policy):
    """The accident that started this, as a test."""
    outside = project.parent / "trace-escaped.jsonl"
    trace = Trace(path=outside, policy=policy)
    with pytest.raises(PathEscapes):
        loop_mod.run(
            PLAN,
            policy=policy,
            budget=loop_mod.Budget.from_file(project / "config" / "budget.json"),
            raw_dir=project / "evidence" / "raw",
            trace=trace,
            fetcher=fetcher_from({URL: GREENHOUSE_OK}),
        )
    assert not outside.exists(), "the trace was written outside evidence/"


def test_a_run_report_outside_the_output_root_is_refused(project, policy):
    outside = project.parent / "runs-escaped"
    trace = Trace(path=project / "evidence" / "runs" / "t.jsonl", policy=policy)
    result = loop_mod.run(
        PLAN,
        policy=policy,
        budget=loop_mod.Budget.from_file(project / "config" / "budget.json"),
        raw_dir=project / "evidence" / "raw",
        trace=trace,
        fetcher=fetcher_from({URL: GREENHOUSE_OK}),
    )
    report = report_mod.build(
        result, policy=policy, mode="constructed", label=None, new_entries=[],
        is_first_run=True, state_before_sha=None, state_after_sha=None,
        state_path=str(project / "evidence" / "state" / "seen.json"),
    )
    with pytest.raises(PathEscapes):
        report_mod.write(report, outside, policy=policy)
    assert not outside.exists()


def test_the_normal_locations_still_work(project, policy):
    """The confinement must not have been bought by breaking the default paths."""
    trace = Trace(path=project / "evidence" / "runs" / "t.jsonl", policy=policy)
    result = loop_mod.run(
        PLAN,
        policy=policy,
        budget=loop_mod.Budget.from_file(project / "config" / "budget.json"),
        raw_dir=project / "evidence" / "raw",
        trace=trace,
        fetcher=fetcher_from({URL: GREENHOUSE_OK}),
    )
    report = report_mod.build(
        result, policy=policy, mode="constructed", label=None, new_entries=[],
        is_first_run=True, state_before_sha=None, state_after_sha=None,
        state_path=str(project / "evidence" / "state" / "seen.json"),
    )
    out = report_mod.write(report, project / "evidence" / "runs", policy=policy)
    assert out.exists()
    assert trace.path.exists()


def test_every_write_in_the_package_is_reachable_from_a_policy_check():
    """A reading of the source, not of behaviour.

    Any call that puts bytes on disk should sit next to a `check_write`. This
    counts the write primitives in `agent/` and requires each module that has
    one to also mention `check_write`, so a new unchecked writer added later
    shows up here rather than in a sign-off six weeks from now.
    """
    import re
    from pathlib import Path

    pkg = Path(__file__).resolve().parents[1] / "agent"
    writers = re.compile(r"\.write_text\(|\.write_bytes\(|\.open\(\s*[\"']a|\.open\(\s*[\"']w")
    offenders = []
    for path in sorted(pkg.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        if writers.search(source) and "check_write" not in source:
            offenders.append(path.name)
    assert offenders == [], (
        f"these modules write to disk without mentioning check_write: {offenders}"
    )
