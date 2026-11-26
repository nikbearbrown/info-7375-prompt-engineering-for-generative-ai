"""The independent check, run on committed loop runs (real evidence)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType

from tests.conftest import REPO_ROOT

LIVE_RUN_1 = REPO_ROOT / "data/watch/loops/2026-11-09T08-14-22Z"
WRONG_BOARD_RUN = REPO_ROOT / "data/watch/loops/2026-11-09T08-16-16Z"
AFTER_PATCH_RUN = REPO_ROOT / "data/watch/loops/2026-11-09T08-23-46Z"
EXPECTATIONS = REPO_ROOT / "checks/expectations.toml"


def _checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "check_watch", REPO_ROOT / "checks/check_watch.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _failures(loop_dir: Path) -> set[tuple[str, str]]:
    rows = _checker().check_loop(loop_dir, EXPECTATIONS)
    return {(board, check) for board, check, passed, _ in rows if passed is False}


def test_live_run_1_passes_every_check() -> None:
    assert _failures(LIVE_RUN_1) == set()


def test_wrong_board_run_is_caught() -> None:
    assert _failures(WRONG_BOARD_RUN) == {
        ("(loop)", "FINISHED only if every board is OK and checks out"),
        ("greenhouse/ramp", "careers page uses this system"),
        ("greenhouse/ramp", "at least the expected floor"),
    }


def test_after_patch_run_agrees_with_the_check() -> None:
    assert _failures(AFTER_PATCH_RUN) == set()


def test_checker_fails_an_agent_that_failed_a_good_board(tmp_path: Path) -> None:
    """Constructed from live run 1: ``ashby/ramp`` relabelled FAILED by hand."""
    loop = tmp_path / "loop"
    loop.mkdir()
    shutil.copyfile(LIVE_RUN_1 / "trace.jsonl", loop / "trace.jsonl")
    report = json.loads((LIVE_RUN_1 / "report.json").read_text())
    for board in report["boards"]:
        if board["board"] == "ashby/ramp":
            board["state"] = "FAILED"
    (loop / "report.json").write_text(json.dumps(report))
    assert ("ashby/ramp", "failed board misses an expectation") in _failures(loop)


def test_checker_imports_nothing_from_the_agent() -> None:
    source = (REPO_ROOT / "checks/check_watch.py").read_text()
    assert "job_search_agent" not in source


def test_count_includes_a_job_without_an_id(tmp_path: Path) -> None:
    """The agent counts every listed job; the checker must count the same way."""
    body = json.dumps({"jobs": [{"id": 1}, {"title": "no id"}]}).encode()
    digest = hashlib.sha256(body).hexdigest()
    raw = tmp_path / "raw.json"
    raw.write_bytes(body)
    (tmp_path / "report.json").write_text(
        json.dumps({"raw_evidence": {"path": str(raw), "sha256": digest}})
    )
    (tmp_path / "state.before.json").write_text("null")
    board = {
        "board": "greenhouse/stripe",
        "state": "OK",
        "run_folder": str(tmp_path),
        "fetched_count": 2,
        "new_count": 1,
    }
    trace = [
        {"event": "tool.fetch.result", "board": "greenhouse/stripe", "sha256": digest}
    ]
    expect = {"stripe": {"system": "greenhouse", "min_postings": 2}}
    rows = _checker().check_board(board, trace, expect)
    assert [r for r in rows if r[1] is False] == []
