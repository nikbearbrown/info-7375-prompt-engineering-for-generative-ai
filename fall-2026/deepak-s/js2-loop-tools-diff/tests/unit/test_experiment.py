"""Unit tests for `experiment` (CONTRACT.md Interfaces › experiment, Amendments A7, A8, A10-A12). Written by Claude Code on 2026-10-30. All postings, labels and responses are constructed; fake client only."""
import csv
import json
import re
import subprocess

import pytest

from conftest import BOARD_URL, FakeClient, FakeOpener, board_body, job, run_args, run_cli
from jobwatch.experiment import wilson
from jobwatch.prompt import load_prompt

PROMPT_A = "## System\nA\n## User\nID={{POSTING_ID}}\n{{RESUME_JSON}}\n{{POSTING_JSON}}\n"
PROMPT_B = "## System\nB\n## User\nID={{POSTING_ID}}\n{{RESUME_JSON}}\n{{POSTING_JSON}}\n"
JOBS = [
    job(21, "Machine Learning Engineer"),         # rule relevant, hand relevant
    job(22, "Machine Learning Engineer, Radar"),  # rule relevant, hand not_relevant
    job(23, "Account Executive"),                 # rule not_relevant, hand not_relevant
    job(24, "Staff Machine Learning Engineer"),   # rule not_relevant, hand relevant
    job(25, "Machine Learning Engineer, Link"),
    job(26, "Machine Learning Engineer, Payments"),
]
HAND = {"21": "relevant", "22": "not_relevant", "23": "not_relevant", "24": "relevant",
        "25": "relevant", "26": "not_relevant"}
SPLIT = {"seed": 7375, "development": ["21", "22", "23", "24"], "held_out": ["25", "26"]}


def responder(kwargs):
    """21 and 22 accepted as relevant; 23 not JSON; 24 an API failure; held-out accepted."""
    pid = re.search(r"ID=(\d+)", kwargs["messages"][0]["content"]).group(1)
    if pid == "23":
        return "not json", "end_turn"
    if pid == "24":
        raise TimeoutError("constructed failure")
    return json.dumps({"posting_id": pid, "verdict": "relevant", "reason": "constructed", "citations": [
        {"source": "resume", "path": "/targets/roles/0", "value": "Machine Learning Engineer"},
        {"source": "posting", "path": "/title", "value": "Machine Learning Engineer"},
    ]}), "end_turn"


