"""CONTRACT Wrong version 2 — an empty or "good fit" justification.

A right verdict with no reason looks fine to someone reading only the conclusion. These tests make
every ok verdict name real fields (each name is looked up in the actual résumé / profile / data
files), stop at the check that cut it, and turn an empty JD into an error instead of "relevant".
"""

import json

import pytest
from fakes import GOOD, FakeClaude, board, by_id, job, run_once

from job_agent.common.posting import Posting
from job_agent.judges import claude, rule

POSTING_FIELDS = {"title", "location.name", "content"}
PROMPT = claude.Prompt("test", "judge this")

# One posting cut at each check, plus one that passes all: together they produce every kind of line.
CASES = {
    11: GOOD,                                                                  # relevant: all 7 lines
    12: {**GOOD, "title": "Senior Backend Engineer"},                          # cut at 1a
    13: {**GOOD, "title": "Abuse Investigator"},                               # cut at 1b
    14: {**GOOD, "location": "Dublin, Ireland"},                               # cut at 2
    15: {**GOOD, "content": "<p>We use Haskell.</p>"},                          # cut at 3
    16: {**GOOD, "content": "<p>Java, 8+ years.</p>"},                          # cut at 4
    17: {**GOOD, "content": "<p>Java. We cannot sponsor visas.</p>"},           # cut at 5
    18: {**GOOD, "content": "<p>Java. Pay: $50,000 - $60,000.</p>"},            # cut at 6
}
LAST_FIELD = {11: "content", 12: "title", 13: "title", 14: "location.name",
              15: "content", 16: "content", 17: "content", 18: "content"}


def _field_exists(name: str, docs: dict) -> bool:
    """Resolve 'profile.years_experience + profile.years_stretch' or 'resume.skills[].keywords[]'
    against the real input files, so a made-up field name ('common sense') fails."""
    for part in name.split(" + "):
        if part.startswith("data/"):
            if not (docs["repo"] / part).exists():
                return False
            continue
        root, *keys = part.replace("[]", "").split(".")
        node = docs[root]
        for key in keys:
            node = node[0] if isinstance(node, list) else node   # step into the first list item
            if not isinstance(node, dict) or key not in node:
                return False
            node = node[key]
    return True


@pytest.fixture
def run_doc(paths):
    run_once(paths, board(job(1)), n=0)
    return run_once(paths, board(job(1), *(job(i, **c) for i, c in CASES.items())), n=1)


def test_every_ok_verdict_has_a_justification_with_real_field_names(paths, run_doc):
    docs = {"resume": json.loads(paths.default_resume.read_text()),
            "profile": json.loads(paths.default_profile.read_text()), "repo": paths.repo}
    ok = [v for v in run_doc["verdicts"] if v["status"] == "ok" and v["judge"] == "rule"]
    assert len(ok) == len(CASES)
    for v in ok:
        assert v["justification"], f"{v['posting_id']}: empty justification"
        for line in v["justification"]:
            assert set(line) == {"posting_field", "compared_to", "result"}
            assert line["posting_field"] in POSTING_FIELDS
            assert _field_exists(line["compared_to"], docs), line["compared_to"]
            assert line["result"].strip() and line["result"].lower() != "good fit"


def test_justification_stops_at_the_check_that_cut_it(run_doc):
    verdicts = by_id(run_doc)
    assert len(verdicts[11]["justification"]) == 7          # passed all six (1a and 1b are two lines)
    for pid, field in LAST_FIELD.items():
        assert verdicts[pid]["justification"][-1]["posting_field"] == field
    # 12..18 are cut at checks 1a, 1b, 2, 3, 4, 5, 6: justification length = position of that check.
    assert [len(verdicts[p]["justification"]) for p in range(12, 19)] == [1, 2, 3, 4, 5, 6, 7]
    assert all(verdicts[p]["verdict"] == "not_relevant" for p in range(12, 19))


@pytest.mark.parametrize("content", ["", "   ", "<p></p>", "<div> <br/> </div>"])
def test_empty_jd_is_an_error_not_relevant(criteria, content):
    result = rule.judge(Posting(31, GOOD["title"], GOOD["location"], content), criteria)
    v = result.verdict
    assert v["status"] == "error"
    assert v["verdict"] == "not_relevant"
    assert v["error_message"] == "posting.content is empty, skills check cannot run"
    assert v["justification"] == []


def test_claude_answer_with_a_quote_not_in_the_posting_is_rejected(criteria):
    """Claude side: a confident answer whose evidence is made up must become an error, not a verdict."""
    def made_up(p):
        return {"posting_id": p["posting_id"], "verdict": "relevant", "justification": [
            {"posting_field": "content", "compared_to": "resume.skills[].keywords[]",
             "result": "requires Rust, which the résumé lists", "quote": "5+ years of Rust required"}]}
    posting = Posting(41, GOOD["title"], GOOD["location"], GOOD["content"])
    v = claude.judge(posting, criteria, FakeClaude(made_up), PROMPT).verdict
    assert (v["status"], v["verdict"]) == ("error", "not_relevant")
    assert v["error_message"] == "rejected by validator: justification[0].quote not found in posting.content"


def test_claude_answer_with_no_justification_is_rejected(criteria):
    posting = Posting(42, GOOD["title"], GOOD["location"], GOOD["content"])
    answer = FakeClaude(lambda p: {"posting_id": p["posting_id"], "verdict": "relevant", "justification": []})
    v = claude.judge(posting, criteria, answer, PROMPT).verdict
    assert v["status"] == "error" and v["justification"] == []
