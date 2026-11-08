"""Load and validate the fictional persona: résumé JSON plus target fields.

The agent refuses to run on anything that does not look like a fictional
example persona (CONTRACT.md, Refuses: never show a real résumé).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESUME_PATH = HERE / "persona" / "priya-nair.resume.example.json"
TARGETS_PATH = HERE / "persona" / "priya-nair.targets.json"


class PersonaError(ValueError):
    pass


def _require(condition, message):
    if not condition:
        raise PersonaError(message)


def _fictional_marker(data, what):
    _require(isinstance(data, dict), f"{what}: top level must be a JSON object")
    _require("FICTIONAL" in str(data.get("_comment", "")),
             f"{what}: _comment must mark the persona FICTIONAL")


def validate_resume(data):
    _fictional_marker(data, "résumé")
    personal = data.get("personal")
    _require(isinstance(personal, dict), "résumé: personal must be an object")
    for key in ("name", "location", "email", "phone"):
        _require(isinstance(personal.get(key), str) and personal[key].strip(),
                 f"résumé: personal.{key} must be a non-empty string")
    _require(personal["email"].lower().endswith("@example.com"),
             "résumé: personal.email must be an @example.com address")
    _require("555" in personal["phone"], "résumé: personal.phone must be a 555 number")
    for key in ("education", "experience"):
        _require(isinstance(data.get(key), list) and data[key],
                 f"résumé: {key} must be a non-empty list")
    for i, job in enumerate(data["experience"]):
        _require(isinstance(job, dict) and isinstance(job.get("title"), str),
                 f"résumé: experience[{i}].title must be a string")
    _require(isinstance(data.get("skills"), dict), "résumé: skills must be an object")
    return data


def validate_targets(data, resume):
    _fictional_marker(data, "targets")
    _require(data.get("persona") == resume["personal"]["name"],
             "targets: persona must match résumé personal.name")
    role = data.get("target_role")
    _require(isinstance(role, dict), "targets: target_role must be an object")
    for key in ("primary", "secondary"):
        _require(isinstance(role.get(key), str) and role[key].strip(),
                 f"targets: target_role.{key} must be a non-empty string")
    geo = data.get("geography")
    _require(isinstance(geo, dict), "targets: geography must be an object")
    _require(isinstance(geo.get("current_location"), str) and geo["current_location"].strip(),
             "targets: geography.current_location must be a non-empty string")
    _require(isinstance(geo.get("open_to_remote"), bool),
             "targets: geography.open_to_remote must be true or false")
    visa = data.get("visa")
    _require(isinstance(visa, dict), "targets: visa must be an object")
    for key in ("type", "current_status"):
        _require(isinstance(visa.get(key), str) and visa[key].strip(),
                 f"targets: visa.{key} must be a non-empty string")
    return data


def load_persona(resume_path=RESUME_PATH, targets_path=TARGETS_PATH):
    resume = validate_resume(json.loads(Path(resume_path).read_text(encoding="utf-8")))
    targets = validate_targets(json.loads(Path(targets_path).read_text(encoding="utf-8")), resume)
    return resume, targets
