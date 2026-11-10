"""JS2 Step 5a: the bounded loop over the board list (GATE §1-§4, §6; R12, R15-R17, R19).

test_wv*_ are GATE §6's four wrong versions, by the names GATE gives them. The rest pin the exit
precedence, the retry rule, each budget, the repeat rule, Ctrl-C, the trace, and the code table.
Everything runs on scripted fake responses and a fake clock: no network, no waiting.
"""

import json
import re

import pytest
from fakes import (Clock, FakeClaude, START, ScriptedFetcher, ashby_board, ashby_job, board, board_row,
                   by_id, job, one_board)

from job_agent import __main__ as cli
from job_agent.common import net
from job_agent.common.errors import FetchError, InputError
from job_agent.common.paths import REPO, Paths, stamp
from job_agent.common.policy import PolicyError
from job_agent.loop import codes, exits
from job_agent.loop.budget import Limits
from job_agent.loop.results import FAILED, OK, SKIPPED, BoardResult
from job_agent.pipeline import RunOutcome, run
from job_agent.watch import watcher
from job_agent.watch.board_list import Board
from job_agent.watch.boards import ashby, greenhouse

STRIPE, CLOUDFLARE = greenhouse.board_url("stripe"), greenhouse.board_url("cloudflare")
OPENAI, STRIQE = ashby.board_url("openai"), greenhouse.board_url("striqe")
UUID = "8fb1615c-0000-0000-0000-00000000000a"


def http(status: int, body: bytes = b"") -> FetchError:
    return FetchError(f"fetch failed: HTTP {status}", "http", status, body)


def timeout() -> FetchError:
    return FetchError("fetch failed: timed out", "timeout")


def not_found() -> FetchError:
    return http(404, b"<html>Not found</html>")


def four_boards(stripe=None, cloudflare=None, openai=None, striqe=None) -> dict:
    """The shipped list (stripe, cloudflare, openai, striqe), each with a default response."""
    return {
        STRIPE: stripe or [board(job(1))],
        CLOUDFLARE: cloudflare or [board(job(1))],
        OPENAI: openai or [ashby_board(ashby_job(UUID))],
        STRIQE: striqe or [not_found()],
    }


def run_all(paths, script: dict, n: int = 0, clock=None, step: float = 0.0, limits: Limits = Limits(),
            fetcher=None) -> tuple[RunOutcome, dict]:
    """One run over every board in data/boards.json; returns the outcome and its verdicts.json."""
    clock = clock or Clock()
    fetcher = fetcher or ScriptedFetcher(script, clock, step)
    outcome = run(None, paths.default_resume, paths.default_profile, paths, now=START.replace(second=n),
                  fetcher=fetcher, ask=FakeClaude(), clock=clock, limits=limits)
    return outcome, json.loads((outcome.folder / "verdicts.json").read_text())


def trace_rows(outcome: RunOutcome) -> list[dict]:
    return [json.loads(line) for line in (outcome.folder / "trace.jsonl").read_text().splitlines()]


# ---- GATE §6 wrong versions --------------------------------------------------------------------

def test_wv1_same_job_id_on_different_boards_is_processed_separately(paths):
    run_all(paths, four_boards(), n=0)
    _, doc = run_all(paths, four_boards(stripe=[board(job(1), job(123))], cloudflare=[board(job(1), job(123))]), n=1)
    rule = [v for v in doc["verdicts"] if v["judge"] == "rule"]
    assert sorted((v["board"], v["posting_id"]) for v in rule) == [("cloudflare", 123), ("stripe", 123)]
    assert all(type(v["posting_id"]) is int for v in rule)   # original job id kept


def test_wv2_failed_board_does_not_mark_new_posting_seen(paths):
    run_all(paths, four_boards(), n=0)
    stripe_before = paths.state("stripe").read_text()
    # Run 2: stripe sends new posting 2, but next to a job without an id, so the board fails
    # validation (202) after the new posting was in hand; cloudflare succeeds.
    broken = json.dumps({"jobs": [job(1), job(2), {"title": "no id"}]}).encode()
    _, doc = run_all(paths, four_boards(stripe=[broken], cloudflare=[board(job(1), job(5))]), n=1)
    assert board_row(doc)["code"] == "202"
    assert paths.state("stripe").read_text() == stripe_before
    assert 5 in json.loads(paths.state("cloudflare").read_text())["seen_ids"]
    # Run 3: stripe recovers; posting 2 is still new.
    _, doc = run_all(paths, four_boards(stripe=[board(job(1), job(2))]), n=2)
    assert [v["posting_id"] for v in doc["verdicts"] if v["judge"] == "rule" and v["board"] == "stripe"] == [2]


