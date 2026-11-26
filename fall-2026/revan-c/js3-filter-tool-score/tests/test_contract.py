"""Tests derived from CONTRACT.md v2, written before the implementation existed.

The five tests named in "Wrong versions my tests must catch" come first; the rest
pin down the rule, refusals, and run behaviour the contract states.
"""
import copy
import json

import pytest

from conftest import IRRELEVANT, RELEVANT, make_posting, write_board
from jsagent.authorization import authorization_flag
from jsagent.fetch import FetchRefused, board_url, check_redirect, check_url
from jsagent.resume import ResumeError, load_resume
from jsagent.rule import judge_posting, judge_postings
from jsagent.run import JUDGMENT_LABEL, RunError, run_once
from jsagent.text import contains_sequence, normalize, strip_html
from jsagent.validator import validate_claude_output


def run_dirs(tmp_path):
    return dict(
        state_path=tmp_path / "state" / "seen_ids.json",
        runs_dir=tmp_path / "runs",
        evidence_dir=tmp_path / "evidence",
    )


def conditions(justification):
    return {entry["condition"]: entry for entry in justification}


# ---------------------------------------------------------------------------
# Wrong version 1 — shifted labels
# ---------------------------------------------------------------------------

def test_verdicts_keyed_by_id(resume):
    for order in ([RELEVANT, IRRELEVANT], [IRRELEVANT, RELEVANT]):
        results = judge_postings(resume, order)
        assert results[1001]["rule_verdict"] == "relevant"
        assert results[1002]["rule_verdict"] == "not_relevant"
        # Evidence must come from the same posting, not a neighbour.
        assert conditions(results[1001]["rule_justification"])["title"]["posting_value"] == RELEVANT["title"]
        assert conditions(results[1002]["rule_justification"])["title"]["posting_value"] == IRRELEVANT["title"]


# ---------------------------------------------------------------------------
# Wrong version 2 — empty or fake justification
# ---------------------------------------------------------------------------

def good_claude_output():
    return {
        "verdict": "relevant",
        "justification": [
            {"resume_field": "target_titles", "resume_value": "software engineer",
             "posting_field": "title", "posting_value": "Software Engineer"},
            {"resume_field": "skills.devops_cicd", "resume_value": "Kubernetes",
             "posting_field": "content", "posting_value": "kubernetes"},
        ],
    }


def test_validator_accepts_well_formed_cited_output(resume):
    ok, parsed, errors = validate_claude_output(json.dumps(good_claude_output()), resume, RELEVANT)
    assert ok, errors
    assert parsed["verdict"] == "relevant"


def test_validator_rejects_empty_or_fake_evidence(resume):
    empty = good_claude_output()
    empty["justification"] = []

    fake_field = good_claude_output()
    fake_field["justification"][0]["resume_field"] = "resume.certifications"

    fake_posting_value = good_claude_output()
    fake_posting_value["justification"][1]["posting_value"] = "Terraform at scale"

    fake_resume_value = good_claude_output()
    fake_resume_value["justification"][1]["resume_value"] = "Rust"  # not in skills.devops_cicd

    for bad in (empty, fake_field, fake_posting_value, fake_resume_value):
        ok, parsed, errors = validate_claude_output(json.dumps(bad), resume, RELEVANT)
        assert not ok and parsed is None and errors


def test_validator_rejects_format_violations(resume):
    good = good_claude_output()
    wrong_verdict = dict(good, verdict="maybe")
    extra_key = dict(good, confidence=0.9)
    missing_key = {"verdict": "relevant"}
    entry_extra_key = copy.deepcopy(good)
    entry_extra_key["justification"][0]["note"] = "x"
    cases = [
        "Here is my answer: " + json.dumps(good),  # surrounding prose
        "```json\n" + json.dumps(good) + "\n```",  # code fence
        "not json at all",
        json.dumps([good]),
        json.dumps(wrong_verdict),
        json.dumps(extra_key),
        json.dumps(missing_key),
        json.dumps(entry_extra_key),
    ]
    for text in cases:
        ok, _, errors = validate_claude_output(text, resume, RELEVANT)
        assert not ok, text
        assert errors


