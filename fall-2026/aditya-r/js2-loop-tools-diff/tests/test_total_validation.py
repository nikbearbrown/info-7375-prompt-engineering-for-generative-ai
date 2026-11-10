"""Focused coverage for Greenhouse meta.total validation (review patch, CHANGE_REQUEST.md §5).

Written by Claude Code, 2026-11-10. These are NOT Aditya's designated regression test; that one is
tests/test_aditya_total_mismatch.py. All inputs are SYNTHETIC.
"""
import json

import pytest

from agent.board import BoardError, BoardInconsistentError, parse_jobs
from agent.watch import run
from tests.fixtures import NOT_RELEVANT, RELEVANT, valid_response, fake_judge_from
from tests.test_watch import args_for, boards, explode, report


def test_matching_total_is_accepted():
    assert parse_jobs({"jobs": [RELEVANT, NOT_RELEVANT], "meta": {"total": 2}}) == [RELEVANT, NOT_RELEVANT]


def test_matching_zero_total_is_accepted_by_the_parser():
    # The parser only checks count consistency. Whether an empty board is "suspect-empty" (GATE §4)
    # is a separate policy and outside this patch.
    assert parse_jobs({"jobs": [], "meta": {"total": 0}}) == []


@pytest.mark.parametrize("data", [
    {"jobs": [RELEVANT]},                           # no meta (e.g. archived captures)
    {"jobs": [RELEVANT], "meta": {}},               # meta without total
    {"jobs": [RELEVANT], "meta": {"page": 1}},
])
def test_absent_total_is_not_invented_or_required(data):
    assert parse_jobs(data) == [RELEVANT]


def test_mismatched_total_names_declared_and_observed_counts():
    with pytest.raises(BoardInconsistentError, match=r"declares 40 postings but the jobs list contains 1"):
        parse_jobs({"jobs": [RELEVANT], "meta": {"total": 40}})


def test_total_smaller_than_list_is_also_rejected():
    with pytest.raises(BoardInconsistentError, match=r"declares 1 postings but the jobs list contains 2"):
        parse_jobs({"jobs": [RELEVANT, NOT_RELEVANT], "meta": {"total": 1}})


@pytest.mark.parametrize("bad", [True, False, "1", 1.0, None, -1, [1], {"n": 1}])
def test_invalid_total_types_are_rejected_not_coerced(bad):
    with pytest.raises(BoardInconsistentError, match="not a nonnegative integer"):
        parse_jobs({"jobs": [RELEVANT], "meta": {"total": bad}})


def test_existing_schema_errors_keep_their_original_class():
    # A duplicate id is still a plain BoardError (exit 2), even when meta.total also mismatches.
    with pytest.raises(BoardError) as e:
        parse_jobs({"jobs": [RELEVANT, RELEVANT], "meta": {"total": 7}})
    assert not isinstance(e.value, BoardInconsistentError)


def _write(tmp_path, name, data):
    p = tmp_path / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_watch_rejects_invalid_total_type_as_incomplete_and_keeps_state(tmp_path):
    (b0,) = boards(tmp_path, [RELEVANT])
    assert run(args_for(tmp_path, b0, "base"), judge_fn=explode) == 0
    before = (tmp_path / "state.json").read_bytes()
    bad = _write(tmp_path, "bad.json", {"jobs": [RELEVANT], "meta": {"total": "1"}})
    assert run(args_for(tmp_path, bad, "bad"), judge_fn=explode) == 3
    assert (tmp_path / "state.json").read_bytes() == before


def test_watch_mismatch_saves_raw_and_diagnostic_and_prints_no_success(tmp_path, capsys):
    (b0,) = boards(tmp_path, [RELEVANT])
    run(args_for(tmp_path, b0, "base"), judge_fn=explode)
    capsys.readouterr()
    raw = _write(tmp_path, "mismatch.json", {"jobs": [RELEVANT], "meta": {"total": 40}})
    assert run(args_for(tmp_path, raw, "mismatch"), judge_fn=explode) == 3
    out = capsys.readouterr()
    assert "COMPLETE" not in out.out and "INCOMPLETE" in out.err
    run_dir = next((tmp_path / "runs").glob("*_mismatch"))
    assert (run_dir / "raw_response.json").read_bytes() == raw.read_bytes()
    assert "declares 40 postings but the jobs list contains 1" in (run_dir / "error.txt").read_text()
    assert not (run_dir / "report.json").exists()  # no report that could be read as a zero-new success


def test_first_run_with_mismatch_creates_no_baseline(tmp_path):
    raw = _write(tmp_path, "first.json", {"jobs": [RELEVANT], "meta": {"total": 40}})
    assert run(args_for(tmp_path, raw, "first"), judge_fn=explode) == 3
    assert not (tmp_path / "state.json").exists()


def test_matching_total_still_flows_through_normal_new_posting_processing(tmp_path):
    b0, b1 = boards(tmp_path, [RELEVANT], [RELEVANT, NOT_RELEVANT])  # fixtures set a correct meta.total
    run(args_for(tmp_path, b0, "base"), judge_fn=explode)
    judge = fake_judge_from({NOT_RELEVANT["id"]: valid_response(NOT_RELEVANT)})
    assert run(args_for(tmp_path, b1, "second"), judge_fn=judge) == 0
    rep, _ = report(tmp_path, "second")
    assert [o["posting_id"] for o in rep["new_postings"]] == [NOT_RELEVANT["id"]]
