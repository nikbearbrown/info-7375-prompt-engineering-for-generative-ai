"""JS2 Step 4: the permission policy's boundary tests (GATE §5, R22-R30).

test_gate_row_NN_* match rows 1-10 of GATE.md's boundary-test table, whose expected outcomes were
committed (614afb8) before this code existed (R30). test_extra_* are cases the table doesn't list but
the policy text implies (https only, Claude host only with --claude-via api, prompts/ only with
Claude on, JS2 D15 résumé path and evidence/raw/ overwrites). Each test that writes uses a temp folder;
none touches the network.
"""

import json
import os
import urllib.request

import pytest
from fakes import FakeFetcher, START, board, job

from job_agent import __main__ as cli
from job_agent.common import net, policy as policy_mod
from job_agent.common.paths import Paths, stamp
from job_agent.common.policy import Policy, PolicyError
from job_agent.pipeline import run

GH = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"


class Spy:
    """A confirm() that records every question and gives a fixed answer."""

    def __init__(self, answer: bool):
        self.answer, self.questions = answer, []

    def __call__(self, question: str) -> bool:
        self.questions.append(question)
        return self.answer


def _run(paths, confirm=policy_mod.refuse, fetcher=None, **kw):
    return run("stripe", kw.pop("resume", paths.default_resume), paths.default_profile, paths,
               now=START, fetcher=fetcher or FakeFetcher(board(job(1))), confirm=confirm, **kw)


# ---- GATE §5 table, rows 1-10 ------------------------------------------------------------------

def test_gate_row_01_host_off_the_allow_list_is_refused(policy):
    with pytest.raises(PolicyError, match="not on allow-list"):
        policy.check_url("https://api.lever.co/v0/postings/stripe")


def test_gate_row_02_dotdot_out_of_an_allowed_folder_is_refused(paths, policy):
    with pytest.raises(PolicyError, match="writing outside"):
        policy.check_write(paths.out / "runs" / ".." / "README.md")
    with pytest.raises(PolicyError, match="reading outside"):
        policy.check_read(paths.repo / "personas" / ".." / ".env")


def test_gate_row_03_sibling_folder_with_a_similar_name_is_refused(paths, policy):
    with pytest.raises(PolicyError, match="writing outside"):
        policy.check_write(paths.out / "runs-evil" / "summary.md")


def test_gate_row_04_symlink_inside_runs_pointing_outside_is_refused(paths, policy, tmp_path):
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (paths.out / "runs").mkdir(parents=True, exist_ok=True)
    os.symlink(outside, paths.out / "runs" / "link")
    with pytest.raises(PolicyError, match="writing outside"):
        policy.check_write(paths.out / "runs" / "link" / "summary.md")
    assert list(outside.iterdir()) == []


def test_gate_row_05_config_in_data_can_be_read_but_not_written(paths, policy):
    assert policy.check_read(paths.boards) == paths.boards.resolve()
    before = paths.boards.read_bytes()
    with pytest.raises(PolicyError, match="writing outside"):
        policy.check_write(paths.boards)
    assert paths.boards.read_bytes() == before


def test_gate_row_06_overwriting_a_report_asks_and_goes_ahead_on_yes(paths):
    _run(paths)                                           # the historical report at START
    spy = Spy(True)
    outcome = _run(paths, confirm=spy, fetcher=FakeFetcher(board(job(1), job(2))))
    assert len(spy.questions) == 2                        # runs/<stamp>/ and evidence/raw/<stamp>/, once each
    assert all(stamp(START) in q for q in spy.questions)  # the question names the destination
    assert json.loads((outcome.folder / "verdicts.json").read_text())["verdicts"]  # job 2 judged


def test_gate_row_07_stripe_on_greenhouse_is_allowed(policy):
    policy.check_url(GH)


def test_gate_row_08_new_report_under_runs_is_written_without_asking(paths):
    spy = Spy(False)
    outcome = _run(paths, confirm=spy)
    assert spy.questions == []
    assert (outcome.folder / "summary.md").exists()


def test_gate_row_09_redirect_to_a_host_off_the_list_is_not_followed(policy):
    handler = net._CheckedRedirects(policy)
    req = urllib.request.Request(GH)
    with pytest.raises(PolicyError, match="not on allow-list"):
        handler.redirect_request(req, None, 302, "Found", {}, "https://evil.example.com/jobs")
    # A redirect that stays on an allowed host is still followed.
    assert handler.redirect_request(req, None, 302, "Found", {}, GH + "&page=2").full_url == GH + "&page=2"


def test_gate_row_09_http_get_uses_the_checking_redirect_handler(policy, monkeypatch):
    """The handler above only matters if http_get installs it."""
    seen = []
    def fake_build_opener(*handlers):
        seen.extend(handlers)
        raise RuntimeError("stop before any connection")
    monkeypatch.setattr(urllib.request, "build_opener", fake_build_opener)
    with pytest.raises(RuntimeError):
        net.http_get(GH, policy)
    assert any(isinstance(h, net._CheckedRedirects) for h in seen)


