"""The Claude judge: one fresh `claude -p` call per posting, every raw reply saved.

Its verdict is a judgment, never a record. If the CLI is missing or not logged in,
the judge records "not run" instead of failing the whole run.
"""
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agent import ROOT, rules

PROMPT_PATH = ROOT / "prompts" / "baseline.md"
# No tools: the judge only reads the prompt it is given (the chat surface of Chapter 3).
ARGS = ["-p", "--output-format", "json", "--tools", ""]


def build_prompt(template, resume, posting):
    view = {
        "id": posting["id"],
        "title": rules.field_text(posting, "title"),
        "location.name": rules.field_text(posting, "location.name"),
        "content": rules.field_text(posting, "content"),
    }
    return (template
            .replace("{{RESUME_JSON}}", json.dumps(resume, indent=2, ensure_ascii=False))
            .replace("{{POSTING_JSON}}", json.dumps(view, indent=2, ensure_ascii=False)))


def not_run(reason):
    return {"status": "not run", "reason": reason}


def judge(posting, resume, out_dir, template=None, runner=subprocess.run, which=shutil.which):
    exe = which("claude")
    if not exe:
        return not_run("claude CLI not found on PATH")

    prompt = build_prompt(template or PROMPT_PATH.read_text(encoding="utf-8"), resume, posting)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / str(posting["id"])
    stem.with_suffix(".prompt.md").write_text(prompt, encoding="utf-8", newline="\n")

    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        # An empty working directory keeps this repository's CLAUDE.md out of the judge's context.
        with tempfile.TemporaryDirectory() as cwd:
            proc = runner([exe, *ARGS], input=prompt, capture_output=True, text=True,
                          encoding="utf-8", timeout=300, cwd=cwd)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return not_run(f"claude CLI could not be run: {exc.__class__.__name__}")

    stem.with_suffix(".reply.json").write_text(proc.stdout or "", encoding="utf-8", newline="")
    try:
        reply = json.loads(proc.stdout)
    except ValueError:
        reply = {}
    model = next(iter(reply.get("modelUsage") or {}), None)
    meta = {
        "date": started,
        "session_id": reply.get("session_id"),
        "model": model,
        "returncode": proc.returncode,
        "is_error": reply.get("is_error"),
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "stderr": (proc.stderr or "")[:2000],
    }
    stem.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8", newline="\n")

    if proc.returncode != 0 or not reply or reply.get("is_error"):
        # Not logged in, or any other CLI failure: the judge did not run, and the run goes on.
        return dict(not_run(str(reply.get("result") or proc.stderr or "no readable reply")[:500]), meta=meta)
    return {"status": "ran", "result": reply.get("result"), "meta": meta}
