"""The finished wrong answer (GATE.md §6).

The failure this file is about is not a crash. A board answers HTTP 200 with a
valid, correctly-shaped, empty postings array. Every step of the loop succeeds:
the request was allowed and made, the schema parsed, zero postings were found,
so zero are new. `finished` is the *correct* status for what the loop knows, and
"no new postings" is a true statement about what it saw.

It is still the wrong answer, because the board has jobs and the token now
points at a retired board, or the provider renamed the array.

So these tests assert two things that sound contradictory and are not:

1. the loop **must** exit `finished` here — a loop that cried error on an empty
   board would be wrong about the 161 real postings it cannot distinguish from
   this case, and would teach me to ignore it;
2. something that is **not** the loop must catch it, from the saved bytes and a
   floor I wrote by hand, without consulting the loop's own account of the run.

If test 1 ever fails the loop started guessing. If test 2 ever fails the only
thing standing between this repository and a confident wrong answer is gone.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent import loop as loop_mod
from agent import report as report_mod
from agent import state as state_mod
from agent.trace import Trace
from tests.conftest import GREENHOUSE_EMPTY, GREENHOUSE_OK, fetcher_from, write_plan

ROOT = Path(__file__).resolve().parents[1]

BOARD = "greenhouse:constructed"
URL = "https://boards-api.greenhouse.io/v1/boards/constructed/jobs"
PLAN = [
    {
        "board": BOARD,
        "provider": "greenhouse",
        "token": "constructed",
        "expect_at_least": 1,
    }
]


def fresh_policy(project):
    """A new Policy per run, because a second run is a second process.

    GATE.md §3's repeat rule is scoped to one run, and `Policy` is where that
    scope lives. Reusing one Policy across two calls to `run_once` is not two
    runs, it is one run issuing the same GET twice — which the policy correctly
    refuses. (It refused it at me while this file was being written.)
    """
    from agent.policy import Policy

    return Policy(project_root=project, output_root=(project / "evidence").resolve())


#: Two runs in the same wall-clock second would name their saved response the
#: same thing, and overwriting a file under `raw/` needs `--approve-overwrite`
#: (GATE.md §5.3) — so the loop refuses, loudly, rather than replacing evidence.
#: That refusal is correct and is asserted by
#: `test_two_runs_in_one_second_refuse_rather_than_overwrite_evidence` below.
#: Here, where the point is two runs at two different times, the stamp is
#: advanced explicitly instead. A CONSTRUCTED arrangement, not a real clock.
_STAMPS = iter(f"202611{d:02d}T120000Z" for d in range(1, 29))


def at_the_next_minute(monkeypatch):
    monkeypatch.setattr(loop_mod, "utc_stamp", lambda: next(_STAMPS))


def run_once(project, policy, payload):
    """One loop run against a constructed payload, writing real evidence files."""
    trace = Trace(path=project / "evidence" / "runs" / f"trace-{loop_mod.utc_stamp()}.jsonl")
    result = loop_mod.run(
        PLAN,
        policy=policy,
        budget=loop_mod.Budget.from_file(project / "config" / "budget.json"),
        raw_dir=project / "evidence" / "raw",
        trace=trace,
        fetcher=fetcher_from({URL: payload}),
    )
    return result, trace


# --- 1. the loop is right to say it finished ----------------------------------

def test_an_empty_board_exits_finished_not_error(project, policy, persona):
    result, _ = run_once(project, policy, GREENHOUSE_EMPTY)
    report = report_mod.build(
        result,
        policy=policy,
        mode="constructed",
        label="CONSTRUCTED: HTTP 200 with an empty jobs array",
        new_entries=[],
        is_first_run=True,
        state_before_sha=None,
        state_after_sha=None,
        state_path=str(project / "evidence" / "state" / "seen.json"),
    )
    assert report["exit_status"] == "finished"
    assert report["complete"] is True
    outcome = result.outcomes[0]
    assert outcome.observed is True
    assert outcome.postings == []
    assert outcome.error is None, "an empty board is not an error and must not be dressed as one"


def test_the_finished_status_is_derived_from_a_trace_with_nothing_wrong_in_it(project, policy):
    """`finished` is not assigned; it is what the trace adds up to."""
    _, trace = run_once(project, policy, GREENHOUSE_EMPTY)
    records = [json.loads(line) for line in trace.path.read_text().splitlines() if line.strip()]
    assert records, "the run recorded nothing"
    assert [r["outcome"] for r in records] == ["ok"]
    assert [r["http_status"] for r in records] == [200]
    assert [r["postings"] for r in records] == [0]


def test_no_new_postings_is_reported_as_zero_and_not_as_a_warning(project, policy, persona):
    """The honest sentence that is the dangerous one."""
    result, _ = run_once(project, policy, GREENHOUSE_EMPTY)
    report = report_mod.build(
        result, policy=policy, mode="constructed", label=None, new_entries=[],
        is_first_run=False, state_before_sha=None, state_after_sha=None,
        state_path=str(project / "evidence" / "state" / "seen.json"),
    )
    summary = report_mod.human_summary(report)
    assert "ESCALATE" not in summary, (
        "the loop has nothing to escalate here, which is the whole problem"
    )
    assert report["new_postings"] == 0


# --- 2. something that is not the loop catches it -----------------------------

def crosscheck(project, *, boards_name="boards.json", state=None):
    """Run the real tools/crosscheck.py in-process and capture its exit code."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "crosscheck_under_test", ROOT / "tools" / "crosscheck.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    argv = [
        "--raw-dir", str(project / "evidence" / "raw"),
        "--boards", str(project / "config" / boards_name),
        "--state", str(state or project / "evidence" / "state" / "seen.json"),
    ]
    return module.main(argv)


