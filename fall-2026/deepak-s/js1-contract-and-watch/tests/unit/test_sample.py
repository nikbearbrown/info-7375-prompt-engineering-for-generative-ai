"""Unit tests for `sample` (CONTRACT.md Interfaces › sample, Amendments A7, A8, A13). Written by Claude Code on 2026-10-30. All postings and responses are constructed; fake client only."""
import json
import re

import pytest

from conftest import BOARD_URL, FakeClient, FakeOpener, board_body, job, run_args, run_cli

PROMPT = "## System\nS\n## User\nID={{POSTING_ID}}\n{{RESUME_JSON}}\n{{POSTING_JSON}}\n"
TITLE = "Machine Learning Engineer, Radar"


def answer(kwargs):
    pid = re.search(r"ID=(\d+)", kwargs["messages"][0]["content"]).group(1)
    return json.dumps({"posting_id": pid, "verdict": "relevant", "reason": "constructed", "citations": [
        {"source": "resume", "path": "/targets/roles/0", "value": "Machine Learning Engineer"},
        {"source": "posting", "path": "/title", "value": "Machine Learning Engineer"},
    ]}), "end_turn"


@pytest.fixture
def saved_run(workdir, monkeypatch):
    """A baseline run whose raw response holds postings 11-13; a key and a prompt file."""
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (200, board_body([job(i, TITLE) for i in (11, 12, 13)]), {})})) == 0
    (workdir / "p.md").write_text(PROMPT, encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    (run_dir,) = (workdir / "evidence" / "runs").iterdir()
    return run_dir.relative_to(workdir).as_posix()


def sample_args(run_dir, ids=("11", "12"), extra=()):
    return ["sample", "--run", run_dir, "--posting-id", *ids, "--resume", "examples/persona_resume.json",
            "--prompt", "p.md", *extra]


def test_default_n_is_4_and_every_call_is_a_separate_single_message_request(workdir, saved_run, capsys):
    client = FakeClient(answer)
    assert run_cli(sample_args(saved_run), client=client) == 0
    assert len(client.calls) == 8
    for call in client.calls:
        assert [m["role"] for m in call["messages"]] == ["user"]
        assert call["temperature"] == 1.0 and call["max_tokens"] == 600 and "tools" not in call
    assert len({id(c["messages"]) for c in client.calls}) == 8
    out_dir = workdir / "evidence" / "sampling" / "20261029T180000Z"
    for pid in ("11", "12"):
        for k in range(1, 5):
            for suffix in ("request.json", "response.txt", "response.meta.json", "validation.json"):
                assert (out_dir / "claude" / f"{pid}.{k}.{suffix}").is_file()
    results = json.loads((out_dir / "results.json").read_text())
    assert results["kind"] == "sample" and results["n"] == 4 and results["posting_ids"] == ["11", "12"]
    assert results["run_dir"] == saved_run and results["prompt_path"] == "p.md"
    assert results["per_posting"]["11"] == {"status": {"accepted": 4}, "verdict": {"relevant": 4}}
    assert [(c["posting_id"], c["k"]) for c in results["calls"]][:5] == [("11", 1), ("11", 2), ("11", 3), ("11", 4), ("12", 1)]
    validation = json.loads((out_dir / "claude" / "12.3.validation.json").read_text())
    assert validation["status"] == "accepted" and validation["raw_path"].endswith("claude/12.3.response.txt")
    assert "written to evidence/sampling/20261029T180000Z/" in capsys.readouterr().out


def test_n_is_honoured_and_a_second_sample_gets_its_own_directory(workdir, saved_run):
    client = FakeClient(answer)
    assert run_cli(sample_args(saved_run, ids=("13",), extra=("--n", "2")), client=client) == 0
    assert run_cli(sample_args(saved_run, ids=("13",), extra=("--n", "2")), client=client) == 0
    assert len(client.calls) == 4
    assert sorted(p.name for p in (workdir / "evidence" / "sampling").iterdir()) == ["20261029T180000Z", "20261029T180000Z-2"]


@pytest.mark.parametrize("ids, extra", [
    (("99",), ()),           # not in the saved response
    (("11", "11"), ()),      # repeated id
    (("11",), ("--n", "0")),
])
def test_bad_ids_or_n_are_refused_before_any_call(workdir, saved_run, ids, extra):
    client = FakeClient(answer)
    assert run_cli(sample_args(saved_run, ids=ids, extra=extra), client=client) == 2
    assert client.calls == [] and not (workdir / "evidence" / "sampling").exists()


def test_no_key_is_refused(workdir, saved_run, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    client = FakeClient(answer)
    assert run_cli(sample_args(saved_run), client=client) == 2
    assert client.calls == []


def test_a_held_out_posting_is_refused_once_the_split_exists(workdir, saved_run):
    (workdir / "labels").mkdir()
    (workdir / "labels" / "split.json").write_text(json.dumps({"seed": 1, "development": ["11"], "held_out": ["12"]}))
    client = FakeClient(answer)
    assert run_cli(sample_args(saved_run, ids=("11", "12")), client=client) == 2
    assert client.calls == []
    assert run_cli(sample_args(saved_run, ids=("11",), extra=("--n", "1")), client=client) == 0
    assert len(client.calls) == 1


def test_a_raw_response_that_does_not_match_its_manifest_is_refused(workdir, saved_run):
    raw = next((workdir / "evidence" / "raw").iterdir())
    raw.write_bytes(raw.read_bytes() + b"\n")
    client = FakeClient(answer)
    assert run_cli(sample_args(saved_run), client=client) == 2
    assert client.calls == []
