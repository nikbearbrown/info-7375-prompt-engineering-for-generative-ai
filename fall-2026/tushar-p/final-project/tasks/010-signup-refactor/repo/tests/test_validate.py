import pytest

import signup.accounts as accounts
from signup import SignupError

# The same addresses tests/test_signup.py rejects.
INVALID = ["", "no-at-sign", "two@@example.org", "a@b@example.org", "@example.org",
           "user@nodot", "user@.example", "user@example.", "us er@example.org"]


def test_validate_email_normalizes():
    from signup.validate import validate_email
    assert validate_email("  Ana@Example.ORG ") == "ana@example.org"


@pytest.mark.parametrize("email", INVALID)
def test_validate_email_rejects(email):
    from signup.validate import validate_email
    with pytest.raises(SignupError):
        validate_email(email)


def test_register_and_invite_use_validate_email(monkeypatch):
    import signup.validate as validate

    def fake(email):
        raise SignupError("checked by validate_email")

    # Replace validate_email wherever accounts may look it up.
    monkeypatch.setattr(validate, "validate_email", fake)
    monkeypatch.setattr(accounts, "validate_email", fake, raising=False)
    with pytest.raises(SignupError, match="checked by validate_email"):
        accounts.register("ana@example.org", "Ana")
    with pytest.raises(SignupError, match="checked by validate_email"):
        accounts.invite({"email": "ana@example.org"}, "bo@example.org")
