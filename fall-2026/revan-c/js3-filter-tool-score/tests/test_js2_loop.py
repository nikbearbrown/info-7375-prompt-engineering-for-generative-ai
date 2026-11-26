"""Loop tests for Job-Search Agent 2: exits, the trace, budgets, the repeat rule, state, providers.

Each "WRONG VERSION n" test is the test GATE.md's "Plausible wrong versions" item n says must catch it.
Board bodies are CONSTRUCTED fixtures (see js2_support.py); no test touches the network.
"""
import json

import pytest

from jsloop.budget import PRODUCTION_BUDGET, Budget
from jsloop.fetch import FetchResult
from jsloop.loop import EXIT_CODES, Ledger, run_watch
from jsloop.policy import DEMO_SELECTION, NORMAL_SELECTION
from jsloop.providers import BoardInvalid, parse_greenhouse, parse_lever
from js2_support import (DUOLINGO, KLAVIYO, MISSING, PATCHMYPC, FakeClock, FakeFetcher, file_bytes,
                         gh_body, gh_job, good_responses, lever_body, lever_posting, make_workspace, ok)

STATE = ("state", "js2", "seen_ids.json")


def _run(base, selection=NORMAL_SELECTION, responses=None, **kw):
    fetcher = kw.pop("fetcher", None) or FakeFetcher(responses or good_responses())
    clock = kw.pop("clock", None) or FakeClock()
    return run_watch(selection, base_dir=base, fetcher=fetcher, clock=clock, **kw), fetcher


def _board(trace, name):
    return next(b for b in trace["boards"] if b["board"] == name)


# ---- the production numbers are the gate's numbers -----------------------------------------------

def test_production_budget_matches_gate():
    assert PRODUCTION_BUDGET == Budget(max_boards=4, max_requests=4, max_seconds=45.0,
                                       request_timeout=8.0, finalize_reserve=2.0)


def test_exit_codes_distinct_and_only_finished_is_zero():
    assert EXIT_CODES["finished"] == 0
    others = [EXIT_CODES[s] for s in ("incomplete", "budget-exhausted", "error")]
    assert all(code != 0 for code in others) and len(set(others)) == 3


# ---- finished -------------------------------------------------------------------------------------

def test_finished_run_reports_what_the_gate_requires(tmp_path):
    base = make_workspace(tmp_path)
    responses = good_responses()
    trace, fetcher = _run(base, responses=responses)
    assert trace["status"] == "finished" and trace["exit_code"] == 0
    assert trace["requests_made"] == 3 and len(fetcher.calls) == 3
    assert [b["board"] for b in trace["boards"]] == ["klaviyo", "duolingo", "patchmypc"]
    for board, url in zip(trace["boards"], (KLAVIYO, DUOLINGO, PATCHMYPC)):
        assert board["outcome"] == "ok" and board["mode"] == "live" and board["http_status"] == 200
        assert board["postings_in_response"] == 2
        # Raw bytes saved exactly as received, at the path the trace names.
        assert file_bytes(base / board["raw_path"]) == responses[url].body
    for key in ("elapsed_seconds", "run_mode", "state_updated", "selection", "started_at", "actions"):
        assert key in trace
    saved = json.loads((base / trace["trace_path"]).read_text())
    assert saved["status"] == "finished" and saved["boards"] == trace["boards"]


def test_first_run_is_a_baseline_not_every_posting_new(tmp_path):
    trace, _ = _run(make_workspace(tmp_path), approve_state_write=True)
    for board in trace["boards"]:
        assert board["baseline"] is True
        assert board["new_count"] == "baseline"
        assert board["new_postings"] == []


def test_second_run_reports_only_unseen_ids_with_rule_verdicts(tmp_path):
    base = make_workspace(tmp_path)
    _run(base, approve_state_write=True)
    responses = good_responses()
    responses[DUOLINGO] = ok(gh_body(gh_job(10, "Backend Engineer"), gh_job(11, "Designer", "Pittsburgh, PA"),
                                     gh_job(12, "Software Engineer, Platform", "Remote, US")))
    trace, _ = _run(base, responses=responses, approve_state_write=True)
    assert trace["status"] == "finished"
    assert _board(trace, "klaviyo")["new_count"] == 0
    duo = _board(trace, "duolingo")
    assert duo["baseline"] is False and duo["new_count"] == 1
    new = duo["new_postings"][0]
    assert new["posting_id"] == "12"
    assert new["rule_verdict"] in {"relevant", "not_relevant"}
    assert {e["condition"] for e in new["rule_justification"]} == {
        "title", "location", "skills", "seniority", "role_type"}


