"""Claude's verdict under a prompt contract. Its output is a judgment, never the record."""
import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

from . import validate

MODEL = "claude-sonnet-5-5"
POSTING_KEYS = ("id", "title", "location", "employmentType", "address", "descriptionPlain")


def load_prompt(path):
    return Path(path).read_text(encoding="utf-8")


def build_prompt(template, posting, resume):
    slim = {k: posting[k] for k in POSTING_KEYS if k in posting}
    return (template.replace("{{RESUME}}", json.dumps(resume, indent=2, ensure_ascii=False))
                    .replace("{{POSTING}}", json.dumps(slim, indent=2, ensure_ascii=False)))


def ask_claude(prompt, model=MODEL):
    """One fresh, tool-less conversation: no tools, no settings, no MCP, no saved session."""
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError("claude CLI not found on PATH")
    cmd = [exe, "-p", "--model", model, "--tools", "", "--setting-sources", "",
           "--strict-mcp-config", "--no-session-persistence", "--output-format", "json"]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr[:300]}")
    meta = json.loads(proc.stdout)
    return meta["result"], {"model": ",".join(meta.get("modelUsage", {})) or model,
                            "session_id": meta.get("session_id"), "cost_usd": meta.get("total_cost_usd")}


def parse_and_validate(text, posting, resume):
    """The fixed format is exactly one JSON object and nothing else; anything else is rejected."""
    try:
        v = json.loads(text.strip())
    except json.JSONDecodeError as e:
        return None, [f"not valid JSON: {e.msg}"]
    errs = validate.errors(v, posting, resume)
    return (None, errs) if errs else (v, [])


def judge(posting, resume, template, model=MODEL, ask=ask_claude):
    text, meta = ask(build_prompt(template, posting, resume), model)
    v, errs = parse_and_validate(text, posting, resume)
    out = {"posting_id": posting["id"], "title": posting.get("title"), "kind": "judgment",
           "model": meta["model"], "date": date.today().isoformat(), "raw": text, "meta": meta}
    if errs:
        out.update(valid=False, errors=errs, verdict=None)
    else:
        out.update(valid=True, errors=[], verdict=v["verdict"], justification=v["justification"],
                   resume_fields=v["resume_fields"], posting_fields=v["posting_fields"])
    return out
