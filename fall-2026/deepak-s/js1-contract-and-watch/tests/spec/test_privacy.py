"""Case 15 (Privacy). Written by Claude Code from tests/acceptance/ACCEPTANCE_CASES.md on 2026-10-29, before any implementation. Every bad email is built at runtime so none sits in a tracked file."""
import json

import pytest

from conftest import FakeOpener, run_args, run_cli

BAD_EMAIL = "me" + "@" + "gmail.com"
SUBDOMAIN_EMAIL = "riley" + "@" + "mail." + "example.com"


def _set(path, value):
    def mutate(data):
        node = data
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
    return mutate


def _append_highlight(text):
    def mutate(data):
        data["work"][0]["highlights"].append(text)
    return mutate


def _drop_fictional(data):
    del data["fictional"]


LEAKS = {
    "email_outside_example_com": (_set(["basics", "email"], BAD_EMAIL), BAD_EMAIL),
    "email_in_nested_string": (_append_highlight("Write to " + BAD_EMAIL), BAD_EMAIL),
    "email_on_example_com_subdomain": (_set(["basics", "email"], SUBDOMAIN_EMAIL), SUBDOMAIN_EMAIL),
    "phone_617_555_9999": (_set(["basics", "phone"], "617-555-9999"), "617-555-9999"),
    "phone_other_format": (_set(["basics", "phone"], "(617) 555 9999"), "(617) 555 9999"),
    "phone_with_country_code": (_set(["basics", "phone"], "+1 617 555 0200"), "+1 617 555 0200"),
}
NOT_FICTIONAL = {
    "fictional_missing": _drop_fictional,
    "fictional_false": _set(["fictional"], False),
    "fictional_string": _set(["fictional"], "true"),
}


def _write_resume(workdir, mutate):
    data = json.loads((workdir / "examples" / "persona_resume.json").read_text(encoding="utf-8"))
    mutate(data)
    (workdir / "constructed_resume.json").write_text(json.dumps(data), encoding="utf-8")
    return "constructed_resume.json"


@pytest.mark.parametrize("mutate,value", list(LEAKS.values()), ids=list(LEAKS))
def test_ac15_real_contact_details_are_refused_without_echoing_them(workdir, capsys, mutate, value):
    opener = FakeOpener({})
    assert run_cli(run_args(resume=_write_resume(workdir, mutate)), opener=opener) == 2
    assert opener.requests == []
    out = capsys.readouterr()
    assert value not in out.out
    assert value not in out.err


@pytest.mark.parametrize("mutate", list(NOT_FICTIONAL.values()), ids=list(NOT_FICTIONAL))
def test_ac15_resume_not_marked_fictional_is_refused(workdir, mutate):
    opener = FakeOpener({})
    assert run_cli(run_args(resume=_write_resume(workdir, mutate)), opener=opener) == 2
    assert opener.requests == []
