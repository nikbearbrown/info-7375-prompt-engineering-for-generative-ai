"""The Claude judge, carried over from JS1 (agent/claude_judge.py): render, validate, judge.

Used by the held-out experiments (experiments/one_change.py). One call per posting, keyed by the
id it was asked about. The validator rejects anything but the contracted JSON shape; a rejected
reply is recorded as invalid, never repaired.

The three ways an experiment can change what Claude sees, one at a time:
  template      the system prompt file (prompts/judge_v1.md vs judge_v2_abstain.md)
  extra_context text appended to the user message (e.g. the filter's score)
  mcp_servers   the tool list (no servers vs the js3-filter server with score_posting)
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agent3.claude import ask_claude_isolated
from agent3.resume import IDENTITY_FIELDS

KEYS = {"verdict", "cited_resume_fields", "cited_posting_fields", "reason"}
POSTING_FIELDS = ("id", "title", "location", "url", "employment_type", "content")
ROOT = Path(__file__).resolve().parent.parent


def resume_for_claude(resume: dict) -> dict:
    """Claude does not need identity fields to judge fit, so it does not get them (JS1)."""
    return {k: v for k, v in resume.items() if k not in IDENTITY_FIELDS}


def render_system_prompt(template: str, resume_fields) -> str:
    return (template.replace("{RESUME_FIELDS}", ", ".join(resume_fields))
                    .replace("{POSTING_FIELDS}", ", ".join(POSTING_FIELDS)))


def render_user_prompt(posting: dict, resume_view: dict, extra_context: str = "") -> str:
    msg = ("RÉSUMÉ (JSON):\n" + json.dumps(resume_view, indent=2, ensure_ascii=False)
           + "\n\nPOSTING:\n"
           + f"id: {posting['id']}\n"
           + f"title: {posting['title']}\n"
           + f"location: {posting['location']}\n"
           + f"url: {posting['url']}\n"
           + f"employment_type: {posting.get('employment_type') or '(this board has no such field)'}\n"
           + f"content: {posting['content_text']}\n")
    return msg + (f"\n{extra_context}\n" if extra_context else "")


def verdicts_allowed(template: str) -> tuple:
    return ("relevant", "not_relevant", "cannot_tell") if '"cannot_tell"' in template else ("relevant", "not_relevant")


def validate(text: str, resume_fields, verdicts) -> tuple:
    try:
        obj = json.loads((text or "").strip())
    except json.JSONDecodeError:
        return None, "not a single JSON object (extra text, code fences, or invalid JSON)"
    if not isinstance(obj, dict):
        return None, "JSON is not an object"
    if set(obj) != KEYS:
        return None, f"wrong keys (missing {sorted(KEYS - set(obj))}, extra {sorted(set(obj) - KEYS)})"
    if obj["verdict"] not in verdicts:
        return None, f"verdict {obj['verdict']!r} is not one of {verdicts}"
    for key, allowed in (("cited_resume_fields", set(resume_fields)), ("cited_posting_fields", set(POSTING_FIELDS))):
        val = obj[key]
        if not isinstance(val, list) or not val:
            return None, f"{key} must be a non-empty list"
        unknown = [f for f in val if not isinstance(f, str) or f not in allowed]
        if unknown:
            return None, f"{key} names fields that do not exist: {unknown}"
    if not isinstance(obj["reason"], str) or not obj["reason"].strip():
        return None, "reason must be a non-empty string"
    return obj, None


def js3_tool_server() -> dict:
    """The tool-list condition: my MCP server, exactly as in scripts/claude_as_client.py."""
    return {"js3-filter": {"type": "stdio", "command": sys.executable,
                           "args": ["-B", "-m", "agent3.mcp_server", "--transcript-name", "judge_tool_condition"],
                           "env": {"PYTHONPATH": str(ROOT)}}}


def judge(posting, resume, template, extra_context="", mcp_servers=None, allowed_tools=(), caller=ask_claude_isolated):
    view = resume_for_claude(resume)
    verdicts = verdicts_allowed(template)
    result = {"asked_id": posting["id"], "valid": False, "verdict": None}
    try:
        reply = caller(render_system_prompt(template, list(view)), render_user_prompt(posting, view, extra_context),
                       mcp_servers=mcp_servers, allowed_tools=allowed_tools)
    except Exception as e:  # skip the bad item and continue (JS1 Refuses)
        return {**result, "rejection": f"call failed: {type(e).__name__}: {e}"}
    result.update(reply)
    if reply.get("call_error") or reply.get("raw_text") is None:
        return {**result, "rejection": f"call failed: {reply.get('call_error')}"}
    parsed, why = validate(reply["raw_text"], list(view), verdicts)
    if parsed is None:
        return {**result, "rejection": why}
    return {**result, "valid": True, "verdict": parsed["verdict"], "parsed": parsed, "rejection": None}


def judge_all(postings, resume, template, workers=4, contexts=None, **kw) -> dict:
    """Replies keyed by the id each call was asked about, never by position (JS1 W1).

    contexts: optional {posting id: extra context string}, so each posting gets its own.
    """
    contexts = contexts or {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {p["id"]: pool.submit(judge, p, resume, template, extra_context=contexts.get(p["id"], ""), **kw)
                   for p in postings}
        return {pid: f.result() for pid, f in futures.items()}
