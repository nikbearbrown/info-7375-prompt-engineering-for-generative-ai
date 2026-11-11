"""Unit tests for the claude-cli judge backend (Amendment A14). Written by Claude Code on 2026-10-30. A fake subprocess runner stands in for `claude`; no real CLI call is made, and the ANTHROPIC_API_KEY set here is a fake value used only to check that it is removed."""
import json
import os
import re
import subprocess
from datetime import timedelta
from pathlib import Path

import pytest

from conftest import BOARD_URL, FIXED_NOW, FakeOpener, board_body, job, latest_report, run_args, run_cli
from jobwatch import judge_cli
from jobwatch.cli import build_parser
from test_experiment import exp_args, git, setup, target  # noqa: F401  (setup is a fixture)

PROMPT = "## System\nJudge.\n## User\nID={{POSTING_ID}}\n{{RESUME_JSON}}\n{{POSTING_JSON}}\n"
TITLE = "Machine Learning Engineer, Radar"
VERSION = "2.1.314 (Claude Code)"


def answer(pid, verdict="relevant", reason="constructed"):
    return json.dumps({"posting_id": pid, "verdict": verdict, "reason": reason, "citations": [
        {"source": "resume", "path": "/targets/roles/0", "value": "Machine Learning Engineer"},
        {"source": "posting", "path": "/title", "value": "Machine Learning Engineer"},
    ]})


def envelope(result, is_error=False, model="claude-sonnet-5-5"):
    return json.dumps({"type": "result", "subtype": "success", "is_error": is_error, "result": result,
                       "session_id": "sess-1", "usage": {"input_tokens": 10, "output_tokens": 20},
                       "modelUsage": {model: {"inputTokens": 10}}})


def ok(pid):
    return 0, envelope(answer(pid)), ""


class FakeRunner:
    """Replaces subprocess.run. `behaviour(pid) -> (exit code, stdout, stderr)`, or it raises."""

    def __init__(self, behaviour=ok):
        self.behaviour = behaviour
        self.calls = []

    def __call__(self, argv, input=None, capture_output=None, text=None, timeout=None, cwd=None, env=None):
        if argv[1:] == ["--version"]:
            return subprocess.CompletedProcess(argv, 0, VERSION + "\n", "")
        self.calls.append({"argv": argv, "input": input, "timeout": timeout, "cwd": cwd,
                           "cwd_listing": os.listdir(cwd), "env": env})
        pid = re.search(r"ID=(\d+)", input).group(1)
        code, stdout, stderr = self.behaviour(pid)
        return subprocess.CompletedProcess(argv, code, stdout, stderr)


@pytest.fixture
def runner(monkeypatch):
    fake = FakeRunner()
    monkeypatch.setattr(judge_cli, "run_subprocess", fake)
    monkeypatch.setattr(judge_cli, "which", lambda name: "/fake/bin/claude" if name == "claude" else None)
    return fake


def _seeded(workdir, jobs, extra=()):
    """A baseline, then a seeded claude-cli run on `jobs`; returns its exit code."""
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (200, board_body([]), {})})) == 0
    (workdir / "p.md").write_text(PROMPT, encoding="utf-8")
    (workdir / "saved.raw").write_bytes(board_body(jobs))
    argv = run_args(extra=("--from-file", "saved.raw", "--prompt", "p.md", "--judge", "claude-cli", *extra))
    return run_cli(argv, now=FIXED_NOW + timedelta(minutes=1))


def test_judge_defaults_to_sdk_everywhere():
    parser = build_parser()
    assert parser.parse_args(["run", "--board", "b", "--resume", "r"]).judge == "sdk"
    assert parser.parse_args(["sample", "--run", "d", "--posting-id", "1", "--resume", "r", "--prompt", "p"]).judge == "sdk"
    assert parser.parse_args(["experiment", "--set", "development", "--run", "d", "--resume", "r",
                              "--prompt-a", "p"]).judge == "sdk"


