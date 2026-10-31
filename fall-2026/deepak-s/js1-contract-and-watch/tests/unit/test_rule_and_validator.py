"""Unit tests for jobwatch.rule, jobwatch.validator, jobwatch.postings and jobwatch.paths. Written by Claude Code on 2026-10-29.

Real postings come from evidence/manual/stripe_20261030T000804Z.raw (Deepak's manual capture);
everything else is constructed.
"""
import json

import pytest

from conftest import PERSONA, ROOT, job
from jobwatch.paths import Unresolved, pointer, resolve
from jobwatch.postings import content_text, normalise_id, parse_body, posting_document
from jobwatch.rule import apply_rule
from jobwatch.validator import Invalid, check_verdict, parse_output

CAPTURE = ROOT / "evidence" / "manual" / "stripe_20261030T000804Z.raw"
RESUME = json.loads(PERSONA.read_text(encoding="utf-8"))


def _real(posting_id):
    jobs = json.loads(CAPTURE.read_bytes())["jobs"]
    return next(j for j in jobs if j["id"] == posting_id)


def _cite(source, path, value):
    return {"source": source, "path": path, "value": value}


def test_worked_example_8197886():
    j = _real(8197886)
    assert j["location"]["name"] == "New York City "
    assert apply_rule(RESUME, j) == {"verdict": "relevant", "citations": [
        _cite("resume", "/targets/roles/0", "Machine Learning Engineer"),
        _cite("posting", "/title", "Machine Learning Engineer"),
        _cite("resume", "/targets/locations/1", "New York"),
        _cite("posting", "/location/name", "New York"),
    ]}


def test_staff_is_excluded_at_index_5_on_8148653():
    assert apply_rule(RESUME, _real(8148653)) == {"verdict": "not_relevant", "citations": [
        _cite("resume", "/targets/exclude_title_terms/5", "Staff"),
        _cite("posting", "/title", "Staff"),
    ]}


def test_lowest_index_wins_when_several_terms_match():
    # "Senior Staff" (index 0) and "Staff" (index 5) both match; index 0 is cited.
    verdict = apply_rule(RESUME, job(1, "Senior Staff ML Engineer, Remote"))
    assert verdict["citations"][0] == _cite("resume", "/targets/exclude_title_terms/0", "Senior Staff")


def test_no_role_cites_roles_0_and_the_full_title():
    assert apply_rule(RESUME, job(1, "Account Executive, AI Sales")) == {"verdict": "not_relevant", "citations": [
        _cite("resume", "/targets/roles/0", "Machine Learning Engineer"),
        _cite("posting", "/title", "Account Executive, AI Sales"),
    ]}


@pytest.mark.parametrize("location,cited", [("Chicago", True), ("", False), (" — ", False), (None, False)])
def test_no_location_cites_location_name_only_when_it_has_tokens(location, cited):
    verdict = apply_rule(RESUME, job(1, "AI Engineer", location=location))
    assert verdict["verdict"] == "not_relevant"
    tail = [_cite("posting", "/location/name", location)] if cited else []
    assert verdict["citations"] == [
        _cite("resume", "/targets/roles/2", "AI Engineer"),
        _cite("posting", "/title", "AI Engineer"),
    ] + tail


def test_every_rule_verdict_on_the_real_capture_passes_the_validator():
    parsed = parse_body(CAPTURE.read_bytes())
    assert parsed.total == 737 and not parsed.skipped_bad_id and not parsed.skipped_bad_title
    for pid, j in parsed.judgeable():
        check_verdict(apply_rule(RESUME, j), RESUME, posting_document(j))


@pytest.mark.parametrize("raw,expected", [
    (123, "123"), ("123", "123"), (True, None), (0, None), (-5, None), ("0123", None),
    ("12a", None), ("123\n", None), (12.0, None), (None, None),
])
def test_normalise_id(raw, expected):
    assert normalise_id(raw) == expected