@pytest.mark.parametrize("body, code", [(b'{"jobs": []}', "201"), (b"{}", "202")])
def test_wv3_empty_or_missing_jobs_list_is_a_validation_error(paths, body, code):
    outcome, doc = run_all(paths, four_boards(stripe=[body]))
    row = board_row(doc)
    assert (row["status"], row["code"], row["fetched"], row["new"]) == ("failed", code, None, None)
    assert outcome.exit != exits.FINISHED


def test_wv4_failed_board_has_no_job_count(paths):
    outcome, doc = run_all(paths, four_boards())
    row = board_row(doc, "striqe")
    assert (row["status"], row["code"], row["fetched"]) == ("failed", "101", None)
    line = next(l for l in outcome.summary.splitlines() if l.startswith("| striqe "))
    assert "101 fetch: board not found (HTTP 404)" in line
    assert re.search(r"\| — \| — \| 1 \|$", line)            # fetched and new are "—", never 0


# ---- Exits (GATE §1 precedence) -----------------------------------------------------------------

def _r(status, budget=None):
    return BoardResult("b", "greenhouse", status, budget=budget)


@pytest.mark.parametrize("results, shared, expected", [
    ([_r(OK), _r(OK)], None, exits.FINISHED),
    ([_r(OK), _r(FAILED)], None, exits.INCOMPLETE),                          # 3 ok + a 404 is incomplete
    ([_r(OK), _r(SKIPPED)], None, exits.INCOMPLETE),                         # interrupted
    ([_r(OK), _r(SKIPPED, "requests")], None, exits.BUDGET_EXHAUSTED),
    ([_r(FAILED, "requests"), _r(SKIPPED, "requests")], None, exits.BUDGET_EXHAUSTED),  # budget before "no ok"
    ([_r(FAILED), _r(FAILED)], None, exits.ERROR),                           # no board ok
    ([_r(OK), _r(SKIPPED, "boards")], "401 output: x", exits.ERROR),         # shared failure first
])
def test_exit_follows_gate_precedence(results, shared, expected):
    assert exits.decide(results, shared)[0] == expected


def test_three_ok_boards_and_one_404_is_incomplete(paths):
    outcome, doc = run_all(paths, four_boards())
    assert outcome.exit == exits.INCOMPLETE
    assert [b["status"] for b in doc["boards"]] == ["ok", "ok", "ok", "failed"]


# ---- Retry rule (GATE §3-§4) ---------------------------------------------------------------------

@pytest.mark.parametrize("attempts, status, code, n", [
    ([not_found()], FAILED, "101", 1),                       # not retryable: one attempt only
    ([http(403)], FAILED, "106", 1),
    ([timeout(), board(job(1))], OK, None, 2),               # a retry that works
    ([timeout(), timeout()], FAILED, "102", 2),              # same code twice: stop
    ([timeout(), http(503), http(503)], FAILED, "104", 3),   # different retryable code: one final try
    ([timeout(), http(503), board(job(1))], OK, None, 3),
    ([timeout(), http(503), timeout()], FAILED, "102", 3),   # never a 4th attempt, even with a new code
    ([timeout(), not_found()], FAILED, "101", 2),            # retryable checked first: 404 ends it
    ([http(429), http(500)], FAILED, "104", 2),              # 429 and 5xx are the same code
])
def test_retry_rule(paths, policy, attempts, status, code, n):
    fetcher = ScriptedFetcher({STRIPE: attempts + [AssertionError("one request too many")]})
    result, trace = one_board(paths, policy, Board("stripe", "greenhouse", "stripe", greenhouse), fetcher)
    assert (result.status, result.code, result.attempts) == (status, code, n)
    assert len(fetcher.urls) == n == sum(r["event"] == "request" for r in trace.rows)


