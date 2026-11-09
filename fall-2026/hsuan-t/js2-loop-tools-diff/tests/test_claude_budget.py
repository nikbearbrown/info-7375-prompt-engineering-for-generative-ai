"""The optional Claude step under its budget (GATE §2, D1, D20).

Claude is off unless --claude; when on it sees every new posting, in board order, until 30 calls or
300 s of Claude time (all calls together) are used; each call's timeout is the Claude time left; a
posting the budget never reached is code 304 and makes the run budget-exhausted; a failed or unsent
call never changes the rule's verdict. Fake Claude, fake clock: no network.
"""

import json
import sys
import types

import pytest
from fakes import GOOD, SENIOR, START, Clock, FakeClaude, ScriptedFetcher, ashby_board, ashby_job, board, by_id, job

from job_agent import __main__ as cli
from job_agent.common.errors import ClaudeCallError
from job_agent.common.paths import Paths
from job_agent.judges import claude_api, claude_cli
from job_agent.loop import exits
from job_agent.loop.budget import Budget
from job_agent.pipeline import RunOutcome, run
from job_agent.watch.boards import ashby, greenhouse

STRIPE, CLOUDFLARE = greenhouse.board_url("stripe"), greenhouse.board_url("cloudflare")
OPENAI, STRIQE = ashby.board_url("openai"), greenhouse.board_url("striqe")
UUID = "8fb1615c-0000-0000-0000-00000000000a"


def boards(stripe, cloudflare=None) -> dict:
    return {STRIPE: [stripe], CLOUDFLARE: [cloudflare or board(job(1))],
            OPENAI: [ashby_board(ashby_job(UUID))], STRIQE: [board(job(1))]}


class SlowClaude(FakeClaude):
    """A fake Claude whose every call takes `seconds` on the test clock."""

    def __init__(self, clock: Clock, seconds: float, **kw):
        super().__init__(**kw)
        self.clock, self.seconds = clock, seconds

    def __call__(self, system, user):
        self.clock.now += self.seconds
        return super().__call__(system, user)


def two_runs(paths, second: dict, ask, clock=None, step=0.0):
    """A baseline run, then a run with Claude on; returns the second run's outcome and record."""
    clock = clock or Clock()
    run(None, paths.default_resume, paths.default_profile, paths, now=START,
        fetcher=ScriptedFetcher(boards(board(job(1)))), clock=clock)
    clock.now = 0.0
    outcome = run(None, paths.default_resume, paths.default_profile, paths, now=START.replace(second=1),
                  fetcher=ScriptedFetcher(second, clock, step), ask=ask, clock=clock, use_claude=True)
    return outcome, json.loads((outcome.folder / "verdicts.json").read_text())


def claude_by(doc) -> dict:
    return {(v["board"], v["posting_id"]): v for v in doc["verdicts"] if v["judge"] == "claude"}


def test_every_new_posting_is_sent_in_board_order_whatever_the_rule_said(paths):
    fake = FakeClaude()
    second = boards(board(job(1), job(2, **GOOD), job(3, **SENIOR), job(4, **GOOD)),
                    board(job(1), job(7, **GOOD), job(8, **GOOD)))
    outcome, doc = two_runs(paths, second, fake)
    assert fake.sent == [2, 3, 4, 7, 8]                    # 3 is cut by the rule (senior) and still sent
    assert by_id(doc)[3]["verdict"] == "not_relevant"     # Claude's answer never changes the rule's
    assert outcome.exit == exits.FINISHED                 # every fake board ok; Claude had budget for all 5


def test_the_31st_new_posting_is_not_sent_and_the_exit_says_claude_calls(paths):
    fake = FakeClaude()
    second = boards(board(job(1), *[job(i, **GOOD) for i in range(2, 33)]))   # 31 new postings
    outcome, doc = two_runs(paths, second, fake)
    assert fake.sent == list(range(2, 32))                                    # 30 calls
    c = claude_by(doc)[("stripe", 32)]
    assert (c["status"], c["error_code"]) == ("error", "304")
    assert by_id(doc)[32]["verdict"] == "relevant"                            # the rule verdict stands
    assert outcome.exit == exits.BUDGET_EXHAUSTED and "claude calls" in doc["exit_reason"]


