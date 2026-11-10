"""Claude JUDGMENT via the authenticated Claude Code CLI, one fresh isolated session per call.

Isolation: an empty temporary working directory, no tools (`--tools ""`), no MCP servers,
no settings sources, no slash commands, no session persistence, and our own system prompt.
The CLI still adds its own environment block (account email, working directory, platform);
temperature is not controllable through the CLI and is not set.
"""
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .rules import html_to_text, resume_skill_entries

ROOT = Path(__file__).resolve().parent.parent
MODEL = "claude-opus-5-5"
EFFORT = "medium"
TIMEOUT_S = 300


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_prompt(version):
    path = ROOT / "prompts" / f"judge_{version}.md"
    text = path.read_text(encoding="utf-8")
    return text, sha256_text(text)


def build_user_message(posting, resume):
    """Only the four permitted résumé arrays are sent (no contact details), plus the posting."""
    payload_resume = resume_skill_entries(resume)
    payload_posting = {
        "posting_id": posting.get("id"),
        "title": posting.get("title") or "",
        "location": (posting.get("location") or {}).get("name"),
        "departments": [d.get("name") for d in posting.get("departments") or []],
        "description": html_to_text(posting.get("content")),
    }
    return (
        "<resume_skills>\n" + json.dumps(payload_resume, ensure_ascii=False, indent=1) + "\n</resume_skills>\n\n"
        "<posting>\n" + json.dumps(payload_posting, ensure_ascii=False, indent=1) + "\n</posting>\n\n"
        "Apply the rule to this posting and reply with the JSON object only."
    )


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def cli_version():
    try:
        return subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"


def call_claude(system_prompt, user_message, model=MODEL, effort=EFFORT, timeout=TIMEOUT_S):
    """One fresh, tool-less, history-less call. Returns a provenance record (never raises on model errors)."""
    workdir = tempfile.mkdtemp(prefix="js1-judge-")
    argv = [
        "claude", "-p",
        "--model", model,
        "--effort", effort,
        "--tools", "",
        "--strict-mcp-config",
        "--setting-sources", "",
        "--disable-slash-commands",
        "--no-session-persistence",
        "--output-format", "json",
        "--system-prompt", system_prompt,
    ]
    record = {
        "invoked_at_utc": _now(),
        "argv": argv[:-1] + [f"<system prompt sha256={sha256_text(system_prompt)}>"],
        "model_requested": model,
        "effort": effort,
        "temperature": "not set (not controllable via the Claude Code CLI)",
        "user_message": user_message,
        "user_message_sha256": sha256_text(user_message),
    }
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, input=user_message, capture_output=True, text=True, timeout=timeout, cwd=workdir)
        record["returncode"] = proc.returncode
        record["stderr_tail"] = proc.stderr[-2000:]
        try:
            record["cli_json"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            record["cli_json"] = None
            record["stdout_raw"] = proc.stdout[-5000:]
    except subprocess.TimeoutExpired:
        record["returncode"] = None
        record["cli_json"] = None
        record["transport_error"] = f"timeout after {timeout}s"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    record["finished_at_utc"] = _now()
    record["wall_seconds"] = round(time.monotonic() - started, 2)
    cj = record.get("cli_json") or {}
    record["response_text"] = cj.get("result") if isinstance(cj.get("result"), str) else None
    record["models_used"] = sorted((cj.get("modelUsage") or {}).keys())
    record["session_id"] = cj.get("session_id")
    record["transport_ok"] = bool(proc_ok(record))
    return record


def proc_ok(record):
    cj = record.get("cli_json") or {}
    return record.get("returncode") == 0 and not cj.get("is_error") and isinstance(cj.get("result"), str)
