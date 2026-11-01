"""The Claude judge around the validator: what happens when Claude can't run, stops early, or is capped.

CONTRACT In says a missing key makes the Claude judge report an error while the rule judge carries
on; D14 says the test cap must be visible in every capped run. Both are easy to break silently
(a run that "just has fewer Claude verdicts"), so each gets a test. All use a fake Claude.
"""

import json

import pytest
from fakes import GOOD, FakeClaude, START, board, by_id, job, run_once

from job_agent import pipeline
from job_agent.common.errors import ClaudeCallError, InputError, WatchError
from job_agent.common.posting import Posting
from job_agent.judges import claude, claude_api
from job_agent.pipeline import run

PROMPT = claude.Prompt("test", "judge this")


def _new_run(paths, *jobs, ask=None):
    run_once(paths, board(job(1)), n=0)
    return run_once(paths, board(job(1), *jobs), n=1, ask=ask)


@pytest.mark.parametrize("via, message", [
    ("cli", "claude CLI not found: install Claude Code and log in, or use --claude-via api"),
    ("api", "ANTHROPIC_API_KEY is not set; Claude judge did not run"),
])
def test_no_claude_gives_claude_errors_but_rule_verdicts_still_count(paths, via, message):
    """conftest makes both lines unavailable; the run must still finish with the rule's verdicts."""
    run("stripe", paths.default_resume, paths.default_profile, paths, now=START,
        fetcher=lambda url: (board(job(1)), ""), via=via)
    outcome = run("stripe", paths.default_resume, paths.default_profile, paths, now=START.replace(second=1),
                  fetcher=lambda url: (board(job(1), job(2, **GOOD)), ""), via=via)   # no ask: the real line
    doc = json.loads((outcome.folder / "verdicts.json").read_text())
    assert by_id(doc)[2]["verdict"] == "relevant"
    c = by_id(doc, "claude")[2]
    assert (c["status"], c["error_message"]) == ("error", message)


def test_unknown_claude_line_stops_before_fetching(paths):
    fetched = []
    with pytest.raises(InputError, match="--claude-via"):
        run("stripe", paths.default_resume, paths.default_profile, paths, now=START,
            fetcher=lambda url: fetched.append(url), via="carrier-pigeon")
    assert fetched == []


def test_make_ask_without_a_key_raises():
    with pytest.raises(ClaudeCallError, match="ANTHROPIC_API_KEY"):
        claude_api.make_ask()


def test_make_ask_refuses_a_host_off_the_allow_list(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    with pytest.raises(WatchError, match="not on allow-list"):
        claude_api.make_ask(base_url="https://evil.example.com")


@pytest.mark.parametrize("stop", ["refusal", "max_tokens"])
def test_a_refused_or_cut_off_reply_is_an_error(criteria, stop):
    posting = Posting(5, GOOD["title"], GOOD["location"], GOOD["content"])
    v = claude.judge(posting, criteria, FakeClaude(stop_reason=stop), PROMPT).verdict
    assert v["status"] == "error" and stop in v["error_message"]


def test_failed_call_is_an_error_for_that_posting_only(criteria):
    def broken(system, user):
        raise ClaudeCallError("Claude API error HTTP 529: overloaded")
    v = claude.judge(Posting(5, GOOD["title"], GOOD["location"], GOOD["content"]), criteria, broken, PROMPT).verdict
    assert (v["status"], v["error_message"]) == ("error", "Claude API error HTTP 529: overloaded")


def test_empty_jd_is_not_sent_to_claude(criteria):
    fake = FakeClaude()
    v = claude.judge(Posting(5, GOOD["title"], GOOD["location"], "<p></p>"), criteria, fake, PROMPT).verdict
    assert v["status"] == "error" and fake.sent == []


def test_claude_sees_posting_resume_and_profile_without_html(criteria):
    seen = {}
    def spy(system, user):
        seen.update(json.loads(user))
        return FakeClaude()(system, user)
    claude.judge(Posting(5, GOOD["title"], GOOD["location"], GOOD["content"]), criteria, spy, PROMPT)
    assert set(seen) == {"posting", "resume", "profile"}
    assert "<p>" not in seen["posting"]["content"] and "Java" in seen["posting"]["content"]
    assert seen["resume"]["basics"]["email"].endswith("@example.com")


def test_every_new_posting_is_sent_to_claude(paths):
    """R18: no cap. Each new posting gets a Claude verdict, not only the first few (D14 cap removed)."""
    fake = FakeClaude()
    doc = _new_run(paths, job(2, **GOOD), job(3, **GOOD), job(4, **GOOD), ask=fake)
    assert fake.sent == [2, 3, 4]
    assert [by_id(doc, "claude")[i]["status"] for i in (2, 3, 4)] == ["ok", "ok", "ok"]


def test_raw_claude_replies_are_saved_even_when_rejected(paths):
    doc = _new_run(paths, job(2, **GOOD), ask=FakeClaude(lambda p: "This job looks like a good fit!"))
    assert by_id(doc, "claude")[2]["status"] == "error"
    raw = [json.loads(l) for l in (paths.run("2026-10-31T120001Z") / "claude_raw.jsonl").read_text().splitlines()]
    assert raw[0]["posting_id"] == 2 and raw[0]["text"] == "This job looks like a good fit!"


def test_missing_prompt_file_stops_before_fetching(paths):
    fetched = []
    with pytest.raises(InputError, match="prompt file not found"):
        run("stripe", paths.default_resume, paths.default_profile, paths, now=START,
            fetcher=lambda url: fetched.append(url), prompt_name="no_such_prompt")
    assert fetched == []


def test_shipped_prompt_file_exists(paths):
    assert paths.prompt(pipeline.DEFAULT_PROMPT).exists()