@pytest.fixture
def setup(workdir, monkeypatch):
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (200, board_body(JOBS), {})})) == 0
    (run_dir,) = (workdir / "evidence" / "runs").iterdir()
    (workdir / "prompts" / "a.md").write_text(PROMPT_A, encoding="utf-8")
    (workdir / "prompts" / "b.md").write_text(PROMPT_B, encoding="utf-8")
    (workdir / "labels").mkdir()
    with open(workdir / "labels" / "labels.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["posting_id", "board", "title", "hand_label", "labeled_on", "note"])
        for j in JOBS:
            w.writerow([str(j["id"]), "acme", j["title"], HAND[str(j["id"])], "2026-10-30", "work"])
    (workdir / "labels" / "split.json").write_text(json.dumps(SPLIT), encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    return run_dir.relative_to(workdir).as_posix()


def exp_args(run_dir, set_="development", b=None, extra=()):
    argv = ["experiment", "--set", set_, "--run", run_dir, "--resume", "examples/persona_resume.json",
            "--prompt-a", "prompts/a.md"]
    return argv + (["--prompt-b", b] if b else []) + list(extra)


def target(workdir, set_, path):
    return workdir / "evidence" / "experiments" / set_ / load_prompt(workdir / path).sha256[:12]


def git(workdir, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *argv],
                   cwd=workdir, check=True, capture_output=True)


def test_wilson_matches_published_values():
    assert [round(x, 4) for x in wilson(5, 10)] == [0.2366, 0.7634]
    assert [round(x, 4) for x in wilson(0, 10)] == [0.0, 0.2775]
    assert [round(x, 4) for x in wilson(10, 10)] == [0.7225, 1.0]


def test_development_with_prompt_a_only_counts_each_outcome_separately(workdir, setup, capsys):
    client = FakeClient(responder)
    assert run_cli(exp_args(setup), client=client) == 0
    assert len(client.calls) == 4
    out_dir = target(workdir, "development", "prompts/a.md")
    results = json.loads((out_dir / "results.json").read_text())
    assert results["counts"] == {"accepted_correct": 1, "accepted_wrong": 1, "rejected": 1, "error": 1}
    assert results["n"] == 4 and results["pass_rate"] == 0.25 and results["wilson_95"] == wilson(1, 4)
    assert [r["outcome"] for r in results["postings"]] == ["accepted_correct", "accepted_wrong", "rejected", "error"]
    assert results["baseline_rule"]["counts"] == {"accepted_correct": 2, "accepted_wrong": 2, "rejected": 0, "error": 0}
    assert results["baseline_rule"]["pass_rate"] == 0.5
    assert results["run_dir"] == setup and results["posting_ids"] == SPLIT["development"]
    for suffix in ("request.json", "response.txt", "response.meta.json", "validation.json"):
        assert (out_dir / "claude" / f"21.{suffix}").is_file()
    assert (out_dir / "claude" / "24.request.json").is_file() and not (out_dir / "claude" / "24.response.txt").exists()
    out = capsys.readouterr().out
    assert "accepted_correct 1, accepted_wrong 1, rejected 1, error 1; pass rate 1/4 = 0.250" in out
    assert "rule (record, baseline): accepted_correct 2, accepted_wrong 2, rejected 0, error 0" in out


def test_development_reuses_saved_results_and_calls_only_the_new_prompt(workdir, setup, monkeypatch):
    assert run_cli(exp_args(setup), client=FakeClient(responder)) == 0
    a_dir = target(workdir, "development", "prompts/a.md")
    first = json.loads((a_dir / "results.json").read_text())
    client = FakeClient(responder)
    assert run_cli(exp_args(setup, b="prompts/b.md"), client=client) == 0
    assert len(client.calls) == 4 and all(c["system"] == "B" for c in client.calls)
    again = json.loads((a_dir / "results.json").read_text())
    assert again["created_at"] == first["created_at"] and "rescored_at" in again
    assert again["counts"] == first["counts"] and again["postings"] == first["postings"]
    assert (target(workdir, "development", "prompts/b.md") / "results.json").is_file()
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert run_cli(exp_args(setup, b="prompts/b.md"), client=FakeClient(responder)) == 0


def test_reuse_is_refused_when_the_saved_results_came_from_other_inputs(workdir, setup):
    assert run_cli(exp_args(setup), client=FakeClient(responder)) == 0
    client = FakeClient(responder)
    assert run_cli(exp_args(setup, extra=("--model", "claude-other")), client=client) == 2
    (target(workdir, "development", "prompts/b.md") / "claude").mkdir(parents=True)
    assert run_cli(exp_args(setup, b="prompts/b.md"), client=client) == 2
    assert client.calls == []


@pytest.mark.parametrize("b", [None, "prompts/a.md"])
def test_held_out_needs_two_different_prompts(workdir, setup, b):
    client = FakeClient(responder)
    assert run_cli(exp_args(setup, "held-out", b=b), client=client) == 2
    assert client.calls == []


def test_held_out_refuses_outside_git_or_with_uncommitted_prompts(workdir, setup):
    client = FakeClient(responder)
    assert run_cli(exp_args(setup, "held-out", b="prompts/b.md"), client=client) == 2
    git(workdir, "init", "-q")
    git(workdir, "add", "prompts/a.md")
    git(workdir, "commit", "-q", "-m", "a only")
    assert run_cli(exp_args(setup, "held-out", b="prompts/b.md"), client=client) == 2
    git(workdir, "add", "prompts/")
    git(workdir, "commit", "-q", "-m", "prompts")
    (workdir / "prompts" / "README.md").write_text("changed\n", encoding="utf-8")
    assert run_cli(exp_args(setup, "held-out", b="prompts/b.md"), client=client) == 2
    assert client.calls == [] and not (workdir / "evidence" / "experiments").exists()


def test_held_out_runs_once(workdir, setup):
    git(workdir, "init", "-q")
    git(workdir, "add", "prompts/")
    git(workdir, "commit", "-q", "-m", "prompts")
    client = FakeClient(responder)
    assert run_cli(exp_args(setup, "held-out", b="prompts/b.md"), client=client) == 0
    assert len(client.calls) == 4
    for path in ("prompts/a.md", "prompts/b.md"):
        results = json.loads((target(workdir, "held-out", path) / "results.json").read_text())
        assert results["set"] == "held-out" and results["posting_ids"] == SPLIT["held_out"]
        assert results["counts"] == {"accepted_correct": 1, "accepted_wrong": 1, "rejected": 0, "error": 0}
    assert run_cli(exp_args(setup, "held-out", b="prompts/b.md"), client=client) == 2
    assert len(client.calls) == 4


def test_missing_split_or_labels_are_refused(workdir, setup):
    client = FakeClient(responder)
    rows = (workdir / "labels" / "labels.csv").read_text().replace(",relevant,2026-10-30", ",,2026-10-30", 1)
    (workdir / "labels" / "labels.csv").write_text(rows, encoding="utf-8")
    assert run_cli(exp_args(setup), client=client) == 2
    (workdir / "labels" / "split.json").unlink()
    assert run_cli(exp_args(setup), client=client) == 2
    assert client.calls == []