def test_300_seconds_are_shared_by_all_calls(paths):
    """Each call takes 120 s: 0 -> 120 -> 240 -> 360. The third starts with 60 s left (it may be
    cut short, D20 (4)); after it no Claude time is left, so the fourth and fifth are not sent (304):
    every posting the budget never reached is reported, not only the first one."""
    clock = Clock()
    second = boards(board(job(1), *[job(i, **GOOD) for i in (2, 3, 4, 5, 6)]))
    outcome, doc = two_runs(paths, second, SlowClaude(clock, 120.0), clock=clock)
    c = claude_by(doc)
    assert [c[("stripe", i)]["status"] for i in (2, 3, 4)] == ["ok", "ok", "ok"]
    assert [c[("stripe", i)]["error_code"] for i in (5, 6)] == ["304", "304"]
    assert outcome.exit == exits.BUDGET_EXHAUSTED and "claude seconds" in doc["exit_reason"]


def test_each_calls_timeout_is_the_claude_time_left():
    clock = Clock()
    b = Budget(clock=clock)
    assert b.start_claude() == 300.0
    clock.now += 120.0
    b.end_claude(120.0)
    assert b.start_claude() == 180.0
    clock.now += 280.0                                  # run at 400 s: only 20 s before the 60 s reserve of 480
    b.end_claude(10.0)                                  # (Claude time left alone would be 170 s)
    assert b.claude_seconds_left() == 20.0
    clock.now += 20.0
    assert b.stops_claude() == "claude seconds"         # the record must still be written in time


@pytest.mark.parametrize("ask, code", [
    (FakeClaude(lambda p: (_ for _ in ()).throw(ClaudeCallError("timed out", timed_out=True))), "301"),
    (FakeClaude(lambda p: (_ for _ in ()).throw(ClaudeCallError("HTTP 529"))), "302"),
    (FakeClaude(lambda p: "This job looks great!"), "303"),
    (FakeClaude(stop_reason="max_tokens"), "303"),
])
def test_a_failed_call_is_that_postings_error_only(paths, ask, code):
    outcome, doc = two_runs(paths, boards(board(job(1), job(2, **GOOD))), ask)
    c = claude_by(doc)[("stripe", 2)]
    assert (c["status"], c["error_code"]) == ("error", code)
    assert by_id(doc)[2]["verdict"] == "relevant"
    assert outcome.exit == exits.FINISHED      # every board ok; a Claude failure doesn't change the run's exit


def test_each_claude_call_is_in_the_trace(paths):
    outcome, _ = two_runs(paths, boards(board(job(1), job(2, **GOOD)), board(job(1), job(7, **GOOD))), FakeClaude())
    rows = [json.loads(l) for l in (outcome.folder / "trace.jsonl").read_text().splitlines()]
    calls = [(r["board"], r["posting_id"], r["code"]) for r in rows if r["event"] == "claude_call"]
    assert calls == [("stripe", 2, None), ("cloudflare", 7, None)]
    assert rows[-1]["budget"]["claude_calls_used"] == 2


def test_summary_says_off_or_not_sent_budget(paths):
    second = boards(board(job(1), *[job(i, **GOOD) for i in range(2, 33)]))
    outcome, _ = two_runs(paths, second, FakeClaude())
    assert "| 32 | " in outcome.summary and "| not sent: budget |" in outcome.summary
    assert "| not sent: Claude budget used up | — | 1 |" in outcome.summary
    assert "| error | 0 | 0 |" in outcome.summary        # an unsent posting is not a Claude error
    assert "calls 30/30" in outcome.summary
    off = run(None, paths.default_resume, paths.default_profile, paths, now=START.replace(second=2),
              fetcher=ScriptedFetcher(boards(board(job(1), job(2, **GOOD), job(99, **GOOD)))), clock=Clock())   # 99: new after ids 2-32
    assert "Claude judge: off" in off.summary and "| off |" in off.summary


