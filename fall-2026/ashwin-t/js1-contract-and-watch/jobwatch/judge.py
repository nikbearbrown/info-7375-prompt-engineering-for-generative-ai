"""Claude's separate verdict, under a prompt contract, and the validator (CONTRACT.md, Out 3).

Whatever comes back is an AI JUDGMENT. A reply that passes validation is traceable,
not proven correct, and it never replaces the RULE RECORD.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from .rule import NOT_RELEVANT, RELEVANT, location_fields, posting_id
from .text import find_phrase, normalize

REPLY_KEYS = {"posting_id", "verdict", "reason", "evidence"}
EVIDENCE_KEYS = {"resume_field", "posting_field", "posting_quote"}
POSTING_FIELDS = {"title", "content", "location.name", "offices[].name"}
_RESUME_FIELD = re.compile(r"^([a-z_]+)(?:\[(\d+)\])?$")

VALID = "VALID"
VALIDATION_FAILED = "UNAVAILABLE — VALIDATION FAILED"
CALL_FAILED = "UNAVAILABLE — CALL FAILED"
NOT_REQUESTED = "NOT REQUESTED"


def load_prompt(path: Path) -> tuple:
    path = Path(path)
    template = path.read_text(encoding="utf-8")
    for marker in ("<<RESUME_JSON>>", "<<POSTING_JSON>>"):
        if marker not in template:
            raise ValueError(f"prompt {path} is missing {marker}")
    return path.stem, template


def posting_view(posting: dict) -> dict:
    """What Claude sees: public posting fields only, with the HTML already removed."""
    return {
        "posting_id": posting_id(posting),
        "title": posting["title"],
        "location.name": (posting.get("location") or {}).get("name"),
        "offices[].name": [o.get("name") for o in posting.get("offices") or []],
        "content": normalize(posting.get("content")),
    }


def build_prompt(template: str, posting: dict, resume: dict) -> str:
    return (template
            .replace("<<RESUME_JSON>>", json.dumps(resume, indent=2, ensure_ascii=False))
            .replace("<<POSTING_JSON>>", json.dumps(posting_view(posting), indent=2, ensure_ascii=False)))


def call_claude(prompt: str, model: Optional[str] = None, timeout: float = 300.0,
                runner: Callable = subprocess.run) -> dict:
    """One fresh, tool-free Claude Code session (`claude -p`), run from an empty folder."""
    called_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cmd = ["claude", "-p", "--output-format", "json", "--tools", "", "--no-session-persistence",
           "--setting-sources", "", "--strict-mcp-config"]
    if model:
        cmd += ["--model", model]
    with tempfile.TemporaryDirectory(prefix="js1-claude-") as empty:
        try:
            done = runner(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=empty)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"ok": False, "error": f"claude call failed: {exc}", "called_at": called_at}
    if done.returncode != 0:
        return {"ok": False, "error": f"claude exited {done.returncode}: {done.stderr.strip()[:300]}",
                "called_at": called_at}
    try:
        envelope = json.loads(done.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "claude output was not a JSON envelope", "called_at": called_at,
                "stdout": done.stdout}
    if envelope.get("is_error"):
        return {"ok": False, "error": f"claude reported an error: {envelope.get('result')}",
                "called_at": called_at}
    return {"ok": True, "text": envelope.get("result", ""), "called_at": called_at,
            "model": ",".join(sorted(envelope.get("modelUsage") or {})) or model,
            "session_id": envelope.get("session_id")}


def _field_texts(posting: dict, field: str) -> list:
    if field == "title":
        return [normalize(posting["title"])]
    if field == "content":
        return [normalize(posting.get("content"))]
    wanted = "posting.location.name" if field == "location.name" else "posting.offices[].name"
    return [normalize(v) for f, v in location_fields(posting) if f == wanted]


def _resume_value(resume: dict, ref: str):
    """Resolve 'skills[0]' or 'experience_level'. Raises KeyError if it is not a real field."""
    m = _RESUME_FIELD.match(ref)
    if not m or m.group(1) not in resume:
        raise KeyError(ref)
    value = resume[m.group(1)]
    if m.group(2) is None:
        return m.group(1), None, value
    index = int(m.group(2))
    if not isinstance(value, list) or index >= len(value):
        raise KeyError(ref)
    return m.group(1), index, value[index]


def validate_reply(text: str, posting: dict, resume: dict) -> tuple:
    """Return (parsed reply or None, list of errors). Rejects; never repairs."""
    try:
        reply = json.loads(text.strip())
    except (json.JSONDecodeError, AttributeError):
        return None, ["reply is not a single JSON object (rule 1)"]
    if not isinstance(reply, dict):
        return None, ["reply is not a JSON object (rule 1)"]
    errors = []
    if set(reply) != REPLY_KEYS:
        errors.append(f"top-level keys must be exactly {sorted(REPLY_KEYS)}, got {sorted(reply)} (rule 1)")
    rid = reply.get("posting_id")
    if isinstance(rid, bool) or not isinstance(rid, (str, int)) or str(rid) != posting_id(posting):
        errors.append(f"posting_id {rid!r} does not match {posting_id(posting)!r} (rule 2)")
    if reply.get("verdict") not in (RELEVANT, NOT_RELEVANT):
        errors.append(f"verdict {reply.get('verdict')!r} is not RELEVANT or NOT_RELEVANT (rule 3)")
    if not isinstance(reply.get("reason"), str) or not reply["reason"].strip():
        errors.append("reason must be a nonempty string (rule 4)")
    evidence = reply.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a nonempty array (rule 5)")
        evidence = []
    for i, item in enumerate(evidence):
        where = f"evidence[{i}]"
        if not isinstance(item, dict) or set(item) != EVIDENCE_KEYS:
            errors.append(f"{where} must have exactly {sorted(EVIDENCE_KEYS)} (rule 5)")
            continue
        try:
            key, index, value = _resume_value(resume, str(item["resume_field"]))
        except KeyError:
            errors.append(f"{where}.resume_field {item['resume_field']!r} is not a real résumé field (rule 6)")
            continue
        field = item["posting_field"]
        if not isinstance(field, str) or field not in POSTING_FIELDS:
            errors.append(f"{where}.posting_field {field!r} is not allowed (rule 7)")
            continue
        quote = item["posting_quote"]
        texts = _field_texts(posting, field)
        if not isinstance(quote, str) or not normalize(quote):
            errors.append(f"{where}.posting_quote must be a nonempty string (rule 8)")
        elif not any(normalize(quote) in t for t in texts):
            errors.append(f"{where}.posting_quote {quote!r} does not appear in posting.{field} (rule 8)")
        if key == "skills" and index is not None and not any(find_phrase(value, t) for t in texts):
            errors.append(f"{where} cites skill {value!r}, which is not a valid match in posting.{field} (rule 9)")
    return (reply if not errors else None), errors


def judge(posting: dict, resume: dict, prompt_name: str, template: str,
          caller: Optional[Callable] = None) -> dict:
    """Ask once and validate. With no caller, the judgment is recorded as NOT REQUESTED."""
    base = {"label": "AI JUDGMENT", "posting_id": posting_id(posting), "prompt": prompt_name}
    if caller is None:
        return {**base, "status": NOT_REQUESTED, "verdict": None}
    result = caller(build_prompt(template, posting, resume))
    base.update({"called_at": result.get("called_at"), "model": result.get("model"),
                 "raw_reply": result.get("text")})
    if not result.get("ok"):
        return {**base, "status": CALL_FAILED, "verdict": None, "errors": [result.get("error")]}
    reply, errors = validate_reply(result["text"], posting, resume)
    if errors:
        return {**base, "status": VALIDATION_FAILED, "verdict": None, "errors": errors}
    return {**base, "status": VALID, "verdict": reply["verdict"], "reason": reply["reason"],
            "evidence": reply["evidence"], "errors": []}
