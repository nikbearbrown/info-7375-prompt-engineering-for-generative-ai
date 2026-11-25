"""The Claude judge. Its output is a judgment, not a record: label it so.

Each call is a fresh, tool-less Claude Code headless session (`claude -p`),
run from an empty temp folder so no project files or settings are read. Every
call, valid or not, is appended to a log with its date, model, and session id.
"""
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agent import resume as resume_mod, rule

MODEL = "claude-sonnet-5-5"
ROOT = Path(__file__).resolve().parent.parent
VERDICTS = {"relevant", "not relevant"}
KEYS = {"verdict", "resume_fields", "posting_fields", "reason"}
POSTING_FIELDS = {"posting.title", "posting.location.name", "posting.content"}
RESUME_FIELD = re.compile(r"^resume\.(skills(\.(languages|frontend|database_cloud|devops_cicd))?"
                          r"|experience|education|projects|personal\.location)$")


class InvalidOutput(Exception):
    pass


def validate(text):
    """Accept exactly one JSON object in the contract's format, or raise."""
    try:
        obj = json.loads(text.strip())
    except json.JSONDecodeError as e:
        raise InvalidOutput(f"not a single JSON object: {e}") from e
    if not isinstance(obj, dict):
        raise InvalidOutput("output is not a JSON object")
    if set(obj) != KEYS:
        raise InvalidOutput(f"keys must be exactly {sorted(KEYS)}, got {sorted(obj)}")
    if obj["verdict"] not in VERDICTS:
        raise InvalidOutput(f"verdict must be one of {sorted(VERDICTS)}, got {obj['verdict']!r}")
    for key, ok in (("resume_fields", RESUME_FIELD.match), ("posting_fields", POSTING_FIELDS.__contains__)):
        vals = obj[key]
        if not isinstance(vals, list) or not vals:
            raise InvalidOutput(f"{key} must be a non-empty list (a justification that cites nothing)")
        bad = [v for v in vals if not isinstance(v, str) or not ok(v)]
        if bad:
            raise InvalidOutput(f"{key} cites fields that don't exist: {bad}")
    reason = obj["reason"]
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 300:
        raise InvalidOutput("reason must be a non-empty string under 300 characters")
    return obj


def build_prompt(template, posting, resume_data):
    skills = ", ".join(s for _, s in resume_mod.counted_skills(resume_data)) or "(none listed)"
    content = " ".join(rule.posting_text(posting).split()[len((posting.get("title") or "").split()):])
    return template.format(skills=skills, title=(posting.get("title") or "").strip(),
                           location=((posting.get("location") or {}).get("name") or "").strip(),
                           content=content)


def call_claude(prompt, model=MODEL, timeout=300):
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", model, "--tools", "", "--strict-mcp-config",
             "--no-session-persistence", "--output-format", "json"],
            cwd=empty, capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"is_error": True, "result": (proc.stdout or proc.stderr)[-2000:]}


def judge(posting, resume_data, template_path, log_path, model=MODEL, tag=""):
    template_path = Path(template_path)
    prompt = build_prompt(template_path.read_text(), posting, resume_data)
    when = datetime.now(timezone.utc).isoformat(timespec="seconds")
    meta = call_claude(prompt, model=model)
    raw = meta.get("result", "")
    entry = {"at": when, "tag": tag, "posting_id": posting.get("id"), "posting_title": posting.get("title"),
             "prompt_file": template_path.name, "model_requested": model,
             "models_used": list((meta.get("modelUsage") or {}).keys()),
             "session_id": meta.get("session_id"), "cli_error": bool(meta.get("is_error")),
             "raw_output": raw, "judge": "claude", "label": "judgment"}
    try:
        if meta.get("is_error"):
            raise InvalidOutput(f"CLI error: {raw[:200]}")
        entry.update(valid=True, **validate(raw))
    except InvalidOutput as e:
        entry.update(valid=False, rejected_because=str(e), verdict=None)
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry
