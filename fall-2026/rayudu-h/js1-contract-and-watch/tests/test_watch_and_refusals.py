"""The watch and the refusals in CONTRACT.md. No network: fetches to other hosts are refused before any request."""
import copy
import gzip
import json

import pytest

from conftest import ROOT, board, posting
from jsagent import claude_judge, cli, resume as resume_mod, watch


def test_off_allow_list_hosts_are_refused():
    for url in ["https://evil.example.com/jobs", "http://boards-api.greenhouse.io/v1/boards/x/jobs",
                "https://job-boards.greenhouse.io/anthropic/jobs/1", "https://api.lever.co/v0/postings/x"]:
        with pytest.raises(watch.Refused):
            watch.fetch(url)


def test_board_token_cannot_smuggle_a_url():
    for bad in ["anthropic/../../x", "evil.com", "a?b", ""]:
        with pytest.raises(watch.Refused):
            watch.board_url(bad)
    assert watch.board_url("anthropic").startswith("https://boards-api.greenhouse.io/v1/boards/anthropic/")


def test_baseline_reports_none_as_new():
    jobs = [posting(1, "AI Engineer"), posting(2, "Data Analyst")]
    assert watch.new_postings(jobs, None) == []
    assert [j["id"] for j in watch.new_postings(jobs, {1})] == [2]


def test_raw_response_saved_exactly_and_never_overwritten(tmp_path):
    raw = board(posting(1, "AI Engineer"))
    meta = watch.save_raw(tmp_path, raw, {"source": "constructed"})
    assert gzip.decompress((tmp_path / "raw.json.gz").read_bytes()) == raw
    assert meta["raw_bytes"] == len(raw)
    with pytest.raises(watch.Refused):
        watch.save_raw(tmp_path, b"{}", {})


def test_non_board_json_is_a_fetch_failure():
    for raw in [b"<html>", b"{}", b'{"jobs": [{"title": "no id"}]}']:
        with pytest.raises(watch.FetchFailed):
            watch.parse_jobs(raw)


def test_failed_fetch_is_not_reported_as_nothing_new(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_bytes(b"not json")
    code = cli.main(["run", "--board", "anthropic", "--resume", str(ROOT / "persona" / "priya-nair.resume.json"),
                     "--state", str(tmp_path / "seen.json"), "--runs-dir", str(tmp_path / "runs"),
                     "--from-raw", str(bad), "--label", "constructed", "--no-claude"])
    assert code == 1
    assert "fetch failed" in capsys.readouterr().out
    assert not (tmp_path / "seen.json").exists()
    report = next((tmp_path / "runs").iterdir()) / "report.md"
    assert "fetch failed" in report.read_text()


def test_real_looking_resume_is_refused_and_state_not_advanced(tmp_path, resume):
    real = copy.deepcopy(resume)
    real["personal"]["email"] = "someone@gmail.com"
    path = tmp_path / "resume.json"
    path.write_text(json.dumps(real))
    raw = tmp_path / "r.json"
    raw.write_bytes(board(posting(1, "AI Engineer")))
    cli.main(["run", "--board", "x", "--resume", str(path), "--state", str(tmp_path / "seen.json"),
              "--runs-dir", str(tmp_path / "runs"), "--from-raw", str(raw), "--label", "constructed", "--no-claude"])
    assert not (tmp_path / "seen.json").exists()
    assert "example.com" in (next((tmp_path / "runs").iterdir()) / "report.md").read_text()


def test_persona_is_valid_and_judges_never_see_contact_fields(resume):
    assert resume_mod.validate(resume) == []
    view = json.dumps(resume_mod.judge_view(resume))
    for field in ["Priya", "example.com", "555", "linkedin", "github"]:
        assert field not in view
    prompt = claude_judge.build_prompt("v1", posting(1, "AI Engineer"), resume)
    for field in ["Priya", "example.com", "555", "linkedin"]:
        assert field not in prompt
