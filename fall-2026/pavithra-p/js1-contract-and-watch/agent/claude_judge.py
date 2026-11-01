"""Claude's opinion under a prompt contract (CONTRACT.md, Out). Its verdict is a judgment, never a fact.

Each call is a fresh `claude -p` conversation with no tools, a fixed system prompt and a fixed model, run
from an empty folder so no project instructions are loaded. Every reply is saved as it came back.
"""
import hashlib
import json
import string
import subprocess
import tempfile
from datetime import datetime, timezone

from . import rule
from .resume import SKILL_LISTS

MODEL = "claude-sonnet-5-5"
SYSTEM = ("You judge job postings for a candidate. Follow the user's instructions exactly "
          "and reply with one JSON object only.")
KIND = "judgment (Claude, prompt contract)"
KEYS = {"verdict", "posting_fields", "resume_fields", "reason"}
POSTING_FIELDS = {"title", "location", "description"}
RESUME_FIELDS = {f"skills.{s}" for s in SKILL_LISTS} | {"experience", "education", "personal.location"}
COMMAND = ["claude", "-p", "--output-format", "json", "--tools", "", "--system-prompt", SYSTEM,
           "--model", MODEL, "--no-session-persistence", "--strict-mcp-config", "--setting-sources", ""]


class InvalidReply(Exception):
    """The reply does not match the fixed format. It is saved and reported as invalid, never repaired."""


def validate(text):
    stripped = (text or "").strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        raise InvalidReply("text outside the JSON object")
    try:
        data = json.loads(stripped)
    except ValueError as e:
        raise InvalidReply(f"invalid JSON ({e})") from None
    if not isinstance(data, dict) or set(data) != KEYS:
        raise InvalidReply(f"keys must be exactly {sorted(KEYS)}")
    if data["verdict"] not in ("Relevant", "Not Relevant"):
        raise InvalidReply(f"verdict {data['verdict']!r} is not Relevant or Not Relevant")
    for key, allowed in (("posting_fields", POSTING_FIELDS), ("resume_fields", RESUME_FIELDS)):
        values = data[key]
        if not isinstance(values, list) or not values or not all(isinstance(v, str) and v in allowed for v in values):
            raise InvalidReply(f"{key} must be a non-empty list drawn from {sorted(allowed)}")
    reason = data["reason"]
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 300 or "\n" in reason:
        raise InvalidReply("reason must be one line of 1-300 characters")
    return data


def resume_block(resume):
    keep = {"personal": {"location": resume["personal"].get("location")},
            "education": [{k: e.get(k) for k in ("degree", "institution", "end_date")} for e in resume.get("education", [])],
            "experience": [{k: x.get(k) for k in ("title", "company", "start_date", "end_date")}
                           for x in resume.get("experience", [])],
            "skills": {name: resume["skills"][name] for name in SKILL_LISTS}}
    return json.dumps(keep, indent=2, ensure_ascii=False)


def posting_block(job):
    location = (job.get("location") or {}).get("name", "")
    return f"title: {job.get('title', '')}\nlocation: {location}\ndescription:\n{rule.description_text(job).strip()}"


def build_prompt(template_text, job, resume):
    return string.Template(template_text).substitute(resume=resume_block(resume), posting=posting_block(job))


def call_claude(prompt, run=subprocess.run, timeout=300):
    """One fresh conversation. Returns the CLI's JSON envelope (the reply text is its 'result')."""
    with tempfile.TemporaryDirectory() as empty:
        done = run(COMMAND, input=prompt, capture_output=True, text=True, cwd=empty, timeout=timeout)
    if done.returncode != 0:
        return {"is_error": True, "result": "", "error": (done.stderr or done.stdout or "").strip()[:2000]}
    return json.loads(done.stdout)


def judge(job, resume, template_path, run=subprocess.run, now=None):
    template_text = template_path.read_text(encoding="utf-8")
    prompt = build_prompt(template_text, job, resume)
    at = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    envelope = call_claude(prompt, run=run)
    reply = envelope.get("result", "")
    record = {"kind": KIND, "at": at, "job_id": job["id"], "prompt_file": template_path.name,
              "prompt_sha256": hashlib.sha256(template_text.encode()).hexdigest(),
              "prompt_sent_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
              "model_requested": MODEL, "models_used": list((envelope.get("modelUsage") or {}).keys()),
              "session_id": envelope.get("session_id"), "cli_error": envelope.get("error") if envelope.get("is_error") else None,
              "reply": reply, "valid": False, "error": None, "parsed": None}
    try:
        record["parsed"] = validate(reply)
        record["valid"] = True
    except InvalidReply as e:
        record["error"] = str(e)
    return record


def save(record, out_dir, name):
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
