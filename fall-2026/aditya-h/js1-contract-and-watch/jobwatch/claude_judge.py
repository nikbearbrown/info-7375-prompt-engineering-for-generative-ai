"""Claude judge under a prompt contract. Its output is a labeled judgment, never a record.

The runner shells out to the `claude` CLI in print mode: a fresh conversation per call, no tools,
no session saved, run from an empty temp directory so no project files or CLAUDE.md are read.
"""
import datetime as dt
import html
import json
import pathlib
import re
import subprocess
import tempfile

from . import fields

KEYS = {"posting_id", "verdict", "resume_fields", "posting_fields", "reason"}
VERDICTS = {"relevant", "not_relevant"}
SYSTEM = "You are a careful job-posting screener. You reply with a single JSON object only."
CONTACT_KEYS = {"name", "email", "phone", "linkedin", "github"}
MAX_CONTENT = 6000


class ClaudeError(Exception):
    pass


def resume_view(resume):
    """The résumé as sent to Claude: same structure (so paths resolve), contact details and metadata removed."""
    view = {k: v for k, v in resume.items() if not k.startswith("_") and not k.startswith("attest")}
    view["personal"] = {k: v for k, v in resume.get("personal", {}).items() if k not in CONTACT_KEYS}
    return view


def posting_view(p):
    text = re.sub(r"<[^>]+>", " ", html.unescape(html.unescape(p.get("content") or "")))
    text = re.sub(r"\s+", " ", text).strip()[:MAX_CONTENT]
    return {
        "id": p.get("id"),
        "title": p.get("title"),
        "location": {"name": (p.get("location") or {}).get("name")},
        "offices": [{"name": o.get("name")} for o in p.get("offices") or []],
        "departments": [{"name": d.get("name")} for d in p.get("departments") or []],
        "content": text,
    }


def render(template, posting, resume):
    return (template.replace("{{RESUME_JSON}}", json.dumps(resume_view(resume), ensure_ascii=False, indent=1))
            .replace("{{POSTING_JSON}}", json.dumps(posting_view(posting), ensure_ascii=False, indent=1))
            .replace("{{POSTING_ID}}", str(posting.get("id"))))


def cli_runner(prompt, model, timeout=180):
    """One fresh `claude -p` conversation. Returns (reply_text, model_id)."""
    with tempfile.TemporaryDirectory() as empty:
        try:
            proc = subprocess.run(
                ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence",
                 "--output-format", "json", "--system-prompt", SYSTEM],
                input=prompt, capture_output=True, text=True, timeout=timeout, cwd=empty)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise ClaudeError(f"claude CLI failed: {e}") from e
    try:
        out = json.loads(proc.stdout)
    except ValueError as e:
        raise ClaudeError(f"claude CLI gave non-JSON output: {proc.stdout[:200]!r} {proc.stderr[:200]!r}") from e
    if out.get("is_error"):
        raise ClaudeError(f"claude CLI error: {out.get('result')}")
    used = list((out.get("modelUsage") or {}).keys())
    return out.get("result", ""), (used[0] if used else model)


def validate(text, posting, resume):
    """Accept exactly the contract's JSON object; anything else is 'invalid' with the raw text kept."""
    errors = []
    try:
        d = json.loads(text.strip())
    except (ValueError, AttributeError):
        return {"status": "invalid", "errors": ["reply is not a single JSON object"], "raw": text}
    if not isinstance(d, dict):
        return {"status": "invalid", "errors": ["reply is not a JSON object"], "raw": text}
    if set(d) != KEYS:
        errors.append(f"keys must be exactly {sorted(KEYS)}; got {sorted(d)}")
    pid = d.get("posting_id")
    if isinstance(pid, bool) or pid != posting.get("id"):
        errors.append(f"posting_id {pid!r} does not match the posting asked about ({posting.get('id')})")
    if d.get("verdict") not in VERDICTS:
        errors.append(f"verdict {d.get('verdict')!r} not in {sorted(VERDICTS)}")
    for key, source in (("resume_fields", resume), ("posting_fields", posting)):
        paths = d.get(key)
        if not isinstance(paths, list) or not paths or not all(isinstance(x, str) for x in paths):
            errors.append(f"{key} must be a non-empty list of field paths")
            continue
        for path in paths:
            try:
                fields.resolve(source, path)
            except KeyError:
                errors.append(f"{key}: {path!r} does not exist")
    if not isinstance(d.get("reason"), str) or not d["reason"].strip():
        errors.append("reason must be a non-empty string")
    if errors:
        return {"status": "invalid", "errors": errors, "raw": text}
    return {"status": "valid", "verdict": d["verdict"], "resume_fields": d["resume_fields"],
            "posting_fields": d["posting_fields"], "reason": d["reason"], "raw": text}


def make_judge(prompt_path, model="sonnet", runner=cli_runner):
    prompt_path = pathlib.Path(prompt_path)
    template = prompt_path.read_text()

    def judge(posting, resume):
        meta = {"judge": "claude", "kind": "judgment", "prompt": prompt_path.name,
                "date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "model": model}
        try:
            text, used = runner(render(template, posting, resume), model)
        except ClaudeError as e:
            return {**meta, "status": "invalid", "errors": [str(e)], "raw": None}
        return {**meta, "model": used, **validate(text, posting, resume)}

    return judge