def test_parse_body_lists_skips_and_keeps_first_duplicate():
    body = json.dumps({"jobs": [
        job(1, "AI Engineer"), job("1", "Recruiter"), job(0, "Bad id"), "not a job",
        job(2, "  "), job(3, None), job(4, "Data Scientist"),
    ]}).encode()
    p = parse_body(body)
    assert p.total == 7
    assert [pid for pid, _ in p.kept] == ["1", "2", "3", "4"]
    assert p.kept[0][1]["title"] == "AI Engineer"
    assert p.duplicates_dropped == 1
    assert p.skipped_bad_id == [0, None]
    assert p.skipped_bad_title == ["2", "3"]
    assert [pid for pid, _ in p.judgeable()] == ["1", "4"]


def test_content_text_unescapes_strips_tags_unescapes_again_and_truncates():
    assert content_text("&lt;p&gt;Hello&lt;/p&gt;&lt;p&gt;world&amp;nbsp;!&lt;/p&gt;") == "Hello world !"
    # Escaped markup in the text survives as text: the second unescape runs after tag stripping.
    assert content_text("&lt;p&gt;Use &amp;lt;b&amp;gt; tags &amp;amp; more&lt;/p&gt;") == "Use <b> tags & more"
    assert len(content_text("x " * 5000)) == 6000
    assert content_text(None) == ""


def test_no_entities_left_in_content_text_of_the_real_capture():
    for j in json.loads(CAPTURE.read_bytes())["jobs"]:
        text = content_text(j.get("content"))
        assert "&nbsp;" not in text and "&amp;" not in text and "&gt;" not in text, j["id"]


def test_posting_document_is_exactly_the_contract_fields():
    doc = posting_document(job(7, "AI Engineer", content="&lt;b&gt;PyTorch&lt;/b&gt;", departments=["ML"]))
    assert set(doc) == {"id", "title", "location", "absolute_url", "departments", "content_text"}
    assert doc["content_text"] == "PyTorch"


def test_json_pointer_escapes_and_bounds():
    doc = {"a/b": {"~k": [10, 20]}}
    assert resolve(doc, pointer("a/b", "~k", 1)) == 20
    for bad in ("/a~1b/~0k/2", "/a~1b/~0k/01", "/a~1b/~0k/-", "nope", "/missing"):
        with pytest.raises(Unresolved):
            resolve(doc, bad)


GOOD = {"posting_id": "7", "verdict": "relevant", "reason": "r",
        "citations": [_cite("resume", "/targets/roles/2", "AI Engineer"), _cite("posting", "/title", "AI Engineer")]}


@pytest.mark.parametrize("text,reason", [
    ("[]", "not_object"),
    ('{"posting_id": "7", "posting_id": "7"}', "duplicate_key"),
    (json.dumps({**GOOD, "reason": "x" * 401}), "reason_too_long"),
    (json.dumps({k: v for k, v in GOOD.items() if k != "reason"}), "missing_keys"),
    (json.dumps({**GOOD, "citations": [GOOD["citations"][0], {**GOOD["citations"][1], "note": 1}]}), "citation_malformed"),
    (json.dumps({**GOOD, "citations": [GOOD["citations"][0], _cite("job", "/title", "AI")]}), "citation_bad_source"),
    (json.dumps({**GOOD, "citations": [GOOD["citations"][0], _cite("posting", "/title", "")]}), "value_empty"),
    (json.dumps({**GOOD, "citations": [GOOD["citations"][0], _cite("posting", "/departments", "x")]}), "path_not_text"),
])
def test_parse_output_named_reasons(text, reason):
    j = job(7, "AI Engineer")
    with pytest.raises(Invalid) as e:
        parse_output(text, "7", RESUME, posting_document(j))
    assert e.value.reason == reason


def test_parse_output_accepts_the_contract_format():
    j = job(7, "AI Engineer")
    assert parse_output(json.dumps(GOOD), "7", RESUME, posting_document(j)) == GOOD
