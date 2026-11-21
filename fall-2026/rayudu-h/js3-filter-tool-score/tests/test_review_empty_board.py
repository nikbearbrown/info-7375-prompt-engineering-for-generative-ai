"""Review packet: the test written BEFORE the patch (GATE.md, error policy last row; wrong version 1).

Defect, reproduced in runs/2026-10-31T191312-seeded-wrong-answer/: an empty board, after a run
that had postings, was reported "ok, 0 new" and the run exited "finished". It also overwrote
the board's last good count with 0.

Required behavior (GATE.md): the board is "unverified"; it never reports "0 new"; its state is
not updated; the run exits "incomplete". All responses here are CONSTRUCTED.
"""
import shutil

import pytest

from conftest import ROOT, ashby_board
from jsagent import loop
from jsagent.policy import Policy

NO = {"system": "ashby", "board": "notion"}
EMPTY = b'{"apiVersion": "1", "jobs": []}'


@pytest.fixture
def where(tmp_path):
    run_dir = ROOT / "runs" / f"pytest-{tmp_path.name}"
    state = ROOT / "runs" / f"pytest-state-{tmp_path.name}" / "seen.json"
    yield run_dir, state
    for d in (ROOT / "runs").glob(f"pytest-*{tmp_path.name}*"):
        shutil.rmtree(d, ignore_errors=True)


def run(where, resume, body, suffix):
    run_dir, state = where
    return loop.run([NO], resume, Policy(ROOT), state, run_dir.with_name(run_dir.name + suffix),
                    use_claude=False, fetch=lambda p, u, t: body, sleep=lambda s: None)


def test_empty_board_after_postings_is_unverified_not_zero_new(where, resume):
    run(where, resume, ashby_board(("n1", "AI Engineer", "Python"), ("n2", "Data Engineer", "SQL")), "-1")
    out = run(where, resume, EMPTY, "-2")
    board = out["boards"][0]
    assert board["status"] == "unverified"
    assert board["new"] == [] and "postings" not in board          # no "0 new" claim
    assert out["status"] == loop.INCOMPLETE


def test_empty_board_does_not_overwrite_last_good_state(where, resume):
    run(where, resume, ashby_board(("n1", "AI Engineer", "Python"), ("n2", "Data Engineer", "SQL")), "-1")
    run(where, resume, EMPTY, "-2")
    state = loop.load_state(Policy(ROOT), where[1])
    assert state["boards"]["ashby:notion"]["last_good_count"] == 2


def test_empty_board_on_first_ever_run_is_a_baseline(where, resume):
    """No earlier count to compare with: an empty first response is recorded, not flagged."""
    out = run(where, resume, EMPTY, "-1")
    assert out["boards"][0]["status"] == "ok" and out["boards"][0]["baseline"]
