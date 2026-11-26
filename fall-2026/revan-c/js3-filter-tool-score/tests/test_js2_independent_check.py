"""The independent check: it re-reads saved raw responses and tests the agent's claims against them.

It must not trust the agent's own summary, and it must not share the agent's parser.
"""
import json
import pathlib

from tools.independent_check import check_run
from js2_support import FakeClock, FakeFetcher, gh_body, gh_job, good_responses, make_workspace
from jsloop.loop import run_watch
from jsloop.policy import NORMAL_SELECTION

CHECK_SOURCE = pathlib.Path(__file__).resolve().parent.parent / "tools" / "independent_check.py"


def _failed(findings):
    return [f for f in findings if not f["passed"]]


def test_check_shares_no_code_with_the_agents():
    source = CHECK_SOURCE.read_text()
    for package in ("jsloop", "jsagent"):
        assert f"import {package}" not in source and f"from {package}" not in source


def test_js1_style_empty_board_reported_as_no_new_is_caught(tmp_path):
    raw = tmp_path / "empty.json"
    raw.write_text(json.dumps({"jobs": [], "meta": {"total": 0}}))
    record = tmp_path / "run.json"
    record.write_text(json.dumps({"mode": "seeded", "source": str(raw), "board": "klaviyo",
                                  "baseline": False, "postings_in_response": 0, "new_count": 0,
                                  "new_postings": []}))
    failed = _failed(check_run(record, base_dir=tmp_path))
    assert [f["check"] for f in failed] == ["empty-response-claimed-as-no-new-jobs"]


def test_consistent_js2_trace_passes(tmp_path):
    base = make_workspace(tmp_path)
    trace = run_watch(NORMAL_SELECTION, base_dir=base, fetcher=FakeFetcher(good_responses()), clock=FakeClock())
    findings = check_run(base / trace["trace_path"], base_dir=base)
    assert findings and _failed(findings) == []


def test_doctored_count_is_caught(tmp_path):
    base = make_workspace(tmp_path)
    trace = run_watch(NORMAL_SELECTION, base_dir=base, fetcher=FakeFetcher(good_responses()), clock=FakeClock())
    path = base / trace["trace_path"]
    data = json.loads(path.read_text())
    data["boards"][0]["postings_in_response"] = 7
    path.write_text(json.dumps(data))
    assert "count-matches-raw" in [f["check"] for f in _failed(check_run(path, base_dir=base))]


def test_finished_claim_with_failed_or_missing_board_is_caught(tmp_path):
    base = make_workspace(tmp_path)
    trace = run_watch(NORMAL_SELECTION, base_dir=base, fetcher=FakeFetcher(good_responses()), clock=FakeClock())
    path = base / trace["trace_path"]
    data = json.loads(path.read_text())
    data["boards"] = data["boards"][:2]  # a selected board vanished from the trace
    path.write_text(json.dumps(data))
    assert "every-selected-board-observed" in [f["check"] for f in _failed(check_run(path, base_dir=base))]


def test_js2_finished_with_empty_raw_is_caught(tmp_path):
    base = make_workspace(tmp_path)
    trace = run_watch(NORMAL_SELECTION, base_dir=base, fetcher=FakeFetcher(good_responses()), clock=FakeClock())
    path = base / trace["trace_path"]
    data = json.loads(path.read_text())
    raw = base / data["boards"][0]["raw_path"]
    raw.write_bytes(gh_body())  # pretend the saved response was empty
    data["boards"][0]["postings_in_response"] = 0
    path.write_text(json.dumps(data))
    names = [f["check"] for f in _failed(check_run(path, base_dir=base))]
    assert "empty-response-claimed-as-no-new-jobs" in names
