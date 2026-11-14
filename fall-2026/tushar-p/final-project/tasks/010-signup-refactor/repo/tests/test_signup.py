import pytest

from signup import SignupError, invite, register

INVALID = ["", "no-at-sign", "two@@example.org", "a@b@example.org", "@example.org",
           "user@nodot", "user@.example", "user@example.", "us er@example.org"]


def test_register_normalizes():
    assert register("  Ana@Example.ORG ", " Ana ") == {"email": "ana@example.org", "name": "Ana"}


@pytest.mark.parametrize("email", INVALID)
def test_register_rejects(email):
    with pytest.raises(SignupError):
        register(email, "x")


def test_invite():
    ana = register("ana@example.org", "Ana")
    assert invite(ana, " Bo@Example.org") == {"from": "ana@example.org", "to": "bo@example.org"}


@pytest.mark.parametrize("email", INVALID)
def test_invite_rejects(email):
    ana = register("ana@example.org", "Ana")
    with pytest.raises(SignupError):
        invite(ana, email)


def test_cannot_invite_yourself():
    ana = register("ana@example.org", "Ana")
    with pytest.raises(SignupError):
        invite(ana, "ANA@example.org")