def test_a_call_replaces_the_system_prompt_has_no_tools_and_runs_in_an_empty_dir_without_the_key(
        workdir, runner, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    assert _seeded(workdir, [job(1, TITLE)]) == 0
    (call,) = runner.calls
    assert call["argv"] == ["claude", "-p", "--output-format", "json", "--system-prompt", "Judge.", "--tools", "",
                            "--strict-mcp-config", "--safe-mode", "--disable-slash-commands",
                            "--no-session-persistence", "--model", "claude-sonnet-5-5"]
    assert "--append-system-prompt" not in call["argv"]
    assert call["input"].startswith("ID=1\n") and call["timeout"] == 120
    assert call["cwd_listing"] == [] and not Path(call["cwd"]).exists()
    assert Path(workdir).resolve() not in Path(call["cwd"]).resolve().parents
    assert "ANTHROPIC_API_KEY" not in call["env"]

    run_dir = sorted((workdir / "evidence" / "runs").iterdir())[-1]
    request = json.loads((run_dir / "claude" / "1.request.json").read_text())
    assert request["backend"] == "claude-cli" and request["argv"] == call["argv"] and request["stdin"] == call["input"]
    assert (run_dir / "claude" / "1.response.txt").read_text() == envelope(answer("1"))
    meta = json.loads((run_dir / "claude" / "1.response.meta.json").read_text())
    assert meta["cli_version"] == VERSION and meta["model"] == ["claude-sonnet-5-5"]
    assert meta["session_id"] == "sess-1" and meta["usage"]["output_tokens"] == 20
    assert meta["exit_code"] == 0 and meta["error"] is None
    report = latest_report(workdir)
    assert report["judge"]["backend"] == "claude-cli" and report["judge"]["status"] == "run"
    judgment = report["records"][0]["judgment"]
    assert judgment["status"] == "accepted" and judgment["model"] == "claude-sonnet-5-5"
    assert json.loads((run_dir / "manifest.json").read_text())["judge_backend"] == "claude-cli"
    assert "judge: run (backend claude-cli, model claude-sonnet-5-5" in (run_dir / "report.txt").read_text()
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert run_cli(["replay", run_dir.as_posix()]) == 0


def test_no_claude_on_path_means_not_run_and_no_prompt_is_needed(workdir, runner, monkeypatch):
    monkeypatch.setattr(judge_cli, "which", lambda name: None)
    assert _seeded(workdir, [job(1, TITLE)], extra=("--prompt", "missing.md")) == 0
    report = latest_report(workdir)
    assert report["judge"]["status"] == "not_run"
    assert report["records"][0]["judgment"]["reason"] == "claude_cli_not_found"
    assert runner.calls == []


def _raise_timeout(pid):
    raise subprocess.TimeoutExpired(["claude"], 120, output=b"partial")


@pytest.mark.parametrize("behaviour, reason", [
    (lambda pid: (1, "", "boom"), "cli_nonzero_exit"),
    (_raise_timeout, "cli_timeout"),
    (lambda pid: (1, envelope("Claude AI usage limit reached|1761868800", is_error=True), ""), "cli_usage_limit"),
    (lambda pid: (0, envelope("You've hit your limit · resets 9pm"), ""), "cli_usage_limit"),
    (lambda pid: (0, envelope("something failed", is_error=True), ""), "cli_error_result"),
    (lambda pid: (0, "not json", ""), "cli_bad_output"),
])
def test_a_failed_call_stops_the_judge_and_the_run_finishes_with_exit_1(workdir, runner, capsys, behaviour, reason):
    runner.behaviour = behaviour
    assert _seeded(workdir, [job(i, TITLE) for i in (1, 2, 3)]) == 1
    assert len(runner.calls) == 1
    report = latest_report(workdir)
    judgments = [r["judgment"] for r in report["records"]]
    assert (judgments[0]["status"], judgments[0]["reason"]) == ("error", reason)
    assert [(j["status"], j["reason"]) for j in judgments[1:]] == [("not_run", "judge_stopped")] * 2
    state = json.loads((workdir / "state" / "acme.json").read_text())
    assert state["seen_ids"] == ["1", "2", "3"]
    assert f"judge stopped: {reason} on posting 1" in capsys.readouterr().err
    run_dir = sorted((workdir / "evidence" / "runs").iterdir())[-1]
    meta = json.loads((run_dir / "claude" / "1.response.meta.json").read_text())
    assert meta["error"] == reason
    assert run_cli(["replay", run_dir.as_posix()]) == 0


def test_limit_words_inside_a_valid_answer_are_not_a_usage_limit(workdir, runner):
    runner.behaviour = lambda pid: (0, envelope(answer(pid, reason="mentions a usage limit reached")), "")
    assert _seeded(workdir, [job(1, TITLE)]) == 0
    assert latest_report(workdir)["records"][0]["judgment"]["status"] == "accepted"


def test_sample_stops_cleanly_with_an_incomplete_results_json(workdir, runner, capsys):
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (200, board_body([job(11, TITLE), job(12, TITLE)]), {})})) == 0
    (workdir / "p.md").write_text(PROMPT, encoding="utf-8")
    (run_dir,) = (workdir / "evidence" / "runs").iterdir()
    calls = iter([ok("11"), (1, "", "boom")])
    runner.behaviour = lambda pid: next(calls)
    argv = ["sample", "--run", run_dir.relative_to(workdir).as_posix(), "--posting-id", "11", "12",
            "--resume", "examples/persona_resume.json", "--prompt", "p.md", "--judge", "claude-cli"]
    assert run_cli(argv) == 1
    assert len(runner.calls) == 2
    results = json.loads(next((workdir / "evidence" / "sampling").iterdir()).joinpath("results.json").read_text())
    assert results["complete"] is False and results["judge_backend"] == "claude-cli"
    assert results["stopped"] == {"posting_id": "11", "reason": "cli_nonzero_exit"}
    assert [c["status"] for c in results["calls"]] == ["accepted", "error"]


