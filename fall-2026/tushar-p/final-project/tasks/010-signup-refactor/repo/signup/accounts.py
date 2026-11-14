"""Sign-ups and invitations."""


class SignupError(ValueError):
    """Raised for an address that cannot be used."""


def register(email, name):
    """Return a new account {"email": ..., "name": ...}.

    email is trimmed and lower-cased, and must be a valid address: exactly
    one "@", a non-empty part before it, no spaces, and a domain after it
    that contains a "." which is not its first or last character.
    Otherwise SignupError is raised. name is trimmed.
    """
    email = email.strip().lower()
    if email.count("@") != 1 or " " in email:
        raise SignupError(f"invalid address: {email!r}")
    local, domain = email.split("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise SignupError(f"invalid address: {email!r}")
    return {"email": email, "name": name.strip()}


def invite(inviter, email):
    """Return an invitation {"from": ..., "to": ...} from inviter (an account)
    to email. email is trimmed, lower-cased, and checked as for register();
    inviting yourself also raises SignupError."""
    email = email.strip().lower()
    if email.count("@") != 1 or " " in email:
        raise SignupError(f"invalid address: {email!r}")
    local, domain = email.split("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise SignupError(f"invalid address: {email!r}")
    if email == inviter["email"]:
        raise SignupError("cannot invite yourself")
    return {"from": inviter["email"], "to": email}
