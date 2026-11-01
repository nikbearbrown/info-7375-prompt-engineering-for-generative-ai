"""Claude as the second judge, under a prompt contract (CONTRACT §3, Step 3).

Its verdict is a MODEL JUDGMENT, never a fact. Every reply goes through validate(); anything that is not
exactly the fixed JSON shape, or that cites evidence absent from the résumé or the posting, is rejected.

Calls go through the Claude Code CLI (`claude -p`) — one fresh, tool-less session per call, run from an
empty temporary directory so no project files, memory, or MCP servers are in context.
"""

import datetime as dt
import json
import subprocess
import tempfile
from pathlib import Path

from .checks import evidence_errors
from .rule import description_text, location_name

LABEL = "MODEL JUDGMENT (Claude) — not a fact"
VERDICTS = {"RELEVANT", "NOT RELEVANT"}
KEYS = {"posting_id", "verdict", "evidence", "reason"}
EVIDENCE_KEYS = {"skill", "resume_field", "posting_quote"}
MAX_CONTENT = 12000
SYSTEM = "You classify job postings for a fixed contract. Output only the JSON object the user asks for."


def build_prompt(template, job, resume):
    skills = {k: v for k, v in resume["skills"].items() if isinstance(v, list) and k != "familiar_with_not_shipped"}
    return template.format(
        resume_skills=json.dumps(skills, indent=1),
        posting_id=str(job["id"]),
        title=job["title"],
        location=location_name(job),
        content=description_text(job)[:MAX_CONTENT],
    )


def validate(reply_text, job, resume):
    """Return (parsed, errors). Any error means the reply is rejected."""
    text = (reply_text or "").strip()
    if not (text.startswith("{") and text.endswith("}")):
        return None, ["reply is not a bare JSON object (prose or code fences around it)"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        return None, [f"invalid JSON: {e}"]
    if not isinstance(parsed, dict) or set(parsed) != KEYS:
        return None, [f"keys {sorted(parsed) if isinstance(parsed, dict) else type(parsed).__name__} != {sorted(KEYS)}"]
    errors = []
    if parsed["posting_id"] != str(job["id"]):
        errors.append(f"posting_id {parsed['posting_id']!r} != {str(job['id'])!r}")
    if parsed["verdict"] not in VERDICTS:
        errors.append(f"verdict {parsed['verdict']!r} not in {sorted(VERDICTS)}")
    if not isinstance(parsed["reason"], str) or not parsed["reason"].strip() or len(parsed["reason"]) > 300:
        errors.append("reason must be a non-empty string of at most 300 characters")
    evidence = parsed["evidence"]
    if not isinstance(evidence, list) or any(not isinstance(e, dict) or set(e) != EVIDENCE_KEYS for e in evidence):
        errors.append(f"evidence must be a list of objects with keys {sorted(EVIDENCE_KEYS)}")
        return parsed, errors
    if any(len(str(e["posting_quote"])) > 200 for e in evidence):
        errors.append("a posting_quote is longer than 200 characters")
    errors += evidence_errors(parsed, job, resume)
    return parsed, errors


def call_claude(prompt, model=None, timeout=240):
    """One fresh `claude -p` session. Returns the CLI's outer JSON (result text, model usage)."""
    cmd = ["claude", "-p", "--output-format", "json", "--tools", "", "--setting-sources", "",
           "--strict-mcp-config", "--no-session-persistence", "--system-prompt", SYSTEM]
    if model:
        cmd += ["--model", model]
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=empty, timeout=timeout)
    try:
        outer = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude CLI gave no JSON (exit {proc.returncode}): {proc.stderr.strip()[:300]}")
    if outer.get("is_error"):
        raise RuntimeError(f"claude CLI error: {outer.get('result')}")
    return outer


def judge(job, resume, template, model=None, log_path=None, tag=""):
    """Ask Claude once; validate; append the full exchange to a JSONL log. Returns the log record."""
    prompt = build_prompt(template, job, resume)
    asked_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    outer = call_claude(prompt, model=model)
    reply = outer.get("result", "")
    parsed, errors = validate(reply, job, resume)
    record = {
        "label": LABEL,
        "tag": tag,
        "asked_at_utc": asked_at,
        "session_id": outer.get("session_id"),
        "models": sorted((outer.get("modelUsage") or {}).keys()),
        "posting_id": str(job["id"]),
        "title": job["title"],
        "reply": reply,
        "valid": not errors,
        "errors": errors,
        "verdict": parsed["verdict"] if parsed and not errors else None,
        "evidence": parsed.get("evidence", []) if parsed and not errors else [],
        "reason": parsed.get("reason") if parsed and not errors else None,
    }
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_template(path):
    return Path(path).read_text()
