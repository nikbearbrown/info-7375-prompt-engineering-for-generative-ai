"""The JUDGMENT validator rejects anything outside the fixed format or unsupported by the inputs."""
import json

import pytest

from agent.validate import validate_judgment
from tests.fixtures import NOT_RELEVANT, PERSONA, RELEVANT, valid_response


def mutated(p, fn):
    d = json.loads(valid_response(p))
    fn(d)
    return json.dumps(d)


def test_valid_synthetic_responses_pass():
    for p in (RELEVANT, NOT_RELEVANT):
        ok, errs, _ = validate_judgment(valid_response(p), p, PERSONA)
        assert ok, errs


@pytest.mark.parametrize("text", [
    "```json\n" + valid_response(RELEVANT) + "\n```",
    "Here is my answer: " + valid_response(RELEVANT),
    "relevant",
    '{"posting_id": 101, "posting_id": 101}',
    "",
])
def test_format_rejections(text):
    ok, errs, _ = validate_judgment(text, RELEVANT, PERSONA)
    assert not ok and errs[0].startswith("format")


@pytest.mark.parametrize("fn, fragment", [
    (lambda d: d.__setitem__("verdict", "maybe"), "allowed values"),
    (lambda d: d.__setitem__("extra", 1), "keys"),
    (lambda d: d.__setitem__("posting_id", 202), "association"),
    (lambda d: d.__setitem__("posting_id", "101"), "integer"),
    (lambda d: d["role_phrase"].__setitem__("matched", "data engineer"), "does not occur in posting.title"),
    (lambda d: d["excluded_terms"].update({"pass": False, "found": ["senior"]}), "does not occur"),
    (lambda d: d["shared_skills"]["skills"][0].__setitem__("quote", "Rust and Python experience"), "quote not found"),
    (lambda d: d["shared_skills"]["skills"][0].__setitem__("resume_field", "skills.data_bi"), "not in résumé field"),
    (lambda d: d["shared_skills"]["skills"][0].__setitem__("resume_field", "education"), "permitted"),
    (lambda d: d["shared_skills"]["skills"][0].__setitem__("skill", "rust"), "not a target skill"),
    (lambda d: d["shared_skills"]["skills"].append(dict(d["shared_skills"]["skills"][0])), "more than once"),
    (lambda d: d.__setitem__("verdict", "not_relevant"), "consistency: verdict"),
    (lambda d: d["shared_skills"].__setitem__("pass", False), "consistency"),
    (lambda d: d.__setitem__("explanation", "Looks good."), "name the posting field"),
])
def test_content_rejections(fn, fragment):
    ok, errs, _ = validate_judgment(mutated(RELEVANT, fn), RELEVANT, PERSONA)
    assert not ok
    assert any(fragment in e for e in errs), errs
