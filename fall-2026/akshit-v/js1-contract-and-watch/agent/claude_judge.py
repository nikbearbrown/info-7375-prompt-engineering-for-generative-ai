"""The Claude judge: a judgment under a prompt contract, never a record (CONTRACT.md: Out (2)).

Each call is a fresh, tool-less Claude Code CLI session (claude -p) with the
prompt contract as the whole system prompt. The validator rejects any reply
that is not exactly the contracted JSON shape.
"""
import json
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from agent.config import CLAUDE_MODEL
from agent.resume import IDENTITY_FIELDS

VERDICTS = ("relevant", "not_relevant")
KEYS = {"verdict", "cited_resume_fields", "cited_posting_fields", "reason"}
POSTING_FIELDS = ("id", "title", "location.name", "absolute_url", "content")


def resume_for_claude(resume: dict) -> dict:
    """Claude does not need identity fields to judge fit, so it does not get them."""
    return {k: v for k, v in resume.items() if k not in IDENTITY_FIELDS}


def render_system_prompt(template: str, resume_fields) -> str:
    return (template.replace("{RESUME_FIELDS}", ", ".join(resume_fields))
                    .replace("{POSTING_FIELDS}", ", ".join(POSTING_FIELDS)))


def render_user_prompt(posting: dict, resume_view: dict) -> str:
    return (
        "RÉSUMÉ (JSON):\n"
        + json.dumps(resume_view, indent=2, ensure_ascii=False)
        + "\n\nPOSTING:\n"
        + f"id: {posting['id']}\n"
        + f"title: {posting['title']}\n"
        + f"location.name: {posting['location_name']}\n"
        + f"absolute_url: {posting['absolute_url']}\n"
        + f"content: {posting['content_text']}\n"
    )


def validate(text: str, resume_fields) -> tuple[dict | None, str | None]:
    """Return (parsed, None) if the reply meets the contract, else (None, why rejected)."""
    try:
        obj = json.loads(text.strip())
    except json.JSONDecodeError:
        return None, "not a single JSON object (extra text, code fences, or invalid JSON)"
    if not isinstance(obj, dict):
        return None, "JSON is not an object"
    if set(obj) != KEYS:
        missing, extra = KEYS - set(obj), set(obj) - KEYS
        return None, f"wrong keys (missing {sorted(missing)}, extra {sorted(extra)})"
    if obj["verdict"] not in VERDICTS:
        return None, f"verdict {obj['verdict']!r} is not one of {VERDICTS}"
    for key, allowed in (("cited_resume_fields", set(resume_fields)),
                         ("cited_posting_fields", set(POSTING_FIELDS))):
        val = obj[key]
        if not isinstance(val, list) or not val:
            return None, f"{key} must be a non-empty list"
        unknown = [f for f in val if not isinstance(f, str) or f not in allowed]
        if unknown:
            return None, f"{key} names fields that do not exist: {unknown}"
    if not isinstance(obj["reason"], str) or not obj["reason"].strip():
        return None, "reason must be a non-empty string"
    return obj, None


def claude_executable() -> str:
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError("Claude Code CLI not found: npm install -g @anthropic-ai/claude-code, then log in")
    p = Path(exe)
    if p.suffix.lower() == ".cmd":  # Windows npm shim; call the native binary to avoid cmd.exe quoting
        native = p.parent / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
        if native.exists():
            return str(native)
    return exe


def ask_claude(system_prompt: str, user_prompt: str, model: str = CLAUDE_MODEL, timeout: int = 300) -> dict:
    """One fresh, tool-less conversation. Returns the reply text and call metadata."""
    asked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory() as tmp:
        sp = Path(tmp) / "system_prompt.md"
        sp.write_text(system_prompt, encoding="utf-8")
        cmd = [claude_executable(), "-p", "--safe-mode", "--tools", "", "--no-session-persistence",
               "--model", model, "--system-prompt-file", str(sp), "--output-format", "json"]
        proc = subprocess.run(cmd, input=user_prompt, capture_output=True, text=True,
                              encoding="utf-8", timeout=timeout, cwd=tmp)
    meta = {"asked_at_utc": asked_at, "model_requested": model}
    if proc.returncode != 0:
        return {**meta, "call_error": (proc.stderr or proc.stdout).strip()[:500], "raw_text": None}
    env = json.loads(proc.stdout)
    return {
        **meta,
        "models_reported": sorted(env.get("modelUsage", {})),
        "session_id": env.get("session_id"),
        "call_error": env.get("result") if env.get("is_error") else None,
        "raw_text": None if env.get("is_error") else env.get("result", ""),
    }


def judge(posting: dict, resume: dict, template: str, caller=ask_claude) -> dict:
    view = resume_for_claude(resume)
    system_prompt = render_system_prompt(template, list(view))
    result = {"asked_id": posting["id"], "valid": False, "verdict": None}
    try:
        reply = caller(system_prompt, render_user_prompt(posting, view))
    except Exception as e:  # Refuses: skip the bad item and continue
        return {**result, "rejection": f"call failed: {type(e).__name__}: {e}"}
    result.update(reply)
    if reply.get("call_error") or reply.get("raw_text") is None:
        return {**result, "rejection": f"call failed: {reply.get('call_error')}"}
    parsed, why = validate(reply["raw_text"], list(view))
    if parsed is None:
        return {**result, "rejection": why}
    return {**result, "valid": True, "verdict": parsed["verdict"], "parsed": parsed, "rejection": None}


def judge_all(postings: list[dict], resume: dict, template: str, caller=ask_claude, workers: int = 4) -> dict[int, dict]:
    """Ask in parallel; replies are keyed by the id each call was asked about (guards against W1)."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {p["id"]: pool.submit(judge, p, resume, template, caller) for p in postings}
        return {pid: f.result() for pid, f in futures.items()}