def test_validator_checks_posting_value_against_same_posting(resume):
    # "Software Engineer" is in RELEVANT's title, not IRRELEVANT's.
    ok, _, _ = validate_claude_output(json.dumps(good_claude_output()), resume, IRRELEVANT)
    assert not ok


# ---------------------------------------------------------------------------
# Wrong version 3 — baseline leak
# ---------------------------------------------------------------------------

def test_baseline_reports_zero(tmp_path, resume_path):
    dirs = run_dirs(tmp_path)
    seeded = write_board(tmp_path / "seeded.json", RELEVANT, IRRELEVANT)
    result = run_once("klaviyo", resume_path, seeded_response=seeded, claude_judge=None, **dirs)
    assert result["baseline"] is True
    assert result["new_postings"] == []
    saved = json.loads(dirs["state_path"].read_text())
    assert sorted(saved["seen_ids"]) == [1001, 1002]


def test_second_run_reports_only_unseen_ids(tmp_path, resume_path):
    dirs = run_dirs(tmp_path)
    first = write_board(tmp_path / "first.json", IRRELEVANT)
    run_once("klaviyo", resume_path, seeded_response=first, claude_judge=None, **dirs)

    changed_irrelevant = dict(IRRELEVANT, title="Enterprise Account Executive (updated)")
    second = write_board(tmp_path / "second.json", changed_irrelevant, RELEVANT)
    result = run_once("klaviyo", resume_path, seeded_response=second, claude_judge=None, **dirs)

    assert result["baseline"] is False
    assert [r["posting_id"] for r in result["new_postings"]] == [1001]  # same id changed != new
    assert result["new_postings"][0]["rule_verdict"] == "relevant"
    assert sorted(json.loads(dirs["state_path"].read_text())["seen_ids"]) == [1001, 1002]


def test_invalid_board_response_does_not_advance_state(tmp_path, resume_path):
    dirs = run_dirs(tmp_path)
    run_once("klaviyo", resume_path, seeded_response=write_board(tmp_path / "a.json", IRRELEVANT),
             claude_judge=None, **dirs)
    before = dirs["state_path"].read_text()

    broken = dict(RELEVANT)
    del broken["content"]
    with pytest.raises(RunError):
        run_once("klaviyo", resume_path, seeded_response=write_board(tmp_path / "b.json", broken),
                 claude_judge=None, **dirs)
    assert dirs["state_path"].read_text() == before


def test_live_raw_response_saved_before_parsing(tmp_path, resume_path):
    dirs = run_dirs(tmp_path)
    raw = b"{ this is not json"
    with pytest.raises(RunError):
        run_once("klaviyo", resume_path, fetcher=lambda url: raw, claude_judge=None, **dirs)
    saved = list(dirs["evidence_dir"].glob("klaviyo_*.json"))
    assert len(saved) == 1 and saved[0].read_bytes() == raw
    assert not dirs["state_path"].exists()


def test_run_file_labels_mode_and_source(tmp_path, resume_path):
    dirs = run_dirs(tmp_path)
    seeded = write_board(tmp_path / "seeded.json", IRRELEVANT)
    run_once("klaviyo", resume_path, seeded_response=seeded, claude_judge=None, **dirs)
    run_files = list(dirs["runs_dir"].glob("*.json"))
    assert len(run_files) == 1
    record = json.loads(run_files[0].read_text())
    assert record["mode"] == "seeded"
    assert record["source"] == str(seeded)


# ---------------------------------------------------------------------------
# Wrong version 4 — authorization trap
# ---------------------------------------------------------------------------

