"""Exits, precedence, config validation, and CLI codes (GATE "Loop, budgets, and exits";
F6, F7, F13–F15; Wrong versions)."""

import json

import pytest

from agent import PROJECT_DIR, providers, state
from agent.__main__ import main
from agent.config import parse_config
from agent.errors import EvidenceError
from agent.providers import Board, listing_url
from support import (DEMO_BOARDS, INVALID, LINEAR, NOTION, RUN_ID, STRIPE, FakeClock, Slow, TransportSpy,
                     board_entry, ok, read_summary, read_trace, run_agent, status, timeout, write_config)

DEMO_CONFIG = PROJECT_DIR / "config" / "boards.json"


def demo_routes():
    return {STRIPE: [ok(STRIPE, [1, 2])], NOTION: [ok(NOTION, ["a"])], LINEAR: [ok(LINEAR, ["b", "c"])],
            INVALID: [status(INVALID, 404, b'{"status":404,"error":"Job not found"}')]}


def test_demo_config_lists_the_gate_boards_in_order():
    """GATE "Scope and boards": the four boards, in config order."""
    cfg = parse_config(DEMO_CONFIG.read_bytes())
    assert cfg.boards == DEMO_BOARDS and cfg.duplicates == ()


def test_exit_finished_when_every_board_succeeds(tmp_path):
    """GATE exits: `finished` when every distinct scheduled board succeeded within budget."""
    result, spy, out = run_agent(tmp_path, [STRIPE, NOTION, LINEAR],
                                 {b: s for b, s in demo_routes().items() if b != INVALID})
    assert result.exit == "finished" and result.code == 0
    summary = read_summary(out)
    assert [b["status"] for b in summary["boards"]] == ["succeeded"] * 3
    assert [b["fetched"] for b in summary["boards"]] == [2, 1, 2]
    assert summary["state"]["written"] is True
    assert spy.urls() == [listing_url(b) for b in (STRIPE, NOTION, LINEAR)]


def test_exit_incomplete_failed_board_has_null_counts(tmp_path):
    """Wrong versions: "turns a failed fetch into an empty list and exits finished" -> the failed
    board has no counts and the completed schedule exits incomplete (F15: JSON null)."""
    result, _, out = run_agent(tmp_path, DEMO_BOARDS, demo_routes(), config_path=DEMO_CONFIG)
    assert result.exit == "incomplete" and result.code == 3
    summary = read_summary(out)
    failed = board_entry(summary, INVALID)
    assert failed["status"] == "failed" and failed["failure"]["kind"] == "http-404"
    assert failed["fetched"] is None and failed["new"] is None
    raw_text = (out / "runs" / RUN_ID / "summary.json").read_text()
    assert '"fetched": null' in raw_text and '"new": null' in raw_text
    assert [board_entry(summary, b)["status"] for b in (STRIPE, NOTION, LINEAR)] == ["succeeded"] * 3


@pytest.mark.parametrize("steps", [
    [status(STRIPE, 503), status(STRIPE, 503)],
    [timeout(), timeout()],
    [status(STRIPE, 200, b"")],
], ids=["503-twice", "timeout-twice", "empty-body"])
def test_failed_fetch_is_not_an_empty_list(tmp_path, steps):
    """Wrong versions row 1, transport and body variants: no counts, exit incomplete, never zero."""
    result, _, out = run_agent(tmp_path, [STRIPE, NOTION], {STRIPE: steps, NOTION: [ok(NOTION, ["a"])]})
    entry = board_entry(read_summary(out), STRIPE)
    assert entry["fetched"] is None and entry["new"] is None
    assert result.exit == "incomplete"


def test_valid_empty_jobs_counts_zero_and_finishes(tmp_path):
    """Board failure policy: a valid empty `jobs` list means zero fetched (contrast with failures)."""
    result, _, out = run_agent(tmp_path, [STRIPE], {STRIPE: [ok(STRIPE, [])]})
    assert result.exit == "finished"
    assert board_entry(read_summary(out), STRIPE)["fetched"] == 0


