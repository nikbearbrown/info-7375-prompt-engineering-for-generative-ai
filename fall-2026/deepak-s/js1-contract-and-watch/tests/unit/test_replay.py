"""Unit tests for `replay` (CONTRACT.md Interfaces › replay, Amendment A9). Written by Claude Code on 2026-10-30. All postings and responses are constructed; no key, no network."""
import json
import re
from datetime import timedelta

from conftest import BOARD_URL, FIXED_NOW, FakeClient, FakeOpener, board_body, job, run_args, run_cli

PROMPT = "## System\nS\n## User\nID={{POSTING_ID}}\n{{RESUME_JSON}}\n{{POSTING_JSON}}\n"
TITLE = "Machine Learning Engineer, Radar"


def answer(pid, verdict="relevant"):
    return json.dumps({"posting_id": pid, "verdict": verdict, "reason": "constructed", "citations": [
        {"source": "resume", "path": "/targets/roles/0", "value": "Machine Learning Engineer"},
        {"source": "posting", "path": "/title", "value": "Machine Learning Engineer"},
    ]})


def responder(kwargs):
    pid = re.search(r"ID=(\d+)", kwargs["messages"][0]["content"]).group(1)
    if pid == "2":
        return "not json", "end_turn"
    if pid == "3":
        return answer(pid), "max_tokens"
    if pid == "4":
        raise TimeoutError("constructed failure")
    return answer(pid), "end_turn"


def _judged_run(workdir, monkeypatch):
    """A baseline, then a seeded run with a key: accepted, rejected, truncated and error judgments."""
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (200, board_body([]), {})})) == 0
    (workdir / "p.md").write_text(PROMPT, encoding="utf-8")
    (workdir / "saved.raw").write_bytes(board_body([job(i, TITLE) for i in (1, 2, 3, 4)] + [job(5, "Account Executive")]))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    later = FIXED_NOW + timedelta(minutes=1)
    assert run_cli(run_args(extra=("--from-file", "saved.raw", "--prompt", "p.md")),
                   client=FakeClient(responder), now=later) == 0
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    return sorted((workdir / "evidence" / "runs").iterdir())


def _tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_replay_rebuilds_a_judged_run_offline_and_writes_nothing(workdir, monkeypatch, capsys):
    baseline, seeded = _judged_run(workdir, monkeypatch)
    report = json.loads((seeded / "report.json").read_text())
    assert [r["judgment"]["status"] for r in report["records"]] == ["accepted", "rejected", "rejected", "error", "rejected"]
    capsys.readouterr()
    before = _tree(workdir)
    assert run_cli(["replay", seeded.relative_to(workdir).as_posix()]) == 0
    assert run_cli(["replay", baseline.relative_to(workdir).as_posix()]) == 0
    assert _tree(workdir) == before
    out = capsys.readouterr().out
    assert "error judgment(s) 4: reason and called_at taken from report.json" in out
    assert "5 record(s) rebuilt, 4 saved response(s) re-validated" in out
    assert out.count(": ok.") == 2 and "DIFFERENCE" not in out


def test_an_edited_response_is_a_difference(workdir, monkeypatch, capsys):
    _, seeded = _judged_run(workdir, monkeypatch)
    (seeded / "claude" / "1.response.txt").write_text(answer("1", "not_relevant"), encoding="utf-8")
    assert run_cli(["replay", seeded.as_posix()]) == 1
    assert "DIFFERENCE in counts, records[0].agreement, records[0].judgment, report.txt" in capsys.readouterr().out


def test_an_edited_report_is_a_difference(workdir, monkeypatch, capsys):
    _, seeded = _judged_run(workdir, monkeypatch)
    report = json.loads((seeded / "report.json").read_text())
    report["previously_seen_note"] = "added"
    report["records"][4]["record"]["verdict"] = "relevant"
    (seeded / "report.json").write_text(json.dumps(report), encoding="utf-8")
    assert run_cli(["replay", seeded.as_posix()]) == 1
    assert "DIFFERENCE in previously_seen_note, records[4].record" in capsys.readouterr().out


def test_sha256_mismatches_are_differences(workdir, monkeypatch, capsys):
    _, seeded = _judged_run(workdir, monkeypatch)
    raw = workdir / "evidence" / "raw" / f"{seeded.name}.raw"
    original = raw.read_bytes()
    raw.write_bytes(original + b" ")
    assert run_cli(["replay", seeded.as_posix()]) == 1
    assert "sha256 mismatch: evidence/raw/" in capsys.readouterr().out
    raw.write_bytes(original)
    (seeded / "state_before.json").write_bytes(b"{}")
    assert run_cli(["replay", seeded.as_posix()]) == 1
    assert "sha256 mismatch: state_before.json" in capsys.readouterr().out


def test_a_changed_prompt_or_request_is_a_difference(workdir, monkeypatch, capsys):
    _, seeded = _judged_run(workdir, monkeypatch)
    request = seeded / "claude" / "1.request.json"
    saved = request.read_bytes()
    request.write_text(json.dumps({**json.loads(saved), "temperature": 0.0}), encoding="utf-8")
    assert run_cli(["replay", seeded.as_posix()]) == 1
    assert "claude/1.request.json differs" in capsys.readouterr().out
    request.write_bytes(saved)
    (workdir / "p.md").write_text(PROMPT + "\n", encoding="utf-8")
    assert run_cli(["replay", seeded.as_posix()]) == 1
    assert "sha256 mismatch: p.md" in capsys.readouterr().out


def test_a_report_from_before_a1_is_compared_without_its_source_fields(workdir, capsys):
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (200, board_body([job(1, TITLE)]), {})})) == 0
    (run_dir,) = (workdir / "evidence" / "runs").iterdir()
    report = json.loads((run_dir / "report.json").read_text())
    for key in ("source", "from_file", "from_file_sha256"):
        del report[key]
    (run_dir / "report.json").write_text(json.dumps(report), encoding="utf-8")
    lines = (run_dir / "report.txt").read_text().splitlines(keepends=True)
    assert lines[1] == "source network\n"
    (run_dir / "report.txt").write_text("".join(lines[:1] + lines[2:]), encoding="utf-8")
    capsys.readouterr()
    assert run_cli(["replay", run_dir.as_posix()]) == 0
    out = capsys.readouterr().out.splitlines()
    assert sum("A1 fields (source, from_file, from_file_sha256) not compared" in line for line in out) == 1
    report["counts"]["unique"] = 9
    (run_dir / "report.json").write_text(json.dumps(report), encoding="utf-8")
    assert run_cli(["replay", run_dir.as_posix()]) == 1
    assert "DIFFERENCE in counts" in capsys.readouterr().out


def test_a_stopped_run_has_nothing_to_replay(workdir, capsys):
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (500, b"down", {})})) == 3
    (run_dir,) = (workdir / "evidence" / "runs").iterdir()
    assert run_cli(["replay", run_dir.as_posix()]) == 1
    assert "no report.json" in capsys.readouterr().out
    assert run_cli(["replay", "evidence/runs/missing"]) == 1
