"""Revision round 1 (Aditya's REVISE, review/REVIEW.md §8): a present `meta` must be an object.

Written by Claude Code, 2026-11-10, BEFORE the production revision. All inputs are SYNTHETIC.
  1. A missing `meta` field remains permitted.
  2. A `meta` object without `total` remains permitted.
  3. A present non-object `meta` (null, numbers, strings, booleans, lists) is rejected as an
     inconsistent acquisition: exit 3, state unchanged, raw evidence and diagnostic kept.
"""
import json

import pytest

from agent.board import BoardInconsistentError, parse_jobs
from agent.watch import run
from tests.fixtures import RELEVANT
from tests.test_watch import args_for, boards, explode

NON_OBJECT_META = [None, 0, 5, -1, 1.5, "", "total", True, False, [], [1], ["total", 1]]


def test_1_missing_meta_is_permitted():
    assert parse_jobs({"jobs": [RELEVANT]}) == [RELEVANT]


def test_2_meta_object_without_total_is_permitted():
    assert parse_jobs({"jobs": [RELEVANT], "meta": {}}) == [RELEVANT]
    assert parse_jobs({"jobs": [RELEVANT], "meta": {"page": 1}}) == [RELEVANT]


@pytest.mark.parametrize("meta", NON_OBJECT_META, ids=repr)
def test_3_non_object_meta_is_rejected_by_the_parser(meta):
    with pytest.raises(BoardInconsistentError, match=r"meta .*not an object"):
        parse_jobs({"jobs": [RELEVANT], "meta": meta})


@pytest.mark.parametrize("meta", [None, 5, "total", True, [1]], ids=repr)
def test_3_non_object_meta_makes_the_watch_incomplete_and_keeps_state_and_evidence(tmp_path, capsys, meta):
    (b0,) = boards(tmp_path, [RELEVANT])
    assert run(args_for(tmp_path, b0, "base"), judge_fn=explode) == 0
    before = (tmp_path / "state.json").read_bytes()
    capsys.readouterr()

    raw = tmp_path / "bad_meta.json"
    raw.write_text(json.dumps({"jobs": [RELEVANT], "meta": meta}), encoding="utf-8")
    assert run(args_for(tmp_path, raw, "badmeta"), judge_fn=explode) == 3

    assert (tmp_path / "state.json").read_bytes() == before
    out = capsys.readouterr()
    assert "COMPLETE" not in out.out and "INCOMPLETE" in out.err
    run_dir = next((tmp_path / "runs").glob("*_badmeta"))
    assert (run_dir / "raw_response.json").read_bytes() == raw.read_bytes()
    assert "not an object" in (run_dir / "error.txt").read_text()


def test_3_non_object_meta_on_a_first_run_creates_no_baseline(tmp_path):
    raw = tmp_path / "first.json"
    raw.write_text(json.dumps({"jobs": [RELEVANT], "meta": None}), encoding="utf-8")
    assert run(args_for(tmp_path, raw, "first"), judge_fn=explode) == 3
    assert not (tmp_path / "state.json").exists()
