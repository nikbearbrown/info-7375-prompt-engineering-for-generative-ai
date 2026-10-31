"""The Claude verdict (labeled `judgment`), via `claude -p`."""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

from agent import rule

PROJECT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT / "prompts" / "baseline.txt"
RESPONSES_DIR = PROJECT / "claude_responses"
TIMEOUT_SECONDS = 120

KEYS = {"verdict", "resume_fields", "posting_fields", "reason"}
VERDICTS = {"relevant", "not_relevant"}
NOT_RUN = "Claude verdict: not run"
NO_VERDICT = "no Claude verdict"
PLACEHOLDER = re.compile(r"\{(resume_without_personal_info|posting)\}")


def _string_list(value):
    return isinstance(value, list) and bool(value) and all(isinstance(v, str) and v for v in value)


def validate(text):
    """Return the parsed verdict dict if Claude's reply is valid, else None.

    Valid means the whole reply is one JSON object with exactly the keys
    `verdict` (known value), `resume_fields` and `posting_fields`
    (non-empty lists), and `reason` (non-empty string).
    """
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict) or set(data) != KEYS:
        return None
    if data["verdict"] not in VERDICTS:
        return None
    if not _string_list(data["resume_fields"]) or not _string_list(data["posting_fields"]):
        return None
    if not isinstance(data["reason"], str) or not data["reason"].strip():
        return None
    return data


def build_prompt(posting, resume):
    """Fill the template with the résumé minus `personal` and the posting with HTML removed."""
    resume_safe = {k: v for k, v in resume.items() if k != "personal"}
    lines = (line.strip() for line in rule.content_text(posting).splitlines())
    posting_view = {
        "id": posting.get("id"),
        "title": posting.get("title"),
        "location": {"name": (posting.get("location") or {}).get("name")},
        "content": "\n".join(line for line in lines if line),
    }
    values = {
        "resume_without_personal_info": json.dumps(resume_safe, indent=2, ensure_ascii=False),
        "posting": json.dumps(posting_view, indent=2, ensure_ascii=False),
    }
    # One pass, so a placeholder inside posting text is never filled.
    return PLACEHOLDER.sub(lambda m: values[m.group(1)], PROMPT_PATH.read_text())


def not_run(why):
    return {"label": "judgment", "status": NOT_RUN, "error": why}


def _save_reply(posting, stdout):
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    path = RESPONSES_DIR / f"{posting.get('id')}_{datetime.now().astimezone():%Y%m%dT%H%M%S_%f}.json"
    path.write_text(stdout)
    return str(path.relative_to(RESPONSES_DIR.parent))


def _result_text(proc):
    """The `result` text from `--output-format json`, or None if Claude failed."""
    if proc.returncode != 0:
        return None
    try:
        envelope = json.loads(proc.stdout)
    except ValueError:
        return None
    if not isinstance(envelope, dict) or envelope.get("is_error"):
        return None
    result = envelope.get("result")
    return result if isinstance(result, str) else None


def judge(posting, resume):
    """Ask Claude for a verdict. Always returns a dict labeled `judgment`."""
    prompt = build_prompt(posting, resume)
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return not_run("claude command not found")
    except subprocess.TimeoutExpired:
        return {"label": "judgment", "status": NO_VERDICT, "error": f"timed out after {TIMEOUT_SECONDS} s"}

    raw_file = _save_reply(posting, proc.stdout)
    verdict = validate(_result_text(proc))
    if verdict is None:
        return {"label": "judgment", "status": NO_VERDICT, "raw_file": raw_file}
    return {"label": "judgment", "status": "ok", **verdict, "raw_file": raw_file}
