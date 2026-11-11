"""JS2 loop: exits, budgets, repeat rule, error policy, state (GATE.md §1–4). SYNTHETIC inputs only."""
import gzip
import hashlib
import json

import pytest

from agent.loop import ConfigError, resolve_limits
from tests.js2_helpers import (ASHBY, GH, NOT_RELEVANT, RELEVANT, Clock, Transport, TransportError, ashby_body, board,
                               gh_body, judge_invalid, judge_valid, make_root, posting, run, trace)

A, B, Z = GH.format("alpha"), GH.format("beta"), GH.format("js2-no-such-board-zzz")
N = ASHBY.format("nova")


def two_boards(tmp_path, **kw):
    return make_root(tmp_path, [board("greenhouse", "alpha"), board("ashby", "nova")], **kw)


def state(root):
    return json.loads((root / "out/state/seen.json").read_text())


def test_first_run_baselines_every_board_and_finishes(tmp_path):
    root = two_boards(tmp_path)
    code, rep, _ = run(root, Transport({A: [(200, gh_body(RELEVANT))], N: [(200, ashby_body("u-1", "u-2"))]}))
    assert code == 0 and rep["status"] == "finished"
    assert [(o["key"], o["kind"], o["observed"], o["new"]) for o in rep["boards"]] == [
        ("greenhouse:alpha", "baseline", 1, 0), ("ashby:nova", "baseline", 2, 0)]
    assert state(root)["boards"]["ashby:nova"]["ids"] == {"u-1": "baseline", "u-2": "baseline"}


def test_second_run_judges_only_new_ids_and_finishes(tmp_path):
    root = two_boards(tmp_path)
    run(root, Transport({A: [(200, gh_body(RELEVANT))], N: [(200, ashby_body("u-1"))]}))
    code, rep, _ = run(root, Transport({A: [(200, gh_body(RELEVANT, NOT_RELEVANT))], N: [(200, ashby_body("u-1"))]}))
    assert code == 0
    assert [p["posting_id"] for p in rep["postings"]] == ["202"]
    assert state(root)["boards"]["greenhouse:alpha"]["ids"]["202"] == "completed"


