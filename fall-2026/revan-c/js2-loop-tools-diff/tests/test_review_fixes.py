"""Tests added after the author's review of the first implementation (2026-10-31).

Written AFTER the code they test. They check that rule evidence is true, not just
well-shaped, and that a failed output write leaves state untouched.
"""
import json
import pathlib

import pytest

from conftest import IRRELEVANT, RELEVANT, make_posting, write_board
from jsagent.rule import COUNTED_SKILL_CATEGORIES, judge_posting
from jsagent.run import RunError, run_once
from jsagent.text import contains_sequence, normalize, strip_html
from jsagent.validator import _posting_text, _resume_value_at, validate_claude_output

SNAPSHOT = (pathlib.Path(__file__).resolve().parent.parent
            / "evidence" / "klaviyo_2026-10-31_preimplementation_live.json")


def _cited_ok(resume, path, value):
    actual = _resume_value_at(resume, path)
    return value == actual or (isinstance(actual, list) and value in actual)


def _quoted_ok(posting, field, quote):
    return contains_sequence(normalize(_posting_text(posting, field)), normalize(quote))


def assert_evidence_true(resume, posting):
    for entry in judge_posting(resume, posting)["rule_justification"]:
        where = f"posting {posting['id']} {entry['condition']}"
        if entry["condition"] == "skills":
            fields, values, quotes = entry["resume_field"], entry["resume_value"], entry["posting_value"]
            assert len(fields) == len(values) == len(quotes), where
            assert entry["passed"] == (len(values) >= 2), where
            for path, value, quote in zip(fields, values, quotes):
                assert path in {f"skills.{c}" for c in COUNTED_SKILL_CATEGORIES}, where
                assert value in _resume_value_at(resume, path), where
                assert normalize(quote) == normalize(value), where
                assert _quoted_ok(posting, "content", quote), where
            continue
        assert _cited_ok(resume, entry["resume_field"], entry["resume_value"]), where
        quotes = entry["posting_value"]
        for quote in quotes if isinstance(quotes, list) else [quotes]:
            assert _quoted_ok(posting, entry["posting_field"], quote), where


def test_rule_evidence_is_true_on_fixtures(resume):
    senior = make_posting(7001, "Senior Software Engineer", "Boston, MA", "<p>Node.js and Fluent Bit</p>")
    for posting in (RELEVANT, IRRELEVANT, senior):
        assert_evidence_true(resume, posting)


def test_rule_evidence_is_true_on_real_snapshot(resume):
    jobs = json.loads(SNAPSHOT.read_text())["jobs"]
    assert len(jobs) == 156
    for posting in jobs:
        assert_evidence_true(resume, posting)


def test_skills_evidence_names_each_category(resume):
    posting = make_posting(7002, "Software Engineer", "Boston, MA", "<p>Python, Kafka and Kubernetes.</p>")
    skills = {e["condition"]: e for e in judge_posting(resume, posting)["rule_justification"]}["skills"]
    assert list(zip(skills["resume_field"], skills["resume_value"])) == [
        ("skills.languages", "Python"),
        ("skills.backend_automation", "Kafka"),
        ("skills.devops_cicd", "Kubernetes"),
    ]


def test_validator_requires_same_type_for_scalars(resume):
    def output(value):
        return json.dumps({"verdict": "relevant", "justification": [
            {"resume_field": "years_experience", "resume_value": value,
             "posting_field": "title", "posting_value": "Software Engineer"}]})

    assert validate_claude_output(output(2), resume, RELEVANT)[0]
    for wrong in ("2", 2.0, True):
        assert not validate_claude_output(output(wrong), resume, RELEVANT)[0], wrong


def test_cli_refuses_missing_credentials_before_fetching(tmp_path, resume_path, monkeypatch):
    # Added after live run 2 crashed on 2026-10-31 with no key visible to the process.
    from jsagent.__main__ import main
    from jsagent.claude_judge import CREDENTIAL_VARS
    for var in CREDENTIAL_VARS:
        monkeypatch.delenv(var, raising=False)
    code = main(["run", "--board", "klaviyo", "--resume", str(resume_path),
                 "--state", str(tmp_path / "state.json"), "--runs-dir", str(tmp_path / "runs"),
                 "--evidence-dir", str(tmp_path / "evidence")])
    assert code == 5
    assert not (tmp_path / "evidence").exists() and not (tmp_path / "state.json").exists()


def test_output_write_failure_leaves_state_unchanged(tmp_path, resume_path):
    state = tmp_path / "state" / "seen_ids.json"
    run_once("klaviyo", resume_path, seeded_response=write_board(tmp_path / "a.json", IRRELEVANT),
             state_path=state, runs_dir=tmp_path / "runs", evidence_dir=tmp_path / "evidence")
    before = state.read_bytes()

    blocked = tmp_path / "runs_is_a_file"
    blocked.write_text("not a directory")
    with pytest.raises(RunError):
        run_once("klaviyo", resume_path,
                 seeded_response=write_board(tmp_path / "b.json", IRRELEVANT, RELEVANT),
                 state_path=state, runs_dir=blocked, evidence_dir=tmp_path / "evidence")
    assert state.read_bytes() == before
