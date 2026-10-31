"""Load a resume JSON and refuse anything that is not marked as a fictional persona."""
import json
from pathlib import Path

from . import Refused


def fictional_problems(resume):
    personal = resume.get("personal", {})
    problems = []
    if not str(personal.get("email", "")).endswith("@example.com"):
        problems.append("personal.email does not end in @example.com")
    if "555" not in str(personal.get("phone", "")):
        problems.append("personal.phone has no 555 number")
    if "FICTIONAL" not in str(resume.get("_comment", "")):
        problems.append("_comment does not say FICTIONAL")
    return problems


def load_resume(path):
    try:
        resume = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise Refused(f"the system does not accept this resume file: {e}") from e
    if not isinstance(resume, dict):
        raise Refused("the system does not accept this resume file: not a JSON object")
    problems = fictional_problems(resume)
    if problems:
        raise Refused("the system does not accept a real resume (" + "; ".join(problems) + ")")
    return resume