def test_work_authorized_still_needs_sponsorship(tmp_path, resume, resume_path):
    assert "work authorized" in resume["visa"]["current_status"]
    assert authorization_flag(resume) == "NEEDS_SPONSORSHIP"

    dirs = run_dirs(tmp_path)
    run_once("klaviyo", resume_path, seeded_response=write_board(tmp_path / "a.json", IRRELEVANT),
             claude_judge=None, **dirs)
    result = run_once("klaviyo", resume_path,
                      seeded_response=write_board(tmp_path / "b.json", IRRELEVANT, RELEVANT),
                      claude_judge=None, **dirs)
    record = result["new_postings"][0]
    assert record["authorization_flag"] == "NEEDS_SPONSORSHIP"
    assert record["e_verify"] == "unknown"


def test_authorization_flag_other_and_missing_visa(resume, tmp_path):
    other = copy.deepcopy(resume)
    other["visa"] = {"type": "H-1B", "current_status": "H-1B"}
    assert authorization_flag(other) == "UNKNOWN"

    missing = copy.deepcopy(resume)
    del missing["visa"]
    path = tmp_path / "no_visa.json"
    path.write_text(json.dumps(missing))
    with pytest.raises(ResumeError):
        load_resume(path)


# ---------------------------------------------------------------------------
# Wrong version 5 — ignored exclusions
# ---------------------------------------------------------------------------

def test_seniority_and_mobile_exclusions(resume):
    body = "<p>TypeScript and Kubernetes every day.</p>"
    senior = make_posting(2001, "Senior Software Engineer - Platform Tools", "Boston, MA", body)
    mobile = make_posting(2002, "Software Engineer II - Mobile Android", "Boston, MA", body)
    for posting, failing in ((senior, "seniority"), (mobile, "role_type")):
        result = judge_posting(resume, posting)
        conds = conditions(result["rule_justification"])
        assert conds["title"]["passed"] and conds["location"]["passed"] and conds["skills"]["passed"]
        assert conds[failing]["passed"] is False
        assert result["rule_verdict"] == "not_relevant"


# ---------------------------------------------------------------------------
# The rule — contract hand-check examples and stated edge cases
# ---------------------------------------------------------------------------

def test_contract_hand_check_examples(resume):
    both = "<p>TypeScript and Kubernetes.</p>"
    cases = [
        ("Software Engineer - Platform Tools", "Boston, MA", both, "relevant", None),
        ("Software Engineer - Platform Tools", "Boston, MA", "<p>TypeScript only.</p>", "not_relevant", "skills"),
        ("Senior Software Engineer - Platform Tools", "Boston, MA", both, "not_relevant", "seniority"),
        ("Software Engineer II - Mobile Android", "Boston, MA", both, "not_relevant", "role_type"),
        ("Software Engineer - Platform Tools", "Austin, TX", both, "not_relevant", "location"),
    ]
    for i, (title, loc, content, verdict, failing) in enumerate(cases):
        result = judge_posting(resume, make_posting(3000 + i, title, loc, content))
        assert result["rule_verdict"] == verdict, title
        conds = conditions(result["rule_justification"])
        assert set(conds) == {"title", "location", "skills", "seniority", "role_type"}
        failed = {name for name, c in conds.items() if not c["passed"]}
        assert failed == ({failing} if failing else set()), title


def test_justification_entries_have_contract_keys(resume):
    keys = {"condition", "passed", "resume_field", "resume_value", "posting_field", "posting_value"}
    for entry in judge_posting(resume, RELEVANT)["rule_justification"]:
        assert set(entry) == keys


def test_location_rules(resume):
    content = "<p>TypeScript and Kubernetes.</p>"
    expect = {
        "Boston, MA": True,
        "Boston, MA; Denver, CO": True,
        "Remote - US": True,
        "Anywhere in the United States": False,
        "Eastern Timezone": False,
        "Bostonian Heights": False,
        "Denver, CO": False,
    }
    for loc, passed in expect.items():
        result = judge_posting(resume, make_posting(4000, "Software Engineer", loc, content))
        assert conditions(result["rule_justification"])["location"]["passed"] is passed, loc