def test_budget_exhausted_beats_incomplete_and_keeps_earlier_failure(tmp_path):
    """Wrong versions: "A board failure hides a later budget limit" -> precedence gives
    budget-exhausted, and the earlier board failure stays in the trace."""
    result, _, out = run_agent(tmp_path, [INVALID, NOTION, LINEAR],
                               {INVALID: [status(INVALID, 404)], NOTION: [Slow(58.0, ok(NOTION, ["a"]))],
                                LINEAR: [ok(LINEAR, ["b"])]})
    assert result.exit == "budget-exhausted" and result.code == 4
    trace = read_trace(out)
    assert any(e["board"] == INVALID.key and e["operation"] == "fetch" and e["status"] == 404 for e in trace)
    summary = read_summary(out)
    assert board_entry(summary, INVALID)["status"] == "failed"
    assert summary["pending"] == [{"board": LINEAR.key, "pending": "board"}]


def test_error_beats_everything_and_keeps_earlier_failure(tmp_path, monkeypatch):
    """Wrong versions: "A board failure hides a later ... fatal error" -> with a board failure
    (incomplete) and a pending retry (budget-exhausted), a state write failure still exits error."""

    def broken_commit(gate, store):
        raise EvidenceError("synthetic: cannot write state.json")

    monkeypatch.setattr(state, "commit", broken_commit)
    original = b'{"greenhouse/stripe": [1]}'
    result, _, out = run_agent(tmp_path, [INVALID, STRIPE],
                               {INVALID: [status(INVALID, 404)], STRIPE: [Slow(57.0, timeout())]},
                               state=original)
    assert result.exit == "error" and result.code == 2
    trace = read_trace(out)
    assert any(e["board"] == INVALID.key and e["status"] == 404 for e in trace)
    assert any(e["board"] == STRIPE.key and "retry pending" in (e["next"] or "") for e in trace)
    summary = read_summary(out)
    assert summary["exit"] == "error" and summary["budget_limit_hit"] == "network-window"
    assert (out / "state.json").read_bytes() == original


@pytest.mark.parametrize("fatal,budget_limit,any_failed,expected", [
    (True, "network-window", True, "error"),
    (True, "attempts", False, "error"),
    (True, None, True, "error"),
    (True, None, False, "error"),
    (False, "network-window", True, "budget-exhausted"),
    (False, "attempts", False, "budget-exhausted"),
    (False, None, True, "incomplete"),
    (False, None, False, "finished"),
])
def test_exit_precedence_table(fatal, budget_limit, any_failed, expected):
    """GATE: "If more than one exit applies, use this order: error -> budget-exhausted ->
    incomplete -> finished." Every combination, on the resolver directly."""
    from agent.loop import resolve_exit
    assert resolve_exit(fatal=fatal, budget_limit=budget_limit, any_failed=any_failed) == expected


def test_duplicate_board_is_skipped_and_logged(tmp_path):
    """GATE "5 distinct boards": the same (provider, token) twice is skipped and logged."""
    result, spy, out = run_agent(tmp_path, [STRIPE, NOTION, STRIPE],
                                 {STRIPE: [ok(STRIPE, [1])], NOTION: [ok(NOTION, ["a"])]})
    assert result.exit == "finished"
    assert spy.urls() == [listing_url(STRIPE), listing_url(NOTION)]
    summary = read_summary(out)
    assert summary["duplicates_skipped"] == [{"board": STRIPE.key, "config_index": 2, "kept_index": 0}]
    assert any(e["operation"] == "config-duplicate" and e["board"] == STRIPE.key for e in read_trace(out))


def test_six_distinct_boards_is_error_before_transport(tmp_path):
    """F6: a sixth distinct board makes the config invalid; exit error before transport."""
    boards = [Board("greenhouse", f"co-{i}") for i in range(6)]
    result, spy, out = run_agent(tmp_path, boards, {b: [ok(b, [1])] for b in boards})
    assert result.exit == "error" and result.code == 2
    assert spy.calls == []
    assert read_summary(out)["error"]["stage"] == "config"
    assert not (out / "state.json").exists()


