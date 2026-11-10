"""The Claude judge: a judgment under a prompt contract, never a record.

Each call is a fresh, tool-free `claude -p` session run in an empty temporary
directory, so it cannot read project files or earlier conversations. Every
reply is saved verbatim with its date, and anything that is not exactly the
contract's JSON object is rejected as INVALID.
"""

import datetime
import hashlib
import json
import os
import re
import subprocess
import tempfile

from agent import rule

MODEL = "claude-opus-5-5"
POSTING_FIELDS = {"title", "location.name", "content"}
KEYS = {"posting_id", "verdict", "resume_fields", "posting_fields", "reason"}
VERDICTS = {"relevant", "not_relevant"}


def resume_for_prompt(resume):
    """The résumé minus contact details and bookkeeping: Claude does not need
    a name, email or phone to judge fit."""
    drop = {"personal", "_comment", "attested", "attested_date",
            "attestation_note"}
    return {k: v for k, v in resume.items() if k not in drop}


def build_prompt(template, posting, resume):
    return template.format(
        resume_json=json.dumps(resume_for_prompt(resume), indent=2,
                               ensure_ascii=False),
        posting_id=posting["id"],
        title=posting.get("title") or "",
        location=(posting.get("location") or {}).get("name") or "",
        description=rule.description_text(posting))


def run_claude(prompt, model=MODEL, timeout=300):
    """One fresh conversation. Returns the CLI's JSON envelope."""
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json",
             "--tools", "", "--no-session-persistence", "--model", model],
            cwd=empty, capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"is_error": True, "result": proc.stdout[-2000:],
                "stderr": proc.stderr[-2000:]}


def path_exists(data, path):
    """True if a dotted path such as "skills.languages" or
    "experience.title" resolves in data (a list matches if any item does).
    "[0]"-style indexes are accepted and ignored."""
    keys = [k for k in re.sub(r"\[\d+\]", "", path).split(".") if k]
    if not keys:
        return False
    level = [data]
    for key in keys:
        nxt = []
        for node in level:
            items = node if isinstance(node, list) else [node]
            nxt += [i[key] for i in items if isinstance(i, dict) and key in i]
        if not nxt:
            return False
        level = nxt
    return True


def validate(text, posting_id, resume):
    """Return (parsed, errors). parsed is None unless errors is empty."""
    try:
        obj = json.loads(text.strip())
    except (json.JSONDecodeError, AttributeError):
        return None, ["not a single JSON object"]
    if not isinstance(obj, dict):
        return None, ["not a JSON object"]
    errors = []
    if set(obj) != KEYS:
        errors.append(f"keys must be exactly {sorted(KEYS)}, got "
                      f"{sorted(obj)}")
    pid = obj.get("posting_id")
    if type(pid) is not int or pid != posting_id:
        errors.append(f"posting_id {pid!r} is not {posting_id}")
    if obj.get("verdict") not in VERDICTS:
        errors.append(f"verdict {obj.get('verdict')!r} not in "
                      f"{sorted(VERDICTS)}")
    for field, check in (
            ("resume_fields", lambda f: path_exists(resume, f)),
            ("posting_fields", lambda f: f in POSTING_FIELDS)):
        val = obj.get(field)
        if not isinstance(val, list) or not val or not all(
                isinstance(f, str) for f in val):
            errors.append(f"{field} must be a non-empty list of strings")
        else:
            bad = [f for f in val if not check(f)]
            if bad:
                errors.append(f"{field} names fields that do not exist: "
                              f"{bad}")
    if not isinstance(obj.get("reason"), str) or not obj["reason"].strip():
        errors.append("reason must be a non-empty string")
    return (obj if not errors else None), errors


def judge(posting, resume, prompt_path, runner=run_claude, model=MODEL):
    """Ask Claude once. Returns a record that always carries the raw reply."""
    with open(prompt_path, encoding="utf-8") as f:
        template = f.read()
    prompt = build_prompt(template, posting, resume)
    asked_at = datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds")
    envelope = runner(prompt, model=model)
    text = envelope.get("result") or ""
    if envelope.get("is_error"):
        parsed, errors = None, [f"CLI error: {text[:300]}"]
    else:
        parsed, errors = validate(text, posting["id"], resume)
    return {
        "posting_id": posting["id"],
        "judge": "claude",
        "kind": "judgment",
        "verdict": parsed["verdict"] if parsed else "INVALID",
        "parsed": parsed,
        "errors": errors,
        "raw_reply": text,
        "asked_at": asked_at,
        "model_requested": model,
        "models_used": sorted((envelope.get("modelUsage") or {}).keys()),
        "session_id": envelope.get("session_id"),
        "prompt_file": os.path.basename(prompt_path),
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
    }


def save(record, out_dir, name):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path
