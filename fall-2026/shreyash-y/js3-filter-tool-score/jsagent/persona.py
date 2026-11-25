"""Load and validate the fictional resume. The agent refuses to run on anything that does
not look like a fictional persona (CONTRACT.md section 4: no real resume on screen or GitHub)."""
import json
import re

REQUIRED = {"target_roles": list, "experience_years": int, "skills": list, "location": str,
            "remote_ok": bool, "exclusions": list}


def validate(p):
    errors = []
    if p.get("fictional") is not True:
        errors.append("persona must say \"fictional\": true")
    for key, kind in REQUIRED.items():
        if key not in p:
            errors.append(f"missing field {key}")
        elif not isinstance(p[key], kind) or (kind is int and isinstance(p[key], bool)):
            errors.append(f"field {key} must be {kind.__name__}")
        elif kind is list and not all(isinstance(x, str) and x.strip() for x in p[key]):
            errors.append(f"field {key} must be a list of non-empty strings")
    contact = p.get("contact", {})
    email = contact.get("email", "")
    if email and not email.endswith("@example.com"):
        errors.append("contact.email must be an @example.com address")
    phone = contact.get("phone", "")
    if phone and re.sub(r"\D", "", phone)[-7:-4] != "555":
        errors.append("contact.phone must be a 555 number")
    found = re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", json.dumps(p))
    if any(not e.endswith("@example.com") for e in found):
        errors.append("an email outside example.com appears in the persona")
    return errors


def load(path):
    with open(path) as f:
        p = json.load(f)
    errors = validate(p)
    if errors:
        raise ValueError("persona refused: " + "; ".join(errors))
    return p


def public_view(p):
    """What the judges see and what reports may print: the rule fields, no contact block."""
    return {k: p[k] for k in REQUIRED}