def test_five_distinct_plus_a_duplicate_is_valid(tmp_path):
    """F6: duplicate pairs are skipped and count once toward the limit of five."""
    boards = [Board("greenhouse", f"co-{i}") for i in range(5)]
    result, spy, _ = run_agent(tmp_path, boards + [boards[0]], {b: [ok(b, [1])] for b in boards})
    assert result.exit == "finished" and len(spy.calls) == 5


def test_zero_boards_is_error_before_transport(tmp_path):
    """F14: zero configured boards makes the config invalid; exit error before transport."""
    result, spy, out = run_agent(tmp_path, [], {})
    assert result.exit == "error" and spy.calls == []
    assert read_summary(out)["error"]["stage"] == "config"


@pytest.mark.parametrize("entry", [
    {"provider": "lever", "token": "stripe"},
    {"provider": "greenhouse", "token": "Stripe"},
    {"provider": "greenhouse", "token": "stripe/../x"},
    {"provider": "greenhouse", "token": "stripe\n"},
    {"provider": "greenhouse", "token": ""},
], ids=["unknown-provider", "uppercase", "slash", "newline", "empty"])
def test_invalid_board_entry_is_error_before_transport(tmp_path, entry):
    """F7: an unknown provider or a token failing a full match of [a-z0-9-]+ is invalid config."""
    config_path = write_config(tmp_path / "boards.json", [STRIPE, entry])
    result, spy, out = run_agent(tmp_path, None, {STRIPE: [ok(STRIPE, [1])]}, config_path=config_path)
    assert result.exit == "error" and spy.calls == []
    assert read_summary(out)["error"]["stage"] == "config"


def test_config_cannot_raise_limits(tmp_path):
    """GATE "Changing the limits": the board config can't raise them (an extra key is refused)."""
    config_path = write_config(tmp_path / "boards.json", [STRIPE], max_http_attempts=50)
    result, spy, _ = run_agent(tmp_path, None, {STRIPE: [ok(STRIPE, [1])]}, config_path=config_path)
    assert result.exit == "error" and spy.calls == []


def test_permission_denial_during_run_is_a_board_failure(tmp_path, monkeypatch):
    """F7 + GATE: a denial when checking a request during the run is a board failure and
    costs zero attempts."""
    real = providers.listing_url
    monkeypatch.setattr(providers, "listing_url",
                        lambda board: "https://example.com/" if board == STRIPE else real(board))
    result, spy, out = run_agent(tmp_path, [STRIPE, NOTION], {NOTION: [ok(NOTION, ["a"])]})
    assert result.exit == "incomplete"
    assert spy.urls() == [real(NOTION)]
    summary = read_summary(out)
    entry = board_entry(summary, STRIPE)
    assert entry["failure"]["kind"] == "permission-denied" and entry["attempts"] == 0
    assert summary["attempts_used"] == 1


CLI_CASES = {
    "finished": ([STRIPE], {STRIPE: [ok(STRIPE, [1])]}, 0),
    "error": ([], {}, 2),
    "incomplete": ([STRIPE, INVALID], {STRIPE: [ok(STRIPE, [1])], INVALID: [status(INVALID, 404)]}, 3),
    "budget-exhausted": ([NOTION, STRIPE], {NOTION: [Slow(58.0, ok(NOTION, ["a"]))], STRIPE: [ok(STRIPE, [1])]}, 4),
}


@pytest.mark.parametrize("expected", list(CLI_CASES))
def test_cli_exit_codes(tmp_path, capsys, expected):
    """F15: CLI exit codes are finished 0, error 2, incomplete 3, budget-exhausted 4; one result line."""
    boards, routes, code = CLI_CASES[expected]
    clock = FakeClock()
    config_path = write_config(tmp_path / "boards.json", boards)
    spy = TransportSpy(routes={listing_url(b): steps for b, steps in routes.items()}, clock=clock)
    returned = main(["--config", str(config_path), "--out", str(tmp_path / "out")],
                    transport=spy, clock=clock, sleep=clock.sleep, run_id="run-cli")
    assert returned == code
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1 and lines[0].startswith(f"{expected} (exit {code}):")
    summary = json.loads((tmp_path / "out" / "runs" / "run-cli" / "summary.json").read_text())
    assert summary["exit"] == expected and summary["exit_code"] == code
