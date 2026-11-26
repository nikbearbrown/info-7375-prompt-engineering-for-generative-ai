"""Claude judge under a prompt contract. Output is a judgment, validated or rejected, never repaired."""
import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from .resume import redact_for_model, resolve

DEFAULT_MODEL = os.environ.get("JSAGENT_MODEL", "claude-sonnet-5-5")
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")
KEYS = {"posting_id", "verdict", "resume_fields", "posting_fields", "reason"}
VERDICTS = {"relevant", "not_relevant"}
POSTING_FIELDS = {"title", "location.name", "departments", "content"}
MAX_REASON = 500
# Was 6000 until 2026-10-31 ~17:00: that cut the "10+ years" requirement out of posting 8039914 in Run 2.
MAX_CONTENT = 20000


def build_user_message(posting, r):
    post = {
        "id": posting["id"],
        "title": posting["title"],
        "location": {"name": posting["location"]["name"]},
        "departments": posting["departments"],
        "content": posting["content"][:MAX_CONTENT],
    }
    return ("RESUME (JSON):\n" + json.dumps(redact_for_model(r), indent=1)
            + "\n\nPOSTING (JSON):\n" + json.dumps(post, indent=1))


def validate_output(raw, posting_id, r):
    """Return (parsed, errors). Anything but the exact contract shape is rejected."""
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None, ["output is not a bare JSON object"]
    if not isinstance(obj, dict):
        return None, ["output is not a JSON object"]
    errors = []
    if set(obj) != KEYS:
        errors.append(f"keys must be exactly {sorted(KEYS)}, got {sorted(obj)}")
    if obj.get("posting_id") != posting_id:
        errors.append(f"posting_id {obj.get('posting_id')!r} != {posting_id!r}")
    if obj.get("verdict") not in VERDICTS:
        errors.append(f"verdict {obj.get('verdict')!r} not in {sorted(VERDICTS)}")
    model_view = redact_for_model(r)
    rf = obj.get("resume_fields")
    if not isinstance(rf, list) or not rf:
        errors.append("resume_fields must be a non-empty list")
    else:
        for path in rf:
            try:
                resolve(model_view, path)
            except KeyError:
                errors.append(f"resume field {path!r} does not exist in the résumé given")
    pf = obj.get("posting_fields")
    if not isinstance(pf, list) or not pf:
        errors.append("posting_fields must be a non-empty list")
    elif not set(pf) <= POSTING_FIELDS:
        errors.append(f"posting_fields {pf} not all in {sorted(POSTING_FIELDS)}")
    reason = obj.get("reason")
    if not isinstance(reason, str) or not reason.strip() or len(reason) > MAX_REASON:
        errors.append(f"reason must be a non-empty string of at most {MAX_REASON} characters")
    return (obj if not errors else None), errors


def run_claude_cli(system_prompt, user_message, model):
    """One fresh, tool-less, non-persisted Claude Code conversation. Returns (text, meta)."""
    with tempfile.TemporaryDirectory() as cwd:
        proc = subprocess.run(
            [CLAUDE_BIN, "-p", "--system-prompt", system_prompt, "--tools", "",
             "--no-session-persistence", "--model", model, "--output-format", "json"],
            input=user_message, capture_output=True, text=True, cwd=cwd, timeout=180,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed ({proc.returncode}): {proc.stderr.strip()[:300]}")
    out = json.loads(proc.stdout)
    meta = {k: out.get(k) for k in ["session_id", "total_cost_usd", "duration_ms", "stop_reason"]}
    meta["models_used"] = sorted((out.get("modelUsage") or {}).keys())
    return out.get("result", ""), meta


def judge(posting, r, prompt_path, model=DEFAULT_MODEL, runner=run_claude_cli):
    system_prompt = Path(prompt_path).read_text()
    record = {
        "posting_id": posting["id"],
        "kind": "judgment",
        "label": f"Claude judgment ({model}), not a fact",
        "model": model,
        "prompt": Path(prompt_path).name,
        "date": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    try:
        raw, meta = runner(system_prompt, build_user_message(posting, r), model)
    except Exception as e:  # recorded, never guessed
        return {**record, "status": "error", "errors": [str(e)]}
    record["meta"] = meta
    record["content_chars_sent"] = min(len(posting["content"]), MAX_CONTENT)
    record["content_truncated"] = len(posting["content"]) > MAX_CONTENT
    parsed, errors = validate_output(raw.strip() if isinstance(raw, str) else raw, posting["id"], r)
    if errors:
        return {**record, "status": "rejected", "errors": errors, "raw": raw}
    return {**record, "status": "valid", **{k: parsed[k] for k in sorted(KEYS) if k != "posting_id"}, "raw": raw}