@pytest.mark.parametrize("exc, code", [
    (http(404), "101"), (timeout(), "102"), (FetchError("x", "connection"), "103"), (http(502), "104"),
    (http(429), "104"), (PolicyError("x"), "105"), (http(403), "106"), (http(401), "106"),
])
def test_fetch_failures_get_their_code(exc, code):
    assert codes.for_fetch(exc) == code


def test_the_error_page_of_a_failed_attempt_is_kept_as_evidence(paths):
    run_all(paths, four_boards())
    saved = paths.raw(stamp(START)) / "striqe_attempt1_error.txt"
    assert saved.read_bytes() == b"<html>Not found</html>"


# ---- Budgets (GATE §2) ------------------------------------------------------------------------------

def test_request_budget_stops_retries_and_skips_the_rest(paths):
    every = [timeout()]
    outcome, doc = run_all(paths, four_boards(stripe=every, cloudflare=every, openai=every, striqe=every),
                           limits=Limits(requests=3))
    rows = {b["board"]: b for b in doc["boards"]}
    assert (rows["stripe"]["status"], rows["stripe"]["attempts"]) == ("failed", 2)
    assert (rows["cloudflare"]["status"], rows["cloudflare"]["budget"], rows["cloudflare"]["attempts"]) == ("failed", "requests", 1)
    assert [rows[b]["status"] for b in ("openai", "striqe")] == ["skipped", "skipped"]
    assert outcome.exit == exits.BUDGET_EXHAUSTED
    assert sum(r["event"] == "request" for r in trace_rows(outcome)) == 3


def test_board_budget_skips_boards_past_the_limit(paths):
    outcome, doc = run_all(paths, four_boards(), limits=Limits(boards=2))
    assert [(b["status"], b["budget"]) for b in doc["boards"]][2:] == [("skipped", "boards")] * 2
    assert outcome.exit == exits.BUDGET_EXHAUSTED


def test_time_budget_skips_boards_once_the_time_is_used(paths):
    # Each request takes 70 s on the fake clock: after two boards (140 s > 120 s) nothing new starts.
    outcome, doc = run_all(paths, four_boards(), step=70.0)
    assert [b["status"] for b in doc["boards"]] == ["ok", "ok", "skipped", "skipped"]
    assert {b["budget"] for b in doc["boards"][2:]} == {"seconds"}
    assert outcome.exit == exits.BUDGET_EXHAUSTED


def test_a_request_gets_ten_seconds_or_the_time_left(paths, monkeypatch):
    clock, timeouts = Clock(), []
    def fake_http_get(url, policy, timeout):
        timeouts.append(timeout)
        clock.now += 57.5
        return board(job(1)), "HTTP 200\n"
    monkeypatch.setattr(net, "http_get", fake_http_get)
    run(None, paths.default_resume, paths.default_profile, paths, now=START, ask=FakeClaude(), clock=clock)
    assert timeouts == [10.0, 10.0, 5.0]        # 120 - 2 x 57.5 = 5 s left for the third; then time is up


def test_budget_used_and_left_are_in_the_summary_and_the_record(paths):
    outcome, doc = run_all(paths, four_boards())
    assert doc["budget"]["requests_used"] == 4 and doc["budget"]["requests_left"] == 6
    assert "requests 4/10" in outcome.summary


# ---- Repeat rule (GATE §3), interruption, shared failure ----------------------------------------------

def test_a_posting_listed_twice_is_judged_once_and_the_repeat_is_recorded(paths):
    run_all(paths, four_boards(), n=0)
    outcome, doc = run_all(paths, four_boards(stripe=[board(job(1), job(2), job(2))]), n=1)
    assert [v["posting_id"] for v in doc["verdicts"] if v["judge"] == "rule"] == [2]
    assert {"event": "repeat_skipped", "board": "stripe", "kind": "posting", "key": "greenhouse/stripe/2"}.items() \
        <= next(r for r in trace_rows(outcome) if r["event"] == "repeat_skipped").items()