def test_a_stopped_development_experiment_resumes_only_the_missing_postings(workdir, setup, runner):  # noqa: F811
    runner.behaviour = lambda pid: (1, envelope("usage limit reached", is_error=True), "") if pid == "23" else ok(pid)
    argv = exp_args(setup, extra=("--judge", "claude-cli"))
    assert run_cli(argv) == 1
    a_dir = target(workdir, "development", "prompts/a.md")
    first = json.loads((a_dir / "results.json").read_text())
    assert first["complete"] is False and first["counts"] is None and first["pass_rate"] is None
    assert first["stopped"] == {"posting_id": "23", "reason": "cli_usage_limit"}
    assert [r["posting_id"] for r in first["postings"]] == ["21", "22", "23"]

    runner.behaviour = ok
    runner.calls.clear()
    assert run_cli(argv) == 0
    assert [re.search(r"ID=(\d+)", c["input"]).group(1) for c in runner.calls] == ["23", "24"]
    again = json.loads((a_dir / "results.json").read_text())
    assert again["complete"] is True and again["created_at"] == first["created_at"]
    assert again["counts"] == {"accepted_correct": 2, "accepted_wrong": 1, "rejected": 1, "error": 0}
    kept = list((a_dir / "claude" / "previous").iterdir())
    assert len(kept) == 1 and (kept[0] / "23.response.meta.json").is_file()
    runner.calls.clear()
    assert run_cli(argv) == 0 and runner.calls == []


def test_a_stopped_held_out_run_resumes_once_and_only_with_the_same_pair(workdir, setup, runner):  # noqa: F811
    (workdir / "prompts" / "c.md").write_text(PROMPT.replace("Judge.", "C"), encoding="utf-8")
    git(workdir, "init", "-q")
    git(workdir, "add", "prompts/")
    git(workdir, "commit", "-q", "-m", "prompts")

    def b_fails_on_25(pid):
        b_called = any(c["argv"][5] == "B" for c in runner.calls)
        return (1, "", "boom") if pid == "25" and b_called else ok(pid)

    runner.behaviour = b_fails_on_25
    argv = exp_args(setup, "held-out", b="prompts/b.md", extra=("--judge", "claude-cli"))
    assert run_cli(argv) == 1
    assert [(c["argv"][5], re.search(r"ID=(\d+)", c["input"]).group(1)) for c in runner.calls] == [
        ("A", "25"), ("A", "26"), ("B", "25")]
    assert json.loads((target(workdir, "held-out", "prompts/a.md") / "results.json").read_text())["complete"] is True
    assert json.loads((target(workdir, "held-out", "prompts/b.md") / "results.json").read_text())["complete"] is False
    swapped = exp_args(setup, "held-out", b="prompts/c.md", extra=("--judge", "claude-cli"))
    runner.calls.clear()
    assert run_cli(swapped) == 2 and runner.calls == []
    runner.behaviour = ok
    assert run_cli(argv) == 0
    assert [(c["argv"][5], re.search(r"ID=(\d+)", c["input"]).group(1)) for c in runner.calls] == [("B", "26")]
    assert run_cli(argv) == 2
    assert len(runner.calls) == 1


def test_a_held_out_posting_with_a_saved_call_is_never_sent_again(workdir, setup, runner):  # noqa: F811
    """Even an error (here a timeout, after the prompt reached the CLI) is kept, not re-sent (A15)."""
    git(workdir, "init", "-q")
    git(workdir, "add", "prompts/")
    git(workdir, "commit", "-q", "-m", "prompts")
    runner.behaviour = lambda pid: _raise_timeout(pid) if pid == "26" else ok(pid)
    argv = exp_args(setup, "held-out", b="prompts/b.md", extra=("--judge", "claude-cli"))
    assert run_cli(argv) == 1
    runner.behaviour = ok
    assert run_cli(argv) == 0
    sent = [(c["argv"][5], re.search(r"ID=(\d+)", c["input"]).group(1)) for c in runner.calls]
    assert sent == [("A", "25"), ("A", "26"), ("B", "25"), ("B", "26")]
    assert len(sent) == len(set(sent))
    a = json.loads((target(workdir, "held-out", "prompts/a.md") / "results.json").read_text())
    assert a["complete"] is True and a["counts"]["error"] == 1
    assert [(r["posting_id"], r["status"], r["reason"]) for r in a["postings"]][1] == ("26", "error", "cli_timeout")
    assert not (target(workdir, "held-out", "prompts/a.md") / "claude" / "previous").exists()