def test_summary_seconds_use_the_run_limit_that_applies(paths):
    """With Claude on, the run's limit is 480 s, not the 120 s board phase: a 129 s run read
    "129.1/120" and looked over budget (found in the Step 6 run 2026-11-08T234257Z)."""
    clock = Clock()
    second = boards(board(job(1), *[job(i, **GOOD) for i in (2, 3)]))
    on, _ = two_runs(paths, second, SlowClaude(clock, 70.0), clock=clock)
    assert "seconds 140.0/480" in on.summary and "/120" not in on.summary.splitlines()[1]
    assert "calls 2/30 · 140.0/300 s" in on.summary
    off = run(None, paths.default_resume, paths.default_profile, paths, now=START.replace(second=2),
              fetcher=ScriptedFetcher(boards(board(job(1)))), clock=Clock())
    assert "seconds 0.0/120" in off.summary


def test_with_claude_off_no_prompt_is_needed(paths):
    """Off means the prompt file is not even read (GATE §5: prompts/ only with Claude on)."""
    run(None, paths.default_resume, paths.default_profile, paths, now=START,
        fetcher=ScriptedFetcher(boards(board(job(1)))), prompt_name="no_such_prompt", clock=Clock())


def test_the_real_line_gets_the_300_second_limit(paths, monkeypatch):
    seen = {}
    def fake_make_ask(policy=None, timeout_s=None):
        seen["timeout_s"] = timeout_s
        return FakeClaude()
    monkeypatch.setattr(claude_cli, "make_ask", fake_make_ask)
    two_runs(paths, boards(board(job(1), job(2, **GOOD))), ask=None)
    assert seen == {"timeout_s": 300.0}


def test_each_real_call_is_built_with_the_claude_time_left(paths, monkeypatch):
    """D20 (4): the real line gets the time left at each call (300, 180, 60), not 300 every time,
    so three 120 s calls can't run to 360 s."""
    clock, timeouts = Clock(), []
    def fake_make_ask(policy=None, timeout_s=None):
        timeouts.append(timeout_s)
        return SlowClaude(clock, 120.0)
    monkeypatch.setattr(claude_cli, "make_ask", fake_make_ask)
    two_runs(paths, boards(board(job(1), *[job(i, **GOOD) for i in (2, 3, 4)])), ask=None, clock=clock)
    assert timeouts == [300.0, 180.0, 60.0]


def test_api_line_uses_the_call_limit_and_no_sdk_retries(monkeypatch, policy):
    """GATE §4: a failed Claude evaluation is not retried; SDK retries would also outlast 300 s."""
    made = {}
    fake_sdk = types.SimpleNamespace(Anthropic=lambda **kw: made.update(kw) or types.SimpleNamespace(base_url=kw["base_url"]))
    monkeypatch.setitem(sys.modules, "anthropic", fake_sdk)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    claude_api.make_ask(policy, timeout_s=300.0)
    assert (made["timeout"], made["max_retries"]) == (300.0, 0)


def test_cli_flag_turns_claude_on(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(cli, "run", lambda *a, **k: seen.append(k["use_claude"]) or RunOutcome(tmp_path, "", "finished"))
    cli.main([], paths=Paths(out=tmp_path))
    cli.main(["--claude"], paths=Paths(out=tmp_path))
    assert seen == [False, True]


@pytest.mark.parametrize("use_claude, expected", [(False, None), (True, "cli")])
def test_the_run_policy_opens_claude_paths_only_when_claude_is_on(paths, monkeypatch, use_claude, expected):
    """GATE §5: prompts/ (and, with --claude-via api, api.anthropic.com) only when Claude is on."""
    from job_agent import pipeline
    seen = []
    real = pipeline.Policy.for_run
    monkeypatch.setattr(pipeline.Policy, "for_run", lambda p, claude_via=None, confirm=None: seen.append(claude_via) or real(p, claude_via, confirm))
    run(None, paths.default_resume, paths.default_profile, paths, now=START,
        fetcher=ScriptedFetcher(boards(board(job(1)))), ask=FakeClaude(), clock=Clock(), use_claude=use_claude)
    assert seen == [expected]
