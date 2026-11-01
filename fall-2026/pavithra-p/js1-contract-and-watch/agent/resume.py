"""Load the résumé and refuse anything that is not clearly fictional (CONTRACT.md, Refuses 2 and 6)."""
import json
import re

SKILL_LISTS = ("languages", "backend_automation", "database_cloud", "devops_cicd")


class ResumeRefused(Exception):
    """The résumé is not clearly fictional or is missing fields the rule needs."""


def validate(resume):
    problems = []
    personal = resume.get("personal") if isinstance(resume, dict) else None
    if not isinstance(personal, dict):
        raise ResumeRefused("refused: résumé has no 'personal' section")
    if not str(personal.get("name", "")).strip():
        problems.append("no name")
    if not str(personal.get("email", "")).lower().endswith("@example.com"):
        problems.append("email is not at example.com")
    digits = re.sub(r"\D", "", str(personal.get("phone", "")))
    if len(digits) < 7 or digits[-7:-4] != "555":
        problems.append("phone is not a 555 number")
    skills = resume.get("skills")
    for name in SKILL_LISTS:
        values = skills.get(name) if isinstance(skills, dict) else None
        if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values):
            problems.append(f"skills.{name} is missing or empty")
    if not isinstance(resume.get("experience"), list):
        problems.append("experience is missing")
    if problems:
        raise ResumeRefused("refused: " + "; ".join(problems))
    return resume


def load(path):
    with open(path, encoding="utf-8") as f:
        return validate(json.load(f))