# ---- WRONG VERSION 1: clean but wrong empty result ----------------------------------------------

@pytest.mark.parametrize("url, body", [
    (KLAVIYO, json.dumps({"jobs": [], "meta": {"total": 0}}).encode()),
    (PATCHMYPC, b"[]"),
])
def test_empty_board_is_incomplete_never_no_new_jobs(tmp_path, url, body):
    base = make_workspace(tmp_path)
    _run(base, approve_state_write=True)
    state_before = file_bytes(base.joinpath(*STATE))
    trace, _ = _run(base, responses=good_responses() | {url: ok(body)}, approve_state_write=True)
    board = next(b for b in trace["boards"] if b["url"] == url)
    assert board["outcome"] == "failed"
    assert "empty" in board["error"]
    assert board["postings_in_response"] == "unknown" and board["new_count"] == "unknown"
    assert trace["status"] == "incomplete" and trace["exit_code"] == EXIT_CODES["incomplete"]
    assert file_bytes(base.joinpath(*STATE)) == state_before


# ---- WRONG VERSION 2: failure disguised as success -----------------------------------------------

def test_deliberate_404_is_labeled_first_recorded_and_kept(tmp_path):
    base = make_workspace(tmp_path)
    responses = good_responses() | {MISSING: FetchResult(404, b'{"status":404,"error":"Job not found"}', None)}
    trace, _ = _run(base, DEMO_SELECTION, responses=responses, demo=True)
    assert [b["board"] for b in trace["boards"]][-1] == "js2-deliberate-missing-board"
    bad = trace["boards"][-1]
    assert bad["deliberate_failure"] is True
    assert bad["outcome"] == "failed" and bad["http_status"] == 404
    assert bad["postings_in_response"] == "unknown" and bad["new_count"] == "unknown"
    assert file_bytes(base / bad["raw_path"]) == responses[MISSING].body
    assert trace["status"] == "incomplete" and trace["exit_code"] != 0
    # The label is in the action ledger BEFORE the request for that board.
    kinds = [(a["event"], a.get("url")) for a in trace["actions"]]
    assert kinds.index(("label", MISSING)) < kinds.index(("request", MISSING))


@pytest.mark.parametrize("result, expect", [
    (FetchResult(None, None, "timed out after 8.0 s"), "timed out"),
    (FetchResult(200, b"<html>not json</html>", None), "JSON"),
    (FetchResult(200, json.dumps({"jobs": [{"id": 1, "title": "x"}]}).encode(), None), "missing"),
    (FetchResult(200, gh_body(gh_job(1), gh_job(1)), None), "duplicate"),
    (FetchResult(503, b"busy", None), "HTTP 503"),
])
def test_failed_board_records_actual_error_never_zero(tmp_path, result, expect):
    trace, fetcher = _run(make_workspace(tmp_path), responses=good_responses() | {KLAVIYO: result})
    board = _board(trace, "klaviyo")
    assert board["outcome"] == "failed" and expect in board["error"]
    assert board["postings_in_response"] == "unknown" and board["new_count"] == "unknown"
    assert trace["status"] == "incomplete"
    # The loop continued to the remaining boards.
    assert _board(trace, "patchmypc")["outcome"] == "ok"
    if result.body is None:
        assert board["raw_path"] is None and "no response body" in board["raw_note"]
    # Zero automatic retries.
    assert [u for u, _ in fetcher.calls].count(KLAVIYO) == 1


# ---- WRONG VERSION 3: budget crossed by one ------------------------------------------------------

