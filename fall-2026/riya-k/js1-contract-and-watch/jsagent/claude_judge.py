"""The Claude judge: a prompt contract, a fresh headless `claude -p` call, and the validator.

A Claude verdict is a judgment, never a record. Each call is a fresh conversation:
no tools, no MCP servers, no settings, no saved session, run from an empty directory.
"""

import json
import subprocess
import tempfile
from pathlib import Path

from .contract import ContractError, parse_claude_output
from .rules import plain_text

MODEL = "claude-sonnet-5-5"
PROMPTS = Path(__file__).resolve().parent.parent / "experiments" / "prompts"


def build_prompt(template, posting, resume):
    persona = {"skills": resume["skills"], "experience": resume.get("experience", []),
               "projects": resume.get("projects", []), "education": resume.get("education", [])}
    post = {"id": posting["id"], "title": posting.get("title", ""),
            "location.name": (posting.get("location") or {}).get("name", ""),
            "content": plain_text(posting.get("content", ""))[:6000]}
    return (template.replace("{{RESUME_JSON}}", json.dumps(persona, indent=1, ensure_ascii=False))
                    .replace("{{POSTING_JSON}}", json.dumps(post, indent=1, ensure_ascii=False))
                    .replace("{{POSTING_ID}}", str(posting["id"])))


def call_claude(prompt, model=MODEL, timeout=180):
    with tempfile.TemporaryDirectory() as empty:
        out = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence",
             "--strict-mcp-config", "--setting-sources", "", "--output-format", "json"],
            input=prompt, capture_output=True, text=True, cwd=empty, timeout=timeout)
    if out.returncode != 0:
        raise RuntimeError(f"claude -p failed: {out.stderr.strip()[:300]}")
    meta = json.loads(out.stdout)
    return meta["result"], meta.get("session_id")


def judge(posting, resume, prompt_name="v1_baseline.md", model=MODEL):
    """Returns (verdict_or_None, raw_reply, error). Invalid replies are rejected, never repaired."""
    template = (PROMPTS / prompt_name).read_text()
    raw, session = call_claude(build_prompt(template, posting, resume), model)
    try:
        return {**parse_claude_output(raw, posting["id"]), "session_id": session}, raw, None
    except ContractError as e:
        return None, raw, str(e)
