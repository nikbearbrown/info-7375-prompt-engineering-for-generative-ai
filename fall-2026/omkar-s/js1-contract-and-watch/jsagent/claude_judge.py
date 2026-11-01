"""The second judge: Claude under a prompt contract. Its output is a JUDGMENT, never a
fact (CONTRACT.md, Refuses 3), and it is accepted only if the validator passes.

Each call is `claude -p` in an empty temporary directory with no tools, no settings,
no MCP servers and no saved session, so every call is a fresh conversation that can
read nothing but the prompt.
"""
import datetime as _dt
import json
import os
import subprocess
import tempfile

from . import persona as _persona
from .rule import clean_content

JUDGMENT_LABEL = "Claude judgment - not a fact"
VERDICTS = ("relevant", "not_relevant")
REQUIRED_KEYS = {"posting_id", "verdict", "resume_fields", "posting_fields", "reason"}
RESUME_FIELDS = {
    "personal.location", "education[].degree", "education[].end_date", "education[].coursework",
    "experience[].title", "experience[].bullets", "projects[]",
    "skills.languages", "skills.backend_automation", "skills.database_cloud",
    "skills.devops_cicd", "skills.familiar_with_not_shipped",
}
POSTING_FIELDS = {"title", "location.name", "departments", "content"}
MAX_REASON = 500
DEFAULT_MODEL = os.environ.get("JSAGENT_MODEL", "sonnet")


def posting_for_model(posting):
    return {
        "posting_id": str(posting["id"]),
        "title": posting.get("title"),
        "location.name": (posting.get("location") or {}).get("name"),
        "departments": [d.get("name") for d in posting.get("departments") or []],
        "content": clean_content(posting.get("content")),
    }


def build_prompt(template, posting, resume):
    return (template
            .replace("{{RESUME_JSON}}", json.dumps(_persona.for_model(resume), indent=1))
            .replace("{{POSTING_JSON}}", json.dumps(posting_for_model(posting), indent=1))
            .replace("{{POSTING_ID}}", str(posting["id"])))


def validate(text, expected_id):
    """Return (parsed, None) if `text` meets the output contract exactly, else (None, reason).

    No repair: code fences, prose around the JSON, extra keys or unknown field names
    are all rejections.
    """
    s = (text or "").strip()
    if not s.startswith("{") or not s.endswith("}"):
        return None, "output is not a bare JSON object (prose or code fence around it)"
    try:
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e.msg}"
    if not isinstance(obj, dict):
        return None, "top level is not an object"
    keys = set(obj)
    if keys != REQUIRED_KEYS:
        return None, f"keys {sorted(keys)} != {sorted(REQUIRED_KEYS)}"
    if obj["posting_id"] != str(expected_id):
        return None, f"posting_id {obj['posting_id']!r} != {str(expected_id)!r}"
    if obj["verdict"] not in VERDICTS:
        return None, f"verdict {obj['verdict']!r} not in {VERDICTS}"
    for key, allowed in (("resume_fields", RESUME_FIELDS), ("posting_fields", POSTING_FIELDS)):
        v = obj[key]
        if not isinstance(v, list) or not v or not all(isinstance(x, str) for x in v):
            return None, f"{key} must be a non-empty list of strings"
        unknown = [x for x in v if x not in allowed]
        if unknown:
            return None, f"{key} has unknown field names {unknown}"
    if not isinstance(obj["reason"], str) or not obj["reason"].strip():
        return None, "reason must be a non-empty string"
    if len(obj["reason"]) > MAX_REASON:
        return None, f"reason longer than {MAX_REASON} characters"
    return obj, None


def call_claude(prompt, model=DEFAULT_MODEL, timeout=300):
    """One fresh `claude -p` conversation. Returns the CLI's JSON envelope (dict)."""
    cmd = ["claude", "-p", "--model", model, "--output-format", "json",
           "--tools", "", "--setting-sources", "", "--strict-mcp-config",
           "--disable-slash-commands", "--no-session-persistence"]
    with tempfile.TemporaryDirectory(prefix="jsagent-claude-") as empty_dir:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                              cwd=empty_dir, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()[:300]}")
    return json.loads(proc.stdout)


def judge(posting, resume, template, caller=call_claude, raw_dir=None, tag=""):
    """Ask Claude once and validate. Never coerces a rejected answer into a verdict."""
    prompt = build_prompt(template, posting, resume)
    at = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    envelope = caller(prompt)
    text = envelope.get("result", "")
    parsed, why = validate(text, posting["id"])
    models = sorted((envelope.get("modelUsage") or {}).keys())
    raw_path = None
    if raw_dir:
        os.makedirs(raw_dir, exist_ok=True)
        raw_path = os.path.join(raw_dir, f"{tag}{posting['id']}.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump({"asked_at": at, "envelope": envelope}, f, indent=1)
    out = {
        "kind": "judgment",
        "label": JUDGMENT_LABEL,
        "asked_at": at,
        "models": models,
        "session_id": envelope.get("session_id"),
        "raw_path": raw_path,
        "status": "valid" if parsed else "rejected",
        "verdict": parsed["verdict"] if parsed else None,
    }
    if parsed:
        out.update(resume_fields=parsed["resume_fields"], posting_fields=parsed["posting_fields"],
                   reason=parsed["reason"])
    else:
        out["rejection"] = why
    return out
