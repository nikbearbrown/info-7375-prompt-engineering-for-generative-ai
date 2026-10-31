"""claude_judge.py — the second judge: Claude under a prompt contract. Its output is a
JUDGMENT (model), never a record, and never feeds the rule verdict or the counts.

Each call is a fresh conversation: `claude -p` run in an empty temporary directory with
no tools, no settings sources, no MCP servers, no saved session, and the prompt contract
as the whole system prompt. The reply must be exactly one JSON object in the format below;
`validate_reply` rejects anything else. A rejected reply is recorded as REJECTED — never
repaired.

Fixed output format:
    {"posting_id": <int>,
     "verdict": "relevant" | "not_relevant",
     "resume_fields": ["<résumé field path>", ...],          # at least 1
     "posting_evidence": [{"field": "title"|"content", "text": "<exact quote>"}, ...],  # at least 1
     "reason": "<at most 40 words>"}
"""
import json
import os
import subprocess
import tempfile

from rule import plain_text, resume_value

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPTS = os.path.join(HERE, "..", "prompts")
DEFAULT_MODEL = "sonnet"
KEYS = {"posting_id", "verdict", "resume_fields", "posting_evidence", "reason"}
MAX_CONTENT_CHARS = 8000


class ReplyRejected(ValueError):
    pass


def load_prompt(name):
    with open(os.path.join(PROMPTS, f"{name}.md"), encoding="utf-8") as f:
        return f.read()


def user_message(posting, resume):
    content = plain_text(posting.get("content", ""))[:MAX_CONTENT_CHARS]
    return (
        "RÉSUMÉ (JSON):\n" + json.dumps(resume, ensure_ascii=False, indent=1) + "\n\n"
        f"POSTING\nposting_id: {posting['id']}\ntitle: {posting.get('title', '')}\n"
        f"location: {(posting.get('location') or {}).get('name', '')}\n"
        f"content: {content}\n"
    )


def call_claude(system_prompt, message, model=DEFAULT_MODEL, timeout=180):
    """One fresh, tool-less conversation. Returns (reply_text, meta)."""
    with tempfile.TemporaryDirectory(prefix="js1-judge-") as empty:
        proc = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "", "--setting-sources", "",
             "--strict-mcp-config", "--no-session-persistence",
             "--system-prompt", system_prompt, "--output-format", "json"],
            input=message, capture_output=True, text=True, cwd=empty, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()[:300]}")
    envelope = json.loads(proc.stdout)
    meta = {"session_id": envelope.get("session_id"),
            "models_used": sorted(envelope.get("modelUsage", {}) or {}),  # the CLI may also use a small model internally
            "cost_usd": envelope.get("total_cost_usd")}
    return envelope.get("result", ""), meta


def validate_reply(text, posting, resume):
    """Parse and check one reply against the fixed format. Returns the parsed dict or
    raises ReplyRejected. Code fences, prose around the JSON, extra keys: all rejected."""
    try:
        obj = json.loads(text.strip())
    except json.JSONDecodeError as e:
        raise ReplyRejected(f"not a bare JSON object: {e.msg}")
    if not isinstance(obj, dict) or set(obj) != KEYS:
        raise ReplyRejected(f"keys must be exactly {sorted(KEYS)}, got {sorted(obj) if isinstance(obj, dict) else type(obj).__name__}")
    if obj["posting_id"] != posting["id"]:
        raise ReplyRejected(f"posting_id {obj['posting_id']!r} is not the posting asked about ({posting['id']})")
    if obj["verdict"] not in ("relevant", "not_relevant"):
        raise ReplyRejected(f"verdict {obj['verdict']!r} not in relevant|not_relevant")
    rf = obj["resume_fields"]
    if not isinstance(rf, list) or not rf:
        raise ReplyRejected("resume_fields must be a non-empty list")
    for path in rf:
        if not isinstance(path, str) or not isinstance(resume_value(resume, path), str):
            raise ReplyRejected(f"résumé field {path!r} does not exist or is not a single value")
    ev = obj["posting_evidence"]
    if not isinstance(ev, list) or not ev:
        raise ReplyRejected("posting_evidence must be a non-empty list")
    fields = {"title": posting.get("title", ""), "content": plain_text(posting.get("content", ""))}
    for item in ev:
        if not isinstance(item, dict) or item.get("field") not in fields or not isinstance(item.get("text"), str):
            raise ReplyRejected(f"bad posting_evidence item {item!r}")
        if not item["text"].strip() or item["text"].lower() not in fields[item["field"]].lower():
            raise ReplyRejected(f"quoted text {item['text'][:60]!r} not found in posting {item['field']}")
    if not isinstance(obj["reason"], str) or len(obj["reason"].split()) > 40:
        raise ReplyRejected("reason must be a string of at most 40 words")
    return obj


def judge(posting, resume, prompt_name="baseline", model=DEFAULT_MODEL):
    """Returns a record of one Claude judgment — ACCEPTED, REJECTED, or CALL_FAILED; never repaired."""
    rec = {"posting_id": posting["id"], "source": "claude", "label": "JUDGMENT (model)",
           "prompt": prompt_name, "model_requested": model}
    try:
        reply, meta = call_claude(load_prompt(prompt_name), user_message(posting, resume), model)
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as e:
        rec.update(status="CALL_FAILED", verdict=None, reject_reason=f"claude call failed: {e}"[:300])
        return rec
    rec.update(raw_reply=reply, **meta)
    try:
        obj = validate_reply(reply, posting, resume)
        rec.update(status="ACCEPTED", verdict=obj["verdict"], resume_fields=obj["resume_fields"],
                   posting_evidence=obj["posting_evidence"], reason=obj["reason"])
    except ReplyRejected as e:
        rec.update(status="REJECTED", verdict=None, reject_reason=str(e))
    return rec