def test_skill_normalization_edges():
    content = normalize(strip_html("&lt;p&gt;We use PostgreSQL, MSSQL, JavaScript and Node.js.&lt;/p&gt;"))
    assert contains_sequence(content, normalize("PostgreSQL"))
    assert contains_sequence(content, normalize("Node.js"))
    assert not contains_sequence(content, normalize("SQL"))
    assert not contains_sequence(content, normalize("Java"))
    assert normalize("Fluent Bit") == "fluent bit"
    assert normalize("Node.js") == "node js"


def test_skills_count_distinct_and_ignore_not_shipped(resume):
    repeated = make_posting(5001, "Software Engineer", "Boston, MA",
                            "<p>Python, Python, and more Python.</p>")
    not_shipped = make_posting(5002, "Software Engineer", "Boston, MA",
                               "<p>Rust and Terraform required.</p>")
    for posting in (repeated, not_shipped):
        result = judge_posting(resume, posting)
        assert conditions(result["rule_justification"])["skills"]["passed"] is False


# ---------------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------------

def test_only_klaviyo_on_allowed_host():
    assert board_url("klaviyo") == "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true"
    with pytest.raises(FetchRefused):
        board_url("greenhouse")
    for url in (
        "https://evil.example.com/v1/boards/klaviyo/jobs?content=true",
        "http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true",
        "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs/123",
        "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs",
    ):
        with pytest.raises(FetchRefused):
            check_url(url)


def test_cross_host_redirect_refused():
    with pytest.raises(FetchRefused):
        check_redirect("https://job-boards.greenhouse.io/klaviyo")


def test_cli_refuses_other_slug(tmp_path, resume_path):
    with pytest.raises(FetchRefused):
        run_once("greenhouse", resume_path, seeded_response=write_board(tmp_path / "a.json", RELEVANT),
                 claude_judge=None, **run_dirs(tmp_path))


def test_real_looking_resume_refused(resume, tmp_path):
    for field, value in (("email", "aarav@gmail.com"), ("phone", "(617) 123-0148")):
        bad = copy.deepcopy(resume)
        bad["personal"][field] = value
        path = tmp_path / f"bad_{field}.json"
        path.write_text(json.dumps(bad))
        with pytest.raises(ResumeError):
            load_resume(path)


# ---------------------------------------------------------------------------
# Two judges stay separate
# ---------------------------------------------------------------------------

def test_claude_judgment_is_labeled_and_never_overrides_rule(tmp_path, resume_path):
    dirs = run_dirs(tmp_path)
    run_once("klaviyo", resume_path, seeded_response=write_board(tmp_path / "a.json", RELEVANT),
             claude_judge=None, **dirs)

    def contrary_judge(resume, posting):
        return {"claude_verdict": "relevant", "claude_justification": [], "claude_reason": "fake judge"}

    result = run_once("klaviyo", resume_path,
                      seeded_response=write_board(tmp_path / "b.json", RELEVANT, IRRELEVANT),
                      claude_judge=contrary_judge, **dirs)
    record = result["new_postings"][0]
    assert record["posting_id"] == 1002
    assert record["rule_verdict"] == "not_relevant"
    assert record["claude_verdict"] == "relevant"
    assert record["claude_label"] == JUDGMENT_LABEL == "JUDGMENT — model output, not a fact"


def test_disabled_claude_reported_unavailable(tmp_path, resume_path):
    dirs = run_dirs(tmp_path)
    run_once("klaviyo", resume_path, seeded_response=write_board(tmp_path / "a.json", IRRELEVANT),
             claude_judge=None, **dirs)
    result = run_once("klaviyo", resume_path,
                      seeded_response=write_board(tmp_path / "b.json", IRRELEVANT, RELEVANT),
                      claude_judge=None, **dirs)
    record = result["new_postings"][0]
    assert record["claude_verdict"] == "unavailable"
    assert record["claude_reason"]