def test_W2_W12_deliberate_404_is_a_failure_with_null_counts_and_nonzero_exit(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha"), board("greenhouse", "js2-no-such-board-zzz")])
    t = Transport({A: [(200, gh_body(RELEVANT))], Z: [(404, b'{"status":404,"error":"Job not found"}')]})
    code, rep, _ = run(root, t)
    assert code == 3 and rep["status"] == "incomplete"
    z = rep["boards"][1]
    assert z["status"] == "failed" and z["observed"] is None and z["new"] is None and "404" in z["reason"]
    assert "greenhouse:js2-no-such-board-zzz" not in state(root)["boards"]  # failed board state untouched
    assert t.calls.count(Z) == 1  # W4: a 404 is not retried


def test_W1_suspect_empty_on_a_known_board_is_not_zero_new(tmp_path):
    root = two_boards(tmp_path)
    run(root, Transport({A: [(200, gh_body(RELEVANT, NOT_RELEVANT))], N: [(200, ashby_body("u-1"))]}))
    before = state(root)["boards"]["greenhouse:alpha"]
    code, rep, _ = run(root, Transport({A: [(200, gh_body())], N: [(200, ashby_body("u-1"))]}))
    assert code == 3
    a = rep["boards"][0]
    assert a["kind"] == "suspect-empty" and a["new"] is None and a["observed"] is None
    assert state(root)["boards"]["greenhouse:alpha"] == before


def test_W1_suspect_empty_on_a_first_run_creates_no_baseline(tmp_path):
    root = two_boards(tmp_path)
    code, rep, _ = run(root, Transport({A: [(200, gh_body())], N: [(200, b'{"apiVersion":"1","jobs":[]}')]}))
    assert code == 3 and all(o["kind"] == "suspect-empty" for o in rep["boards"])
    assert state(root)["boards"] == {}


def test_W1_count_inconsistent_response_fails_the_board(tmp_path):
    root = two_boards(tmp_path)
    code, rep, _ = run(root, Transport({A: [(200, gh_body(RELEVANT, total=40))], N: [(200, ashby_body("u-1"))]}))
    assert code == 3 and rep["boards"][0]["kind"] == "inconsistent" and rep["boards"][0]["observed"] is None


@pytest.mark.parametrize("first", [(503, b"busy"), TransportError("timeout", "slow"), TransportError("connection", "reset")])
def test_W4_transient_failure_retried_once_after_wait_and_counted(tmp_path, first):
    root = make_root(tmp_path, [board("greenhouse", "alpha")])
    clock = Clock()
    t = Transport({A: [first, (200, gh_body(RELEVANT))]}, clock=clock)
    code, rep, run_dir = run(root, t, clock=clock)
    assert code == 0 and t.calls == [A, A]
    assert rep["budget"]["http_attempts"]["used"] == 2
    ev = trace(run_dir)
    attempts = [e for e in ev if e["event"] == "http_attempt"]
    assert attempts[1]["retry_of"] == attempts[0]["seq"] and any(e["event"] == "retry_wait" for e in ev)


def test_W4_second_transient_failure_and_other_transport_errors_are_not_retried_further(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha"), board("greenhouse", "beta")])
    t = Transport({A: [(503, b""), (503, b"")], B: [TransportError("other", "TLS failure")]})
    code, rep, _ = run(root, t)
    assert code == 3 and t.calls == [A, A, B]


def test_W3_eighth_http_attempt_allowed_and_no_ninth_is_sent(tmp_path):
    names = ["alpha", "beta", "gamma", "delta"]
    root = make_root(tmp_path, [board("greenhouse", n) for n in names])
    t = Transport({GH.format(n): [(503, b""), (503, b"")] for n in names})
    code, rep, _ = run(root, t)
    assert len(t.calls) == 8 and rep["budget"]["http_attempts"]["used"] == 8
    assert code == 3  # all retries fit: the limit was reached but did not prevent required work


def test_W3_lowered_http_budget_blocks_the_retry_and_reports_exhaustion(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha"), board("greenhouse", "beta")])
    t = Transport({A: [(503, b""), (200, gh_body(RELEVANT))], B: [(503, b""), (200, gh_body(RELEVANT))]})
    code, rep, _ = run(root, t, limits={"http_attempts": 3})
    assert len(t.calls) == 3 and code == 4 and rep["status"] == "budget-exhausted"
    assert rep["boards"][1]["status"] == "failed" and rep["boards"][1]["budget"] == "http_attempts"


def test_W3_http_budget_is_checked_before_each_first_attempt(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha"), board("greenhouse", "beta")])
    t = Transport({A: [(200, gh_body(RELEVANT))], B: [(200, gh_body(RELEVANT))]})
    code, rep, _ = run(root, t, limits={"http_attempts": 1})
    assert t.calls == [A] and code == 4
    assert rep["boards"][1]["status"] == "unattempted" and rep["boards"][1]["budget"] == "http_attempts"


def _many_new(tmp_path, n):
    root = make_root(tmp_path, [board("greenhouse", "alpha")])
    run(root, Transport({A: [(200, gh_body(RELEVANT))]}))
    new = [posting(1000 + i, f"Account Executive {i}", "<p>Sales</p>") for i in range(n)]
    return root, Transport({A: [(200, gh_body(RELEVANT, *new))]})


def test_W3_tenth_model_call_allowed_eleventh_never_starts(tmp_path):
    root, t = _many_new(tmp_path, 11)
    calls = []

    def judge(p, r, timeout):
        calls.append(p["id"])
        return judge_valid(p, r, timeout)

    code, rep, _ = run(root, t, judge=judge)
    assert len(calls) == 10 and rep["budget"]["model_calls"]["used"] == 10
    assert code == 4 and rep["postings"][-1]["JUDGMENT"]["status"] == "not-run"
    assert state(root)["boards"]["greenhouse:alpha"]["ids"]["1010"] == "pending"


def test_exactly_ten_new_postings_fit_and_finish(tmp_path):
    root, t = _many_new(tmp_path, 10)
    code, rep, _ = run(root, t)
    assert code == 0 and rep["budget"]["model_calls"]["used"] == 10


def test_elapsed_budget_with_reserve_stops_new_attempts_and_bounds_timeouts(tmp_path):
    names = ["alpha", "beta", "gamma"]
    root = make_root(tmp_path, [board("greenhouse", n) for n in names])
    clock = Clock()
    seen_timeouts = []

    class Slow(Transport):
        def __call__(self, url, timeout, deadline):
            seen_timeouts.append(timeout)
            return super().__call__(url, timeout, deadline)

    t = Slow({GH.format(n): [(200, gh_body(RELEVANT))] for n in names}, clock=clock, cost=85)
    code, rep, _ = run(root, t, clock=clock)
    # t=0: allowance 170 -> timeout 20; t=85: allowance 85 -> 20; t=170: allowance 0 -> no attempt
    assert len(t.calls) == 2 and seen_timeouts == [20.0, 20.0]
    assert code == 4 and rep["boards"][2]["status"] == "unattempted" and rep["boards"][2]["budget"] == "seconds"


def test_W10_invalid_judgment_stays_pending_then_completes_later(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha")])
    run(root, Transport({A: [(200, gh_body(RELEVANT))]}))
    code, rep, _ = run(root, Transport({A: [(200, gh_body(RELEVANT, NOT_RELEVANT))]}), judge=judge_invalid)
    assert code == 3 and state(root)["boards"]["greenhouse:alpha"]["ids"]["202"] == "pending"
    code, rep, _ = run(root, Transport({A: [(200, gh_body(RELEVANT, NOT_RELEVANT))]}))
    assert code == 0 and rep["boards"][0]["retried"] == 1
    assert state(root)["boards"]["greenhouse:alpha"]["ids"]["202"] == "completed"


def test_W9_same_id_on_two_boards_stays_distinct(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha"), board("greenhouse", "beta")])
    run(root, Transport({A: [(200, gh_body(RELEVANT))], B: [(200, gh_body(NOT_RELEVANT))]}))
    code, rep, _ = run(root, Transport({A: [(200, gh_body(RELEVANT))], B: [(200, gh_body(NOT_RELEVANT, RELEVANT))]}))
    assert rep["boards"][1]["new_ids"] == ["101"]  # 101 was seen on alpha, but is new on beta


def test_precedence_budget_exhausted_over_incomplete_keeps_all_reasons(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha"), board("greenhouse", "js2-no-such-board-zzz")])
    run(root, Transport({A: [(200, gh_body(RELEVANT))], Z: [(404, b"")]}))
    new = [posting(2000 + i, f"Clerk {i}", "<p>x</p>") for i in range(3)]
    code, rep, _ = run(root, Transport({A: [(200, gh_body(RELEVANT, *new))], Z: [(404, b"")]}), limits={"model_calls": 1})
    assert code == 4
    assert any("js2-no-such-board-zzz" in r for r in rep["incomplete_reasons"])
    assert sum("judgment not run" in r for r in rep["budget_reasons"]) == 2


def test_run_level_error_publishes_no_state_and_stops_work(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha"), board("greenhouse", "beta"), board("ashby", "nova")])
    t = Transport({A: [(200, gh_body(RELEVANT))], B: [(302, b"", {"location": "https://evil.example/x"})],
                   N: [(200, ashby_body("u"))]})
    code, rep, run_dir = run(root, t)
    assert code == 2 and rep["status"] == "error" and t.calls == [A, B]
    assert not (root / "out/state/seen.json").exists() and rep["state"]["published"] is False
    assert rep["boards"][2]["status"] == "unattempted"
    assert (run_dir / "trace.jsonl").exists() and any(e["event"] == "redirect_refused" for e in trace(run_dir))


@pytest.mark.parametrize("boards, msg", [
    ([board("greenhouse", n) for n in "abcde"], "limit is 4"),
    ([board("greenhouse", "a"), board("greenhouse", "a")], "duplicate"),
    ([board("lever", "a")], "not supported"),
    ([board("greenhouse", "../etc")], "invalid board token"),
])
def test_config_errors_exit_2_before_any_request(tmp_path, boards, msg):
    root = make_root(tmp_path, boards)
    t = Transport({})
    code, rep, _ = run(root, t)
    assert code == 2 and t.calls == [] and msg in rep["errors"][0]


def test_limits_may_be_lowered_but_never_raised():
    assert resolve_limits({"http_attempts": 4})["http_attempts"] == 4
    with pytest.raises(ConfigError):
        resolve_limits({"http_attempts": 9})
    with pytest.raises(ConfigError):
        resolve_limits({"seconds": 181})


def test_inherited_js1_state_seeds_only_its_board(tmp_path):
    js1 = {"board": "alpha", "ids": {"101": "baseline", "202": "completed"}, "runs": [{}]}
    root = make_root(tmp_path, [board("greenhouse", "alpha", seed_from_js1_state="state/seen.json")], js1_state=js1)
    code, rep, run_dir = run(root, Transport({A: [(200, gh_body(RELEVANT, NOT_RELEVANT, posting(303, "Clerk", "<p>x</p>")))]}))
    assert code == 0 and rep["boards"][0]["new_ids"] == ["303"]
    assert any(e["event"] == "state_seeded" and e["ids"] == 2 for e in trace(run_dir))
    assert json.loads((root / "state/seen.json").read_text()) == js1  # inherited file untouched


def test_malformed_working_state_is_an_error_not_a_reset(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha")])
    (root / "out/state").mkdir(parents=True)
    (root / "out/state/seen.json").write_text("{broken")
    t = Transport({})
    code, _, _ = run(root, t)
    assert code == 2 and t.calls == [] and (root / "out/state/seen.json").read_text() == "{broken"


def test_trace_has_every_attempt_and_raw_bytes_match(tmp_path):
    root = make_root(tmp_path, [board("greenhouse", "alpha"), board("greenhouse", "js2-no-such-board-zzz")])
    t = Transport({A: [(503, b"x"), (200, gh_body(RELEVANT))], Z: [(404, b"nf")]})
    code, rep, run_dir = run(root, t)
    results = [e for e in trace(run_dir) if e["event"] == "http_result"]
    assert len(results) == len(t.calls) == 3
    for e in results:
        body = gzip.decompress((run_dir / e["raw"]).read_bytes())
        assert hashlib.sha256(body).hexdigest() == e["sha256"]
