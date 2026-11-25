"""The shortlist's claims: Claude drafts them, the code checks each quote, the student labels them.

Claude is called through the student's Claude Code login, the way JS1's judge was
(jobwatch/transports.py at 99a7443): `claude -p` with no tools, no settings, no MCP servers,
no session saved, from an empty folder. The prompt is prompts/claims-v1.md, written by Claude
Code (Chapter 9: a hand-set object). Every raw reply is saved before it is read."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from jobwatch import evidence

DEFAULT_MODEL = "claude-opus-5-5"
KINDS = ("work", "location", "new_grads", "qualification", "work_authorization", "sponsorship")
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "claims-v1.md"


class ClaimsError(Exception):
    pass


def prompt_parts(path=PROMPT_PATH):
    text = Path(path).read_text(encoding="utf-8")
    system, user = text.split("# User", 1)
    return system.replace("# System", "", 1).strip(), user.strip()


def build_prompt(item, path=PROMPT_PATH):
    system, user = prompt_parts(path)
    filled = (user.replace("{board}", item.board).replace("{key}", item.key)
              .replace("{captured_at}", item.captured_at).replace("{title}", item.title)
              .replace("{location}", item.location or "(blank)")
              .replace("{text}", evidence.plain(item.description)))
    return system, filled


def claude_code_send(model=DEFAULT_MODEL, *, runner=subprocess.run):
    def send(system, user):
        command = ["claude", "-p", "--model", model, "--system-prompt", system, "--tools", "",
                   "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands",
                   "--no-session-persistence", "--output-format", "json"]
        env = dict(os.environ, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
        with tempfile.TemporaryDirectory(prefix="jobwatch-claims-") as empty_dir:
            done = runner(command, input=user, capture_output=True, text=True, cwd=empty_dir, env=env, timeout=600)
        return {"command": command, "returncode": done.returncode, "stdout": done.stdout, "stderr": done.stderr}
    return send


def parse_reply(stdout):
    """claude -p --output-format json -> the claims list. Raises ClaimsError on anything else."""
    try:
        out = json.loads(stdout)
    except ValueError:
        raise ClaimsError("claude -p did not print JSON") from None
    if not isinstance(out, dict) or out.get("is_error") or not isinstance(out.get("result"), str):
        raise ClaimsError("claude -p reported an error instead of a reply")
    text = out["result"].strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.S)
    if fenced:
        text = fenced.group(1)
    try:
        claims = json.loads(text)["claims"]
    except (ValueError, KeyError, TypeError):
        raise ClaimsError("the reply is not the requested JSON shape") from None
    if not isinstance(claims, list):
        raise ClaimsError("claims is not a list")
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("kind") not in KINDS or not isinstance(claim.get("claim"), str):
            raise ClaimsError(f"a claim does not follow the shape: {claim!r}")
    return claims


def checked(item, claims):
    """Each claim with the quote check against the field it names (or the whole posting if none)."""
    fields = {"title": item.title, "location": item.location or "", "description": evidence.plain(item.description)}
    rows = []
    for n, claim in enumerate(claims, start=1):
        field = claim.get("source_field")
        text = fields.get(field) if field in fields else " ".join(fields.values())
        rows.append({"n": n, "kind": claim["kind"], "claim": claim["claim"], "quote": claim.get("quote"),
                     "source_field": field, "quote_check": evidence.check_quote(text, claim.get("quote")),
                     "board": item.board, "key": item.key, "captured_at": item.captured_at})
    return rows
