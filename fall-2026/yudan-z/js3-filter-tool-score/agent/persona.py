"""Contract §1 / §3(2): accept only a fictional persona résumé with the required fields."""
import re

REQUIRED = ["name", "email", "phone", "location", "target_roles", "experience_years",
            "education", "work_authorization", "skills"]


class PersonaError(ValueError):
    pass


def validate_resume(r):
    missing = [k for k in REQUIRED if k not in r]
    if missing:
        raise PersonaError(f"résumé missing fields: {missing}")
    if not str(r["email"]).lower().endswith("@example.com"):
        raise PersonaError("refused: email is not @example.com, so this may be a real résumé")
    if not re.search(r"\b555[-.\s]?\d{4}\b", str(r["phone"])):
        raise PersonaError("refused: phone is not a 555 number, so this may be a real résumé")
    if not (isinstance(r["skills"], list) and r["skills"] and all(isinstance(s, str) for s in r["skills"])):
        raise PersonaError("skills must be a non-empty list of strings")
    wa = r["work_authorization"]
    for k in ("country", "us_citizen", "needs_sponsorship"):
        if k not in wa:
            raise PersonaError(f"work_authorization missing {k}")
    if not all("degree" in e for e in r["education"]):
        raise PersonaError("every education entry needs a degree")
    return r
