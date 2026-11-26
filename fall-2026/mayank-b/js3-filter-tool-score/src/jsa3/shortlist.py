"""The source-grounded shortlist (FILTER.md section 2).

1. select(): the kept postings, ranked by (role word in title, score), top N (N is hand-set, SCORE.md).
2. justify(): ONE Claude call per posting (claude-haiku-5-5, raw urllib). Claude returns claims C1-C4,
   each with the passage it quotes from the posting text. The model output is saved verbatim with its date.
3. prelabel(): a MECHANICAL check, never a judgment. It can only say "not reviewed" or
   "insufficient (the quoted passage is not in the posting text / no passage quoted)".
   It never says "supported": only Mayank may (FILTER.md 2, WF3).

This is the only module allowed to reach api.anthropic.com. The tool server never imports it.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

API_URL = "https://api.anthropic.com/v1/messages"
API_HOST = "api.anthropic.com"
MODEL = "claude-haiku-5-5"
API_VERSION = "2026-10-21"
EFFORT = "low"          # hand-set (SCORE.md): a short extraction task
MAX_TOKENS = 2000       # hand-set: four claims fit in a few hundred tokens
CLAIMS = {
    "C1": "the role matches Priya's target",
    "C2": "the location is one Priya accepts",
    "C3": "the level fits early-career",
    "C4": "the work uses a skill Priya has (name which one)",
}
SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["claims"],
    "properties": {"claims": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["id", "claim", "quote"],
        "properties": {"id": {"type": "string", "enum": list(CLAIMS)},
                       "claim": {"type": "string"},
                       "quote": {"type": "string"}}}}},
}


def collapse(s) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def select(records: list[dict], n: int) -> list[dict]:
    kept = [r for r in records if r["verdict"] == "keep"]
    return sorted(kept, key=lambda r: (r["role_match"] is None, -(r["score"] or 0), r["board"], r["id"]))[:n]


def prompt(posting: dict, persona: dict) -> str:
    s = persona["search"]
    profile = {"target_titles": s["target_titles"], "exclude_titles": s["exclude_titles"],
               "location": persona["personal"]["location"], "open_to_relocate": s["open_to_relocate"],
               "open_to_remote_us": s["open_to_remote"], "skills": persona["skills"],
               "experience": [e["title"] + " (" + e["start_date"] + " to " + e["end_date"] + ")" for e in persona["experience"]]}
    return (
        "You write a short justification for showing one job posting to a job seeker. "
        "Make exactly four claims, one sentence each, with no 'and' joining two ideas:\n"
        + "\n".join(f"{k}: {v}" for k, v in CLAIMS.items())
        + "\nFor each claim, copy the ONE passage from the posting text (or the title or location line) that best bears on it, "
        "word for word, at most 300 characters. Do not paraphrase the quote. If nothing in the posting bears on a claim, "
        "make the claim anyway and give an empty quote. Say what the posting says, even when it goes against the claim.\n\n"
        f"Job seeker (fictional): {json.dumps(profile)}\n\n"
        f"Posting title: {posting['title']}\nPosting location: {posting['location']}\nPosting text:\n{posting['text']}"
    )


def _api_key(env_path: Path) -> str:
    """Read ANTHROPIC_API_KEY from the environment or a git-ignored .env file. Never printed or logged."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError(f"no ANTHROPIC_API_KEY in the environment or {env_path}")


def call_claude(text: str, env_path: Path, timeout: float = 60) -> dict:
    """One Messages API call. Returns the raw response JSON (the caller saves it)."""
    if urlsplit(API_URL).hostname != API_HOST:
        raise RuntimeError("off-list host")
    body = json.dumps({"model": MODEL, "max_tokens": MAX_TOKENS,
                       "output_config": {"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}},
                       "messages": [{"role": "user", "content": text}]}).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "content-type": "application/json", "x-api-key": _api_key(env_path), "anthropic-version": API_VERSION})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": {"status": e.code, "body": e.read().decode("utf-8", "replace")[:2000]}}


def call_claude_cli(text: str, timeout: float = 180) -> dict:
    """The same prompt through the Claude Code CLI (`claude -p`, my NEU Claude Code account), with no tools,
    no MCP servers and no saved session. Used on 2026-11-25 because the JS1 API key returned 401.
    Returns the CLI's JSON result (saved verbatim by the caller)."""
    import subprocess
    cmd = ["claude", "-p", "--model", MODEL, "--output-format", "json", "--json-schema", json.dumps(SCHEMA),
           "--tools", "", "--no-session-persistence", "--strict-mcp-config"]
    r = subprocess.run(cmd, input=text, capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": {"status": r.returncode, "body": (r.stdout + r.stderr)[-2000:]}}


def claims_from(response: dict) -> list[dict]:
    if "structured_output" in response or response.get("type") == "result":   # Claude Code CLI result
        so = response.get("structured_output")
        if isinstance(so, dict) and isinstance(so.get("claims"), list):
            return so["claims"]
        try:
            return json.loads(response.get("result") or "")["claims"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return []
    if "error" in response or response.get("stop_reason") not in ("end_turn", "max_tokens"):
        return []
    text = "".join(b.get("text", "") for b in response.get("content", []) if b.get("type") == "text")
    try:
        return json.loads(text)["claims"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def quote_found(quote: str, posting: dict) -> bool:
    q = collapse(quote).lower()
    hay = collapse(" ".join([posting.get("title", ""), posting.get("location", ""), posting.get("text") or ""])).lower()
    return bool(q) and q in hay


def prelabel(claim: dict, posting: dict) -> str:
    """Mechanical only. Never 'supported' (WF3 swaps in: 'supported' whenever a topic word matched)."""
    if not collapse(claim.get("quote")):
        return "insufficient (no passage quoted)"
    if not quote_found(claim["quote"], posting):
        return "insufficient (quoted passage not found in the posting text)"
    return "not reviewed"