def test_gate_row_10_answering_no_refuses_and_leaves_the_report_intact(paths):
    _run(paths)
    summary = paths.run(stamp(START)) / "summary.md"
    before = summary.read_text()
    fetcher = FakeFetcher(board(job(1), job(2)))
    with pytest.raises(PolicyError, match="not approved"):
        _run(paths, confirm=Spy(False), fetcher=fetcher)
    assert summary.read_text() == before
    assert fetcher.urls == []                             # asked before doing any work


# ---- Cases the table implies --------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "http://boards-api.greenhouse.io/v1/boards/stripe/jobs",      # not https
    "https://boards-api.greenhouse.io:8443/v1/boards/stripe/jobs",  # allowed host, other port
    "https://boards-api.greenhouse.io@evil.com/v1/boards/stripe/jobs",
    "https://user@boards-api.greenhouse.io/v1/boards/stripe/jobs",  # user part refused outright
])
def test_extra_allowed_host_in_the_wrong_form_is_refused(policy, url):
    with pytest.raises(PolicyError):
        policy.check_url(url)


@pytest.mark.parametrize("via, allowed", [(None, False), ("cli", False), ("api", True)])
def test_extra_claude_api_host_only_with_claude_via_api(paths, via, allowed):
    p = Policy.for_run(paths, claude_via=via)
    if allowed:
        p.check_url("https://api.anthropic.com/v1/messages")
    else:
        with pytest.raises(PolicyError):
            p.check_url("https://api.anthropic.com/v1/messages")


def test_extra_prompts_are_readable_only_with_claude_on(paths):
    prompt = paths.prompt("claude_judge.v1")
    Policy.for_run(paths, claude_via="cli").check_read(prompt)
    with pytest.raises(PolicyError, match="reading outside"):
        Policy.for_run(paths, claude_via=None).check_read(prompt)


def test_extra_resume_outside_the_allowed_folders_stops_before_fetching(paths, tmp_path):
    """JS2 D15: --resume must be under personas/ (or another read folder); my_resume/ is after JS2."""
    elsewhere = tmp_path / "my_resume" / "resume.json"
    elsewhere.parent.mkdir()
    elsewhere.write_bytes(paths.default_resume.read_bytes())
    fetcher = FakeFetcher(board(job(1)))
    with pytest.raises(PolicyError, match="reading outside"):
        _run(paths, fetcher=fetcher, resume=elsewhere)
    assert fetcher.urls == []


def test_extra_existing_raw_evidence_also_asks(paths, policy):
    """JS2 D15: evidence/raw/ is part of a run's record, like runs/."""
    raw = paths.raw(stamp(START))
    raw.mkdir(parents=True)
    with pytest.raises(PolicyError, match="not approved"):
        policy.check_write(raw)


def test_extra_state_file_is_updated_without_asking(paths):
    state = paths.state("stripe")
    state.parent.mkdir(parents=True)
    state.write_text("{}")
    p = Policy.for_run(paths, confirm=Spy(False))
    assert p.check_write(state) == state.resolve()


def test_extra_one_yes_covers_the_files_inside_that_folder(paths):
    folder = paths.run("x")
    (folder).mkdir(parents=True)
    (folder / "summary.md").write_text("old")
    spy = Spy(True)
    p = Policy.for_run(paths, confirm=spy)
    p.check_write(folder)
    p.check_write(folder / "summary.md")
    assert len(spy.questions) == 1


@pytest.mark.parametrize("typed, expected", [("y", True), ("Y", True), ("", False), ("yes", False), ("n", False)])
def test_extra_terminal_prompt_needs_an_explicit_y(monkeypatch, typed, expected):
    monkeypatch.setattr("builtins.input", lambda _: typed)
    assert policy_mod.ask_terminal("Overwrite?") is expected


def test_extra_terminal_prompt_with_no_input_is_a_no(monkeypatch):
    def eof(_):
        raise EOFError
    monkeypatch.setattr("builtins.input", eof)
    assert policy_mod.ask_terminal("Overwrite?") is False


def test_extra_cli_without_a_terminal_refuses_instead_of_asking(monkeypatch, tmp_path):
    """GATE §5: noninteractive input defaults to refusal, so a piped "y" can't approve an overwrite."""
    captured = {}
    def fake_run(*args, **kwargs):
        captured["confirm"] = kwargs["confirm"]
        raise PolicyError("stop")
    monkeypatch.setattr(cli, "run", fake_run)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert cli.main([], paths=Paths(out=tmp_path)) == 1
    assert captured["confirm"] is policy_mod.refuse


def test_extra_a_folder_this_run_created_is_not_asked_about_again(paths):
    """Found in Step 5a: board 1 creates evidence/raw/<stamp>/, board 2 writes into it. That is
    this run's own record, not a historical one, so it must not trigger the overwrite question."""
    spy = Spy(False)
    p = Policy.for_run(paths, confirm=spy)
    folder = p.check_write(paths.raw("x"))
    folder.mkdir(parents=True)
    p.check_write(paths.raw("x"))
    p.check_write(paths.raw("x") / "cloudflare_content.json")
    assert spy.questions == []