def test_the_crosscheck_flags_the_empty_board_against_a_hand_written_floor(
    project, policy, capsys
):
    write_plan(project, PLAN)
    run_once(project, policy, GREENHOUSE_EMPTY)
    code = crosscheck(project)
    out = capsys.readouterr().out
    assert code == 1, "the cross-check must fail the run the loop called finished"
    assert "BELOW_FLOOR" in out


def test_the_crosscheck_also_notices_the_board_emptying_out(
    project, policy, capsys, monkeypatch
):
    """Two runs on disk: 3 postings, then 0. The drop is visible in the bytes."""
    at_the_next_minute(monkeypatch)
    write_plan(project, PLAN)
    run_once(project, policy, GREENHOUSE_OK)
    run_once(project, fresh_policy(project), GREENHOUSE_EMPTY)
    code = crosscheck(project)
    out = capsys.readouterr().out
    assert code == 1
    assert "SUSPECT_EMPTY" in out, "a board that had postings and now has none"
    assert "SUSPECT_DROP" in out


def test_the_crosscheck_reaches_its_verdict_with_no_run_report_on_disk(
    project, policy, capsys, monkeypatch
):
    """What 'independent' has to mean, asserted rather than claimed.

    The cross-check is only worth running if the agent's own account of the run
    cannot influence it. The strongest check available is to take that account
    away entirely: delete every run report and trace, leave only the saved
    responses and the hand-written floor, and require the same verdict.
    """
    at_the_next_minute(monkeypatch)
    write_plan(project, PLAN)
    run_once(project, policy, GREENHOUSE_OK)
    run_once(project, fresh_policy(project), GREENHOUSE_EMPTY)

    runs = project / "evidence" / "runs"
    removed = 0
    for path in list(runs.iterdir()):
        path.unlink()
        removed += 1
    assert removed >= 2, "there should have been reports and traces to remove"
    assert list(runs.iterdir()) == []

    code = crosscheck(project)
    out = capsys.readouterr().out
    assert code == 1
    assert "BELOW_FLOOR" in out
    assert "never the run report" in out


def test_a_board_above_its_floor_is_not_flagged(project, policy, capsys):
    """The flag has to be able to stay silent, or it means nothing when it fires."""
    write_plan(project, PLAN)
    run_once(project, policy, GREENHOUSE_OK)
    code = crosscheck(project)
    out = capsys.readouterr().out
    assert code == 0, out
    assert "nothing flagged" in out


# --- 3. what the state file does here, which surprised me ---------------------

def test_the_state_file_records_the_wrong_count_and_is_not_a_safe_baseline(
    project, policy, persona, monkeypatch
):
    """Found while running the demonstration, not while designing it.

    The second run writes `last_count: 0` over the first run's 163, because the
    state file records what was last observed and 0 *was* last observed. So the
    state file cannot be the cross-check's baseline: by the time anyone looks,
    the number that would have raised the alarm has been overwritten by the
    number that needs raising an alarm about.

    This is why `tools/crosscheck.py` compares the saved response bytes against
    each other and treats the state column as display only. Pinned here so that
    a future change which starts trusting `state.boards[*].last_count` fails.
    """
    at_the_next_minute(monkeypatch)
    state_path = project / "evidence" / "state" / "seen.json"

    result, _ = run_once(project, policy, GREENHOUSE_OK)
    state, _ = state_mod.load(state_path)
    postings = [p for o in result.outcomes for p in o.postings]
    state_mod.save(state_path, state, postings=postings, board_counts={BOARD: len(postings)})
    first = json.loads(state_path.read_text())["boards"][BOARD]["last_count"]
    assert first == 3

    result, _ = run_once(project, fresh_policy(project), GREENHOUSE_EMPTY)
    state, _ = state_mod.load(state_path)
    state_mod.save(state_path, state, postings=[], board_counts={BOARD: 0})
    second = json.loads(state_path.read_text())["boards"][BOARD]["last_count"]

    assert second == 0, "last_count follows the last observation, including a bad one"
    assert second < first, (
        "the count went backwards with no complaint from the loop — this is the "
        "reason the cross-check reads evidence/raw/ instead of the state file"
    )
    seen = json.loads(state_path.read_text())["seen_ids"]
    assert len(seen) == 3, (
        "seen_ids is monotonic, so the postings are not forgotten; it is the "
        "per-board count that regresses"
    )


def test_two_runs_in_one_second_refuse_rather_than_overwrite_evidence(project, policy):
    """A refusal I ran into while writing this file, kept because it is the
    behaviour I want.

    `agent.loop._save_raw` names a saved response `<utc-stamp>-<board>.json` to
    the second. Two runs inside one second therefore want the same filename, and
    GATE.md §5.3 makes replacing a file under `raw/` require
    `--approve-overwrite`. So the second run aborts with `NeedsApproval` and the
    first run's evidence is still on disk, unmodified.

    It is a real operational limitation — two legitimate back-to-back runs in the
    same second cannot both save — and it is written up in FRICTIONAL.md rather
    than fixed under deadline, because the failure direction is the safe one: it
    stops, it says why, and it never silently replaces a captured response. A
    sub-second suffix would be the fix; the test to write first is this one.
    """
    from agent.errors import NeedsApproval

    run_once(project, policy, GREENHOUSE_OK)
    saved = sorted((project / "evidence" / "raw").iterdir())
    assert len(saved) == 1
    before = saved[0].read_bytes()

    with pytest.raises(NeedsApproval):
        run_once(project, fresh_policy(project), GREENHOUSE_EMPTY)

    assert sorted((project / "evidence" / "raw").iterdir()) == saved
    assert saved[0].read_bytes() == before, "the captured response was modified"
