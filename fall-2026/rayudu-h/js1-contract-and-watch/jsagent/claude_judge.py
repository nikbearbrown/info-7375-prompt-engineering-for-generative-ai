"""The second judge: Claude under a prompt contract. Its verdict is a JUDGMENT, never a fact.

Claude runs through `claude -p` (Claude Code, no API key) in a fresh conversation every call:
all tools disabled, no settings/MCP/slash commands, no session saved, in an empty working
directory so no CLAUDE.md is discovered. Only the persona's experience[].title and skills are
sent (CONTRACT.md, Refuses 5). The answer must pass `validate`, or it is rejected.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from . import resume as resume_mod
from .rule import VERDICTS, plain_text

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
MODEL = "sonnet"
MAX_CONTENT_CHARS = 15000
CONFIDENCES = ("low", "medium", "high")
RESUME_FIELDS = ("experience[].title", "skills")
POSTING_FIELDS = ("title", "location.name", "content")
KEYS = {"verdict", "confidence", "resume_fields", "posting_fields", "justification"}
SYSTEM_PROMPT = ("You judge whether a job posting is relevant to a candidate. "
                 "Follow the output contract in the user message exactly.")


def load_prompt(version: str) -> str:
    return (PROMPTS_DIR / f"judge_{version}.md").read_text()


def posting_view(posting: dict) -> dict:
    content = plain_text(posting.get("content") or "")
    return {
        "title": (posting.get("title") or "").strip(),
        "location.name": ((posting.get("location") or {}).get("name") or "").strip(),
        "content": content[:MAX_CONTENT_CHARS],
    }


def build_prompt(version: str, posting: dict, resume: dict) -> str:
    template = load_prompt(version)
    return (template
            .replace("{{RESUME_JSON}}", json.dumps(resume_mod.judge_view(resume), indent=2))
            .replace("{{POSTING_JSON}}", json.dumps(posting_view(posting), indent=2)))


def validate(text: str):
    """Return (parsed, errors). Anything other than exactly one JSON object in the contract's shape is rejected."""
    errors = []
    try:
        data = json.loads(text.strip())
    except (json.JSONDecodeError, AttributeError) as e:
        return None, [f"not a bare JSON object: {e}"]
    if not isinstance(data, dict):
        return None, ["not a JSON object"]
    if set(data) != KEYS:
        errors.append(f"keys must be exactly {sorted(KEYS)}; got {sorted(data)}")
    if data.get("verdict") not in VERDICTS:
        errors.append(f"verdict must be one of {list(VERDICTS)}")
    if data.get("confidence") not in CONFIDENCES:
        errors.append(f"confidence must be one of {list(CONFIDENCES)}")
    for key, allowed in (("resume_fields", RESUME_FIELDS), ("posting_fields", POSTING_FIELDS)):
        val = data.get(key)
        if not isinstance(val, list) or not val or not all(v in allowed for v in val):
            errors.append(f"{key} must be a non-empty list drawn from {list(allowed)}")
    just = data.get("justification")
    if not isinstance(just, str) or not just.strip() or len(just) > 800:
        errors.append("justification must be a non-empty string of at most 800 characters")
    return (data if not errors else None), errors


def ungrounded_quotes(justification: str, posting: dict, resume: dict, prompt: str = "") -> list:
    """Double-quoted phrases in the justification found nowhere in what Claude was shown.

    "What Claude was shown" is the posting, the résumé view, and the prompt itself (which holds
    the rule's words and the field names). Flags the CONTRACT.md failure "a justification
    quotes words that are not in the posting".
    """
    view = posting_view(posting)
    haystack = " ".join([view["title"], view["location.name"], plain_text(posting.get("content") or ""),
                         json.dumps(resume_mod.judge_view(resume), ensure_ascii=False), prompt]).lower()
    haystack = re.sub(r"\s+", " ", haystack)
    quotes = re.findall(r'"([^"]{2,200})"', justification or "")
    return [q for q in quotes if re.sub(r"\s+", " ", q.lower()).strip(" .,;:") not in haystack]


def call_claude(prompt: str, model: str = MODEL, timeout: float = 180.0) -> dict:
    """One fresh conversation. Returns the CLI's JSON envelope plus timing."""
    cmd = ["claude", "-p", prompt, "--model", model, "--tools", "", "--setting-sources", "",
           "--strict-mcp-config", "--no-session-persistence", "--disable-slash-commands",
           "--system-prompt", SYSTEM_PROMPT, "--output-format", "json"]
    started = dt.datetime.now(dt.timezone.utc).astimezone()
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(cmd, cwd=empty, capture_output=True, text=True, timeout=timeout)
    envelope = {}
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError:
        envelope = {"is_error": True, "result": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}
    return {
        "started_at": started.isoformat(timespec="seconds"),
        "exit_code": proc.returncode,
        "model_requested": model,
        "models_used": sorted((envelope.get("modelUsage") or {}).keys()),
        "duration_ms": envelope.get("duration_ms"),
        "is_error": envelope.get("is_error", proc.returncode != 0),
        "result": envelope.get("result", ""),
    }


def judge(posting: dict, resume: dict, version: str = "v2", model: str = MODEL, caller=call_claude) -> dict:
    prompt = build_prompt(version, posting, resume)
    call = caller(prompt, model)
    parsed, errors = validate(call["result"]) if not call["is_error"] else (None, ["claude call failed"])
    record = {
        "kind": "judgment (Claude, not a fact)",
        "posting_id": posting.get("id"),
        "prompt_version": version,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        **call,
        "valid": parsed is not None,
        "errors": errors,
        "judgment": parsed,
    }
    if parsed:
        record["ungrounded_quotes"] = ungrounded_quotes(parsed["justification"], posting, resume, prompt)
    return record
