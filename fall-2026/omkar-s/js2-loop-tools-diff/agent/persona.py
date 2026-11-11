"""Résumé validation (CONTRACT.md, In + Refuses 2).

The agent only accepts a fictional persona. A résumé that looks real is refused
before anything is fetched or printed.
"""
import json
import re

SHIPPED_GROUPS = ("languages", "backend_automation", "database_cloud", "devops_cicd")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")


class RefusedResume(Exception):
    pass


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def problems(resume):
    """Return a list of reasons to refuse; an empty list means valid."""
    out = []
    if not isinstance(resume, dict):
        return ["résumé is not a JSON object"]
    if "FICTIONAL" not in str(resume.get("_comment", "")):
        out.append("_comment does not mark the persona as FICTIONAL")
    personal = resume.get("personal")
    if not isinstance(personal, dict) or not isinstance(personal.get("location"), str):
        out.append("personal.location missing")
    if not isinstance(resume.get("experience"), list):
        out.append("experience[] missing")
    skills = resume.get("skills")
    if not isinstance(skills, dict):
        out.append("skills missing")
    else:
        for g in SHIPPED_GROUPS:
            if not isinstance(skills.get(g), list) or not all(isinstance(s, str) for s in skills[g]):
                out.append(f"skills.{g} must be a list of strings")
    for s in _strings(resume):
        for email in EMAIL.findall(s):
            if not email.lower().endswith("@example.com"):
                out.append(f"non-example e-mail address present ({email.split('@')[-1]})")
        for phone in PHONE.findall(s):
            if "555" not in re.sub(r"\D", "", phone)[3:6]:
                out.append("phone number without a 555 exchange present")
    return out


def load(path):
    with open(path, encoding="utf-8") as f:
        resume = json.load(f)
    errs = problems(resume)
    if errs:
        # Never echo the résumé itself, only the reasons.
        raise RefusedResume("résumé refused: " + "; ".join(errs))
    return resume


def shipped_skills(resume):
    """[(group, skill)] in résumé order; familiar_with_not_shipped is excluded by design."""
    return [(g, s) for g in SHIPPED_GROUPS for s in resume["skills"][g]]


def for_model(resume):
    """The résumé as shown to Claude: no contact block, nothing it doesn't need to judge."""
    keep = {k: resume[k] for k in ("education", "experience", "projects", "skills") if k in resume}
    keep["personal"] = {"location": resume["personal"]["location"]}
    return keep