def test_request_budget_refused_before_sending(tmp_path):
    budget = Budget(max_boards=4, max_requests=2, max_seconds=45.0, request_timeout=8.0, finalize_reserve=2.0)
    trace, fetcher = _run(make_workspace(tmp_path), budget=budget)
    assert len(fetcher.calls) == 2
    assert trace["status"] == "budget-exhausted"
    assert trace["stop_reason"]["limit"] == "requests"
    assert _board(trace, "patchmypc")["outcome"] == "not_attempted"
    assert _board(trace, "patchmypc")["postings_in_response"] == "unknown"
    assert trace["budget"]["max_requests"] == 2 and trace["budget_label"] == "test"


def test_board_budget_refused_before_sending(tmp_path):
    budget = Budget(max_boards=1, max_requests=4, max_seconds=45.0, request_timeout=8.0, finalize_reserve=2.0)
    trace, fetcher = _run(make_workspace(tmp_path), budget=budget)
    assert len(fetcher.calls) == 1
    assert trace["status"] == "budget-exhausted" and trace["stop_reason"]["limit"] == "boards"


def test_request_allowed_with_exactly_10_seconds_left(tmp_path):
    clock = FakeClock()
    fetcher = FakeFetcher(good_responses(), clock=clock, advance_by={KLAVIYO: 35})
    trace, _ = _run(make_workspace(tmp_path), fetcher=fetcher, clock=clock)
    assert [u for u, _ in fetcher.calls][:2] == [KLAVIYO, DUOLINGO]
    assert fetcher.calls[1][1] == 8.0  # the timeout handed to the request


def test_timeout_never_exceeds_8_seconds_or_the_time_left(tmp_path):
    clock = FakeClock()
    fetcher = FakeFetcher(good_responses(), clock=clock, advance_by={KLAVIYO: 30})
    _run(make_workspace(tmp_path), fetcher=fetcher, clock=clock)
    for _, timeout in fetcher.calls:
        assert 0 < timeout <= 8.0


def test_overrun_during_a_request_is_budget_exhausted_not_finished(tmp_path):
    clock = FakeClock()
    fetcher = FakeFetcher(good_responses(), clock=clock, advance_by={PATCHMYPC: 50})
    base = make_workspace(tmp_path)
    trace, _ = _run(base, fetcher=fetcher, clock=clock, approve_state_write=True)
    assert trace["status"] == "budget-exhausted"
    assert trace["stop_reason"]["limit"] == "seconds"
    assert trace["elapsed_seconds"] >= 45
    assert trace["state_updated"] is False and not base.joinpath(*STATE).exists()


# ---- WRONG VERSION 4: duplicate action -----------------------------------------------------------

def test_duplicate_url_in_selection_is_preflight_error_with_no_request(tmp_path):
    trace, fetcher = _run(make_workspace(tmp_path), ["klaviyo", "duolingo", "klaviyo"])
    assert trace["status"] == "error" and fetcher.calls == []
    assert "duplicate" in trace["error"]


def test_ledger_suppresses_a_repeated_action():
    ledger = Ledger()
    assert ledger.claim("GET", KLAVIYO, board="klaviyo") is True
    assert ledger.claim("GET", KLAVIYO, board="klaviyo-again") is False
    assert ledger.entries[-1]["event"] == "suppressed"


# ---- WRONG VERSION 5 is B09/B10 in test_js2_boundary.py; WRONG VERSION 6 is B12/B13 there ---------

def test_observation_only_run_still_fetches_and_saves_trace(tmp_path):
    base = make_workspace(tmp_path)
    trace, fetcher = _run(base)
    assert len(fetcher.calls) == 3 and (base / trace["trace_path"]).exists()
    assert trace["state_updated"] is False


# ---- WRONG VERSION 7: state advances after failure ----------------------------------------------

def test_state_bytes_unchanged_after_incomplete_run_even_with_approval(tmp_path):
    base = make_workspace(tmp_path)
    _run(base, approve_state_write=True)
    before = file_bytes(base.joinpath(*STATE))
    responses = good_responses() | {DUOLINGO: FetchResult(None, None, "timed out after 8.0 s")}
    responses[KLAVIYO] = ok(gh_body(gh_job(1), gh_job(2, "Account Executive", "London, UK"), gh_job(3)))
    trace, _ = _run(base, responses=responses, approve_state_write=True)
    assert trace["status"] == "incomplete" and trace["state_updated"] is False
    assert file_bytes(base.joinpath(*STATE)) == before