def test_ctrl_c_keeps_finished_boards_and_skips_the_rest(paths):
    run_all(paths, four_boards(), n=0)
    stripe_before = paths.state("stripe").read_text()
    outcome, doc = run_all(paths, four_boards(stripe=[board(job(1), job(2))], cloudflare=[KeyboardInterrupt()]), n=1)
    assert [b["status"] for b in doc["boards"]] == ["ok", "skipped", "skipped", "skipped"]
    assert {b["reason"] for b in doc["boards"][1:]} == {"interrupted by the user"}
    assert outcome.exit == exits.INCOMPLETE
    assert paths.state("stripe").read_text() != stripe_before        # the finished board's work is kept


def test_raw_evidence_that_cannot_be_saved_stops_the_run_with_error(paths, monkeypatch):
    real = watcher.save_raw
    def fail_for_cloudflare(folder, name, *rest):
        if name == "cloudflare":
            raise OSError("disk full")
        return real(folder, name, *rest)
    monkeypatch.setattr(watcher, "save_raw", fail_for_cloudflare)
    outcome, doc = run_all(paths, four_boards())
    assert outcome.exit == exits.ERROR and "401" in doc["exit_reason"]
    assert [b["status"] for b in doc["boards"]] == ["ok", "failed", "skipped", "skipped"]


# ---- Trace (R17) and the run's shape ---------------------------------------------------------------------

def test_trace_has_a_row_per_request_a_row_per_board_and_the_run_end(paths):
    outcome, _ = run_all(paths, four_boards(stripe=[timeout(), board(job(1))]))
    rows = trace_rows(outcome)
    requests = [r for r in rows if r["event"] == "request"]
    assert [(r["board"], r["attempt"], r["code"]) for r in requests] == [
        ("stripe", 1, "102"), ("stripe", 2, None), ("cloudflare", 1, None), ("openai", 1, None), ("striqe", 1, "101")]
    assert [r["requests_left"] for r in requests] == [9, 8, 7, 6, 5]
    order = [(r["event"], r["board"]) for r in rows if r["event"] in ("request", "board_end")]
    assert order == [("request", "stripe"), ("request", "stripe"), ("board_end", "stripe"),
                     ("request", "cloudflare"), ("board_end", "cloudflare"), ("request", "openai"),
                     ("board_end", "openai"), ("request", "striqe"), ("board_end", "striqe")]   # in time order
    assert rows[-1]["event"] == "run_end" and rows[-1]["exit"] == exits.INCOMPLETE


def test_default_run_visits_every_listed_board_in_order(paths):
    fetcher = ScriptedFetcher(four_boards())
    run_all(paths, {}, fetcher=fetcher)
    assert fetcher.urls == [STRIPE, CLOUDFLARE, OPENAI, STRIQE]


def test_from_raw_needs_a_board_name(paths):
    with pytest.raises(InputError, match="--board"):
        run(None, paths.default_resume, paths.default_profile, paths, now=START, from_raw=paths.boards)


@pytest.mark.parametrize("exit_, status", [(exits.FINISHED, 0), (exits.INCOMPLETE, 2), (exits.BUDGET_EXHAUSTED, 2), (exits.ERROR, 1)])
def test_cli_exit_status_says_whether_the_run_finished(monkeypatch, tmp_path, exit_, status):
    monkeypatch.setattr(cli, "run", lambda *a, **k: RunOutcome(tmp_path, "", exit_))
    assert cli.main([], paths=Paths(out=tmp_path)) == status


# ---- The code table and its document (JS2 D17) ---------------------------------------------------------

def test_error_codes_md_matches_the_code_table():
    """ERROR_CODES.md is for people, loop/codes.py for the program; they must say the same."""
    rows = re.findall(r"^\| `(\d{3})` \| (\w+) \| (.+?) \| (yes|no) \| (run|board|posting) \|$",
                      (REPO / "ERROR_CODES.md").read_text(), re.M)
    documented = {c: (stage, meaning, retry == "yes", scope) for c, stage, meaning, retry, scope in rows}
    in_code = {c.code: (c.stage, c.meaning, c.retryable, c.scope) for c in codes.CODES.values()}
    assert documented == in_code


def test_each_code_starts_with_its_stage_digit():
    assert all(c.code[0] in codes.STAGES for c in codes.CODES.values())
