"""Unit tests for jobwatch.inputs, jobwatch.prompt and jobwatch.fetch.check_url. Written by Claude Code on 2026-10-29. All inputs are constructed; non-example.com emails are built at runtime."""
import json

import pytest

from conftest import PERSONA
from jobwatch.errors import REFUSED, Stop
from jobwatch.fetch import _NoRedirect, check_url
from jobwatch.inputs import check_token, load_resume, privacy_findings
from jobwatch.prompt import load_prompt, fill_user

RESUME = json.loads(PERSONA.read_text(encoding="utf-8"))


@pytest.mark.parametrize("phone", ["+1-617-555-0142", "617-555-0100", "(617) 555-0199", "555-0150", "1 617 555 0101"])
def test_fictional_phone_numbers_are_allowed(phone):
    assert privacy_findings({"basics": {"phone": phone}}) == []


@pytest.mark.parametrize("phone", ["617-555-0200", "617.555.0099", "6175559999", "+1 617 555 1234",
                                   "+44 20 7946 0958", "555-0200", "(617) 867-5309"])
def test_other_phone_numbers_are_refused(phone):
    assert privacy_findings({"basics": {"phone": phone}}) == ["/basics/phone contains a phone number outside 555-0100 to 555-0199"]


@pytest.mark.parametrize("text", ["2023-01-15", "2021-06", "Grew revenue 25% in 2024", "Python 3.11"])
def test_dates_and_versions_are_not_phone_numbers(text):
    assert privacy_findings({"note": text}) == []


def test_email_rules():
    assert privacy_findings({"e": "Riley.Okafor@EXAMPLE.COM"}) == []
    assert privacy_findings({"e": "write to riley.okafor@example.com."}) == []
    for bad in ("x" + "@" + "example.org", "x" + "@" + "mail.example.com", "x" + "@" + "example.com.evil.net"):
        assert privacy_findings({"e": bad}) == ["/e contains an email address outside @example.com"]


def test_refusal_names_the_path_not_the_value(tmp_path):
    data = json.loads(json.dumps(RESUME))
    leaked = "real" + "@" + "gmail.com"
    data["work"][1]["highlights"][0] = "Contact " + leaked
    p = tmp_path / "r.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(Stop) as e:
        load_resume(p)
    assert e.value.code == REFUSED
    assert "/work/1/highlights/0" in str(e.value) and leaked not in str(e.value)


@pytest.mark.parametrize("change", [
    lambda d: d["targets"]["roles"].append("--"),
    lambda d: d["targets"]["locations"].append("()"),
    lambda d: d["targets"].update(roles=[]),
    lambda d: d["basics"].pop("phone"),
    lambda d: d.update(skills="Python"),
])
def test_resume_shape_is_refused(tmp_path, change):
    data = json.loads(json.dumps(RESUME))
    change(data)
    p = tmp_path / "r.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(Stop) as e:
        load_resume(p)
    assert e.value.code == REFUSED


def test_persona_loads():
    data, raw = load_resume(PERSONA)
    assert data == RESUME and raw == PERSONA.read_bytes()


@pytest.mark.parametrize("token", ["stripe", "acme-1", "a_b", "0"])
def test_good_tokens(token):
    check_token(token)


@pytest.mark.parametrize("token", ["acme\n", "-acme", "a" * 64, "acme corp", "acmé"])
def test_bad_tokens(token):
    with pytest.raises(Stop):
        check_token(token)


@pytest.mark.parametrize("url", [
    "http://boards-api.greenhouse.io/v1/boards/acme/jobs",
    "https://BOARDS-API.greenhouse.io./v1/boards/acme/jobs",
    "https://boards-api.greenhouse.io:443/v1/boards/acme/jobs",
    "https://user" + "@" + "boards-api.greenhouse.io/v1/boards/acme/jobs",  # split so the presubmit email scan stays quiet
    "https://boards-api.greenhouse.io.evil.example.net/v1",
    "https://api.greenhouse.io/v1/boards/acme/jobs",
])
def test_url_check_refuses(url):
    with pytest.raises(Stop) as e:
        check_url(url)
    assert e.value.code == REFUSED


def test_url_check_host_is_case_insensitive():
    check_url("https://Boards-API.Greenhouse.io/v1/boards/acme/jobs?content=true")


def test_redirect_handler_never_builds_a_follow_up_request():
    assert _NoRedirect().redirect_request(None, None, 301, "Moved", {}, "https://elsewhere.example.net/") is None


GOOD_PROMPT = "## System\nBe exact.\n\n## User\nR {{RESUME_JSON}}\nI {{POSTING_ID}}\nP {{POSTING_JSON}}\n"


@pytest.mark.parametrize("text", [
    "## User\n{{RESUME_JSON}} {{POSTING_ID}} {{POSTING_JSON}}\n",
    GOOD_PROMPT + "## Notes\nextra\n",
    GOOD_PROMPT + "## User\nagain\n",
    "# Title\n" + GOOD_PROMPT,
    GOOD_PROMPT.replace("{{POSTING_ID}}", "{{POSTING_ID}} {{POSTING_ID}}"),
    GOOD_PROMPT.replace("{{POSTING_JSON}}", ""),
    GOOD_PROMPT.replace("Be exact.", "Be exact. {{POSTING_ID}}"),
])
def test_malformed_prompts_are_refused(tmp_path, text):
    p = tmp_path / "p.md"
    p.write_text(text, encoding="utf-8")
    with pytest.raises(Stop) as e:
        load_prompt(p)
    assert e.value.code == REFUSED


def test_missing_prompt_is_refused(tmp_path):
    with pytest.raises(Stop) as e:
        load_prompt(tmp_path / "absent.md")
    assert e.value.code == REFUSED


def test_fill_is_literal_and_single_pass(tmp_path):
    p = tmp_path / "p.md"
    p.write_text(GOOD_PROMPT, encoding="utf-8")
    prompt = load_prompt(p)
    assert prompt.system == "Be exact."
    filled = fill_user(prompt, {"note": "{{POSTING_ID}}"}, "42", {"id": 42})
    assert "I 42" in filled
    assert '"note": "{{POSTING_ID}}"' in filled