def test_state_bytes_unchanged_after_observation_only_run(tmp_path):
    base = make_workspace(tmp_path)
    _run(base, approve_state_write=True)
    before = file_bytes(base.joinpath(*STATE))
    responses = good_responses()
    responses[KLAVIYO] = ok(gh_body(gh_job(1), gh_job(2, "Account Executive", "London, UK"), gh_job(3)))
    trace, _ = _run(base, responses=responses)
    assert _board(trace, "klaviyo")["new_count"] == 1  # compared against the saved state
    assert trace["status"] == "finished" and trace["state_updated"] is False
    assert file_bytes(base.joinpath(*STATE)) == before


def test_state_write_failure_is_error_and_trace_says_so(tmp_path):
    base = make_workspace(tmp_path)
    # A directory where the state write's temporary file must go: reading state still works,
    # so the run gets through all three boards and fails only at the write itself.
    (base / "state" / "js2" / "seen_ids.json.tmp").mkdir(parents=True)
    trace, fetcher = _run(base, approve_state_write=True)
    assert len(fetcher.calls) == 3 and all(b["outcome"] == "ok" for b in trace["boards"])
    assert trace["status"] == "error" and trace["state_updated"] is False
    assert "state write failed" in trace["error"]
    assert not base.joinpath(*STATE).exists()
    saved = json.loads((base / trace["trace_path"]).read_text())
    assert saved["status"] == "error" and saved["state_updated"] is False


# ---- WRONG VERSION 8: provider shapes conflated --------------------------------------------------

def test_greenhouse_parser_rejects_lever_shape():
    with pytest.raises(BoardInvalid, match="not a Greenhouse board"):
        parse_greenhouse(lever_body(lever_posting("aaa-1")))


def test_lever_parser_rejects_greenhouse_shape():
    with pytest.raises(BoardInvalid, match="not a Lever postings list"):
        parse_lever(gh_body(gh_job(1)))


def test_lever_posting_missing_location_is_rejected():
    posting = lever_posting("aaa-1")
    del posting["categories"]["location"]
    with pytest.raises(BoardInvalid, match="missing"):
        parse_lever(lever_body(posting))


def test_observations_keyed_by_board_and_posting_id(tmp_path):
    base = make_workspace(tmp_path)
    _run(base, approve_state_write=True)
    state = json.loads(base.joinpath(*STATE).read_text())
    assert sorted(state["boards"]) == ["duolingo", "klaviyo", "patchmypc"]
    assert state["boards"]["patchmypc"]["seen_ids"] == ["aaa-1", "bbb-2"]
    assert state["boards"]["klaviyo"]["seen_ids"] == ["1", "2"]


# ---- seeded runs ---------------------------------------------------------------------------------

def test_seeded_board_is_labeled_and_sends_no_request(tmp_path):
    base = make_workspace(tmp_path)
    (base / "fixtures/js2/klaviyo_seeded.json").write_bytes(gh_body(gh_job(1), gh_job(5)))
    trace, fetcher = _run(base, seeded={"klaviyo": "fixtures/js2/klaviyo_seeded.json"})
    klav = _board(trace, "klaviyo")
    assert klav["mode"] == "seeded" and klav["source"] == "fixtures/js2/klaviyo_seeded.json"
    assert KLAVIYO not in [u for u, _ in fetcher.calls]
    assert trace["run_mode"] == "mixed (seeded: klaviyo)"
    assert trace["requests_made"] == 2


def test_seeded_path_outside_fixtures_is_preflight_error(tmp_path):
    base = make_workspace(tmp_path)
    (base / "elsewhere.json").write_bytes(gh_body(gh_job(1)))
    trace, fetcher = _run(base, seeded={"klaviyo": "elsewhere.json"})
    assert trace["status"] == "error" and fetcher.calls == []


# ---- error: an output root that resolves outside the repository ----------------------------------

def test_output_root_symlinked_outside_repository_is_preflight_error(tmp_path):
    """EXTRA (not in GATE.md): if runs/ itself links outside the repository, nothing is fetched."""
    import os
    base = make_workspace(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    os.symlink(outside, base / "runs")
    trace, fetcher = _run(base)
    assert trace["status"] == "error" and fetcher.calls == []
    assert list(outside.iterdir()) == []
