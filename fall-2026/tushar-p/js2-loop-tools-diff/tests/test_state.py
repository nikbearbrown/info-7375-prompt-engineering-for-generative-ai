"""Seen-ID state across runs (GATE "Loop, budgets, and exits"; F4, F5, F17; Wrong versions)."""

import json

import pytest

from agent.providers import Board
from support import (NOTION, RUN_ID, STRIPE, board_entry, ok, read_summary, run_agent, status,
                     timeout)

OTHER = Board("greenhouse", "other-co")


def saved_state(out):
    return json.loads((out / "state.json").read_text())


def test_same_id_on_two_boards_is_isolated(tmp_path):
    """Wrong versions: "Two boards share the same ID" -> each board keeps its own seen IDs."""
    state = {"greenhouse/stripe": [100], "greenhouse/other-co": [200]}
    result, _, out = run_agent(tmp_path, [STRIPE, OTHER],
                               {STRIPE: [ok(STRIPE, [100, 200])], OTHER: [ok(OTHER, [100, 200])]},
                               state=state)
    assert result.exit == "finished"
    summary = read_summary(out)
    assert board_entry(summary, STRIPE)["new_ids"] == [200]
    assert board_entry(summary, OTHER)["new_ids"] == [100]
    assert saved_state(out) == {"greenhouse/other-co": [100, 200], "greenhouse/stripe": [100, 200]}


@pytest.mark.parametrize("failure", [
    [status(STRIPE, 404)],
    [status(STRIPE, 200, b"")],
    [status(STRIPE, 200, b'{"jobs": [{"id": true}]}')],
    [timeout(), timeout()],
], ids=["404", "empty-body", "malformed", "timeout-twice"])
def test_failed_fetch_leaves_board_state_alone(tmp_path, failure):
    """Wrong versions: "a failed fetch clears the board's state" -> a failed fetch leaves its state alone."""
    state = {"greenhouse/stripe": [1, 2], "ashby/notion": ["a"]}
    result, _, out = run_agent(tmp_path, [STRIPE, NOTION],
                               {STRIPE: failure, NOTION: [ok(NOTION, ["a", "b"])]}, state=state)
    assert result.exit == "incomplete"
    assert saved_state(out) == {"ashby/notion": ["a", "b"], "greenhouse/stripe": [1, 2]}


def test_baseline_reports_zero_new(tmp_path):
    """GATE + F4: on a board's first successful fetch, stage a baseline and report zero new IDs."""
    result, _, out = run_agent(tmp_path, [STRIPE], {STRIPE: [ok(STRIPE, [3, 1, 2])]})
    assert result.exit == "finished"
    entry = board_entry(read_summary(out), STRIPE)
    assert entry["baseline"] is True
    assert entry["fetched"] == 3 and entry["new"] == 0 and entry["new_ids"] == []
    assert saved_state(out) == {"greenhouse/stripe": [1, 2, 3]}


def test_board_without_entry_is_baseline_while_others_diff(tmp_path):
    """F4: a board with no state entry reports zero new IDs, even when other boards have state."""
    state = {"greenhouse/stripe": [1]}
    _, _, out = run_agent(tmp_path, [STRIPE, NOTION],
                          {STRIPE: [ok(STRIPE, [1, 2])], NOTION: [ok(NOTION, ["x", "y"])]}, state=state)
    summary = read_summary(out)
    assert board_entry(summary, STRIPE)["new_ids"] == [2] and board_entry(summary, STRIPE)["baseline"] is False
    assert board_entry(summary, NOTION)["new"] == 0 and board_entry(summary, NOTION)["baseline"] is True


def test_new_ids_use_unique_ids_and_report_duplicates(tmp_path):
    """F3 + GATE: fetched and new counts are separate, over unique IDs; duplicates are logged."""
    state = {"greenhouse/stripe": [1, 2]}
    _, _, out = run_agent(tmp_path, [STRIPE], {STRIPE: [ok(STRIPE, [1, 2, 3, 3])]}, state=state)
    entry = board_entry(read_summary(out), STRIPE)
    assert entry["fetched"] == 3 and entry["new"] == 1 and entry["new_ids"] == [3]
    assert entry["jobs_in_response"] == 4 and entry["duplicates_removed"] == 1


def test_state_ids_are_typed_per_provider(tmp_path):
    """GATE: keep Greenhouse IDs as integers and Ashby IDs as strings, keyed by provider and token."""
    _, _, out = run_agent(tmp_path, [STRIPE, NOTION],
                          {STRIPE: [ok(STRIPE, [7])], NOTION: [ok(NOTION, ["7"])]})
    assert saved_state(out) == {"ashby/notion": ["7"], "greenhouse/stripe": [7]}


def test_pre_run_snapshot_is_null_without_state(tmp_path):
    """F17: write pre-run-state.json from the loaded state; JSON null if there was no state file."""
    _, _, out = run_agent(tmp_path, [STRIPE], {STRIPE: [ok(STRIPE, [1])]})
    snapshot = out / "runs" / RUN_ID / "pre-run-state.json"
    assert json.loads(snapshot.read_bytes()) is None
    assert read_summary(out)["state"]["pre_run_snapshot"] == f"runs/{RUN_ID}/pre-run-state.json"


def test_pre_run_snapshot_holds_the_loaded_state(tmp_path):
    """F17: the snapshot is written before staging, from the state that was loaded."""
    original = b'{"greenhouse/stripe": [1, 2]}'
    _, _, out = run_agent(tmp_path, [STRIPE], {STRIPE: [ok(STRIPE, [1, 2, 3])]}, state=original)
    assert (out / "runs" / RUN_ID / "pre-run-state.json").read_bytes() == original
    assert saved_state(out) == {"greenhouse/stripe": [1, 2, 3]}  # the update went to state.json only


def test_no_state_write_on_error(tmp_path):
    """F5: on `error`, leave the existing state file alone (here: evidence can't be saved mid-run)."""
    original = b'{"greenhouse/stripe": [1]}'
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    def block_raw_dir_then_answer():
        raw_ashby = tmp_path / "out" / "runs" / RUN_ID / "raw" / "ashby"
        raw_ashby.symlink_to(elsewhere, target_is_directory=True)  # the gate refuses symlinks
        return ok(NOTION, ["a"])

    result, _, out = run_agent(tmp_path, [STRIPE, NOTION],
                               {STRIPE: [ok(STRIPE, [1, 2])], NOTION: [block_raw_dir_then_answer]},
                               state=original)
    assert result.exit == "error" and result.code == 2
    assert (out / "state.json").read_bytes() == original
    summary = read_summary(out)
    assert summary["error"]["stage"] == "evidence"
    assert summary["state"]["written"] is False
    assert list(elsewhere.iterdir()) == []


@pytest.mark.parametrize("bad", [b"{not json", b"[1, 2]", b'{"greenhouse/stripe": [true]}',
                                 b'{"ashby/notion": [""]}', b'{"lever/x": [1]}', b'{"greenhouse/stripe": "1"}'])
def test_unusable_state_is_error_before_transport(tmp_path, bad):
    """GATE exits: `error` when the state is unusable; no transport call, state left alone."""
    result, spy, out = run_agent(tmp_path, [STRIPE], {STRIPE: [ok(STRIPE, [1])]}, state=bad)
    assert result.exit == "error"
    assert spy.calls == []
    assert (out / "state.json").read_bytes() == bad
    assert read_summary(out)["error"]["stage"] == "state"
