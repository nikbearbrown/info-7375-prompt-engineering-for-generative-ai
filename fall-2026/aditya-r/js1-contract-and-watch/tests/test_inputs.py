"""Résumé validation + R3 fictional-contact guard; board allow-list and response validation."""
import copy
import gzip
import json
import urllib.request

import pytest

from agent.board import (
    BoardError,
    RefusedError,
    _AllowListRedirects,
    board_url,
    check_allowed,
    decode_body,
    parse_jobs,
)
from agent.resume import ResumeError, load_resume, validate_resume
from tests.fixtures import PERSONA


def test_shipped_persona_is_valid():
    r = load_resume("resume/priya-nair.resume.example.json")
    assert r["personal"]["email"].endswith("@example.com")


@pytest.mark.parametrize("mutate, msg", [
    (lambda r: r["skills"].pop("languages"), "skills.languages"),
    (lambda r: r["skills"].__setitem__("data_bi", "Databricks"), "skills.data_bi"),
    (lambda r: r["skills"]["backend_automation"].append(3), "skills.backend_automation"),
    (lambda r: [r["skills"].__setitem__(k, []) for k in ("languages", "data_bi", "backend_automation", "database_cloud")], "nonempty"),
])
def test_resume_structure_errors(mutate, msg):
    r = copy.deepcopy(PERSONA)
    mutate(r)
    with pytest.raises(ResumeError, match=msg):
        validate_resume(r)


@pytest.mark.parametrize("email, phone, ok", [
    ("a@Example.COM", "(617) 555-0100", True),
    ("a@gmail.com", "(617) 555-0100", False),
    ("a@mail.example.com", "(617) 555-0100", False),
    ("a@example.com.evil.org", "(617) 555-0100", False),
    ("not-an-email", "(617) 555-0100", False),
    (None, "(617) 555-0100", False),
    ("a@example.com", "(617) 373-0100", False),
    ("a@example.com", "617-555-0100", False),
    ("a@example.com", None, False),
])
def test_fictional_contact_guard_R3(email, phone, ok):
    r = copy.deepcopy(PERSONA)
    r["personal"]["email"], r["personal"]["phone"] = email, phone
    if ok:
        validate_resume(r)
    else:
        with pytest.raises(ResumeError, match="R3") as e:
            validate_resume(r)
        if isinstance(email, str):
            assert email not in str(e.value)  # never echo a possibly-real address


def test_resume_bad_json(tmp_path):
    p = tmp_path / "r.json"
    p.write_text("{not json")
    with pytest.raises(ResumeError, match="not valid JSON"):
        load_resume(p)


@pytest.mark.parametrize("url", [
    "http://boards-api.greenhouse.io/v1/boards/databricks/jobs",
    "https://api.lever.co/v0/postings/x",
    "https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs",
    "https://user:pw@boards-api.greenhouse.io/v1/boards/x/jobs",
    "https://boards-api.greenhouse.io:8443/v1/boards/x/jobs",
    "https://web.archive.org/web/2026/https://boards-api.greenhouse.io/v1/boards/databricks/jobs",
])
def test_allow_list_refuses(url):
    with pytest.raises(RefusedError):
        check_allowed(url)


def test_allow_list_accepts_board_url():
    assert check_allowed(board_url("databricks"))


def test_redirect_off_allow_list_is_refused():
    req = urllib.request.Request(board_url("databricks"))
    with pytest.raises(RefusedError):
        _AllowListRedirects().redirect_request(req, None, 302, "Found", {}, "https://evil.example.org/jobs")


def test_invalid_board_token_refused():
    with pytest.raises(RefusedError):
        board_url("../../etc")


@pytest.mark.parametrize("data, msg", [
    ({"nope": []}, "no 'jobs'"),
    ({"jobs": [{"title": "x"}]}, "missing or non-integer id"),
    ({"jobs": [{"id": True}]}, "non-integer"),
    ({"jobs": [{"id": 1}, {"id": 1}]}, "duplicate"),
])
def test_board_response_validation(data, msg):
    with pytest.raises(BoardError, match=msg):
        parse_jobs(data)


def test_gzip_and_invalid_body():
    assert decode_body(gzip.compress(json.dumps({"jobs": []}).encode())) == {"jobs": []}
    with pytest.raises(BoardError):
        decode_body(b"<html>maintenance</html>")
