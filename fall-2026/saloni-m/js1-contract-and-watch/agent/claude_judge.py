"""Claude under a prompt contract (CONTRACT.md "Out" 2). Output is a judgment, never a record.

Each call is a fresh, tool-less `claude -p` conversation. Set CLAUDE_BIN to the CLI path and
CLAUDE_MODEL to pin the model (default claude-sonnet-5-5).
"""
import html
import json
import os
import re
import subprocess
import tempfile

from agent.resume import field_exists

ALLOWED_KEYS = {"verdict", "resume_fields", "posting_fields", "reason"}
VERDICTS = {"relevant", "not_relevant"}
POSTING_FIELDS = {"title", "location.name", "content", "departments"}
CONTENT_CHARS = 4000


class ValidationError(ValueError):
    pass


def plain_text(content):
    text = html.unescape(html.unescape(content or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def posting_view(posting):
    return {
        "title": posting.get("title"),
        "location.name": (posting.get("location") or {}).get("name"),
        "departments": [d.get("name") for d in posting.get("departments") or []],
        "content": plain_text(posting.get("content"))[:CONTENT_CHARS],
    }


def resume_view(resume):
    """What Claude sees of the résumé: no contact details."""
    return {k: resume[k] for k in ("education", "experience", "projects", "skills", "search") if k in resume}


def build_prompt(posting, resume, prompt_path):
    with open(prompt_path, encoding="utf-8") as f:
        template = f.read()
    return (template
            .replace("{{RESUME_JSON}}", json.dumps(resume_view(resume), indent=2))
            .replace("{{POSTING_JSON}}", json.dumps(posting_view(posting), indent=2)))


def validate_claude_output(text, resume):
    """Accept exactly one JSON object with the contract's keys; reject anything else."""
    try:
        obj = json.loads(text.strip())
    except json.JSONDecodeError as e:
        raise ValidationError(f"not a bare JSON object: {e.msg}")
    if not isinstance(obj, dict):
        raise ValidationError("not a JSON object")
    if set(obj) != ALLOWED_KEYS:
        raise ValidationError(f"keys must be exactly {sorted(ALLOWED_KEYS)}, got {sorted(obj)}")
    if obj["verdict"] not in VERDICTS:
        raise ValidationError(f"verdict must be one of {sorted(VERDICTS)}")
    for key in ("resume_fields", "posting_fields"):
        if not isinstance(obj[key], list) or not obj[key] or not all(isinstance(x, str) for x in obj[key]):
            raise ValidationError(f"{key} must be a non-empty list of strings")
    missing = [f for f in obj["resume_fields"] if not field_exists(resume, f)]
    if missing:
        raise ValidationError(f"resume_fields name fields that do not exist: {missing}")
    bad = [f for f in obj["posting_fields"] if f not in POSTING_FIELDS]
    if bad:
        raise ValidationError(f"posting_fields must be among {sorted(POSTING_FIELDS)}, got {bad}")
    if not isinstance(obj["reason"], str) or not obj["reason"].strip():
        raise ValidationError("reason must be a non-empty string")
    return obj


def call_claude(prompt):
    bin_ = os.environ.get("CLAUDE_BIN", "claude")
    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
    # Run from an empty temp dir so no project CLAUDE.md or settings leak into the conversation.
    with tempfile.TemporaryDirectory() as cwd:
        proc = subprocess.run(
            [bin_, "-p", prompt, "--model", model, "--output-format", "json", "--tools", ""],
            cwd=cwd, capture_output=True, text=True, timeout=300,
        )
    meta = json.loads(proc.stdout)
    if meta.get("is_error"):
        raise RuntimeError(f"claude CLI error: {meta.get('result')}")
    return meta["result"], {"session_id": meta.get("session_id"), "model": model,
                            "models_used": sorted(meta.get("modelUsage", {}))}


def judge_claude(posting, resume, prompt_path="prompts/v1_baseline.md", caller=call_claude):
    prompt = build_prompt(posting, resume, prompt_path)
    raw, meta = caller(prompt)
    out = {"id": posting["id"], "kind": "judgment", "prompt": prompt_path, "raw": raw, **meta}
    try:
        out.update(validate_claude_output(raw, resume))
        out["status"] = "ok"
    except ValidationError as e:
        out["status"] = "rejected"
        out["error"] = str(e)
    return out
