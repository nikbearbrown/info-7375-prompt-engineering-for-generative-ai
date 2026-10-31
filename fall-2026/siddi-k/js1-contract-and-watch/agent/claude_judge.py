"""Claude judgment (CONTRACT.md, Claude judgment): the `claude` CLI in a fresh empty temp dir, a strict validator,
one identical retry, and never a repaired or invented answer."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import POSTING_FIELDS, RESUME_FIELDS

PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
MAX_CONTENT = 6000
VERDICTS = ("relevant", "not_relevant")
KEYS = {"verdict", "justification", "cited_resume_fields", "cited_posting_fields"}


def fill_prompt(template: str, persona: dict, title: str, location: str, req_text: str) -> str:
    values = {"target_title_keywords": json.dumps(persona["target_title_keywords"]),
              "skills": json.dumps(persona["skills"]),
              "years_experience": str(persona["years_experience"]),
              "highest_degree": persona["highest_degree"],
              "preferred_cities": json.dumps(persona["preferred_cities"]),
              "remote_ok": json.dumps(persona["remote_ok"]),
              "title": title, "location": location, "content": req_text[:MAX_CONTENT]}

    def sub(m):
        if m.group(1) not in values:
            raise KeyError(f"prompt template names an unknown field {{{{{m.group(1)}}}}}")
        return values[m.group(1)]

    return PLACEHOLDER.sub(sub, template)      # one pass, so text inside a posting is never re-substituted


def run_claude(argv, prompt: str, timeout: float = 300.0) -> tuple[bytes, str | None]:
    """Run argv with the prompt on stdin (UTF-8 bytes) from a new empty temp dir; return raw stdout bytes."""
    exe = shutil.which(argv[0])
    if exe is None:
        return b"", f"{argv[0]!r} not found on PATH"
    with tempfile.TemporaryDirectory(prefix="js1-claude-", ignore_cleanup_errors=True) as tmp:
        try:
            proc = subprocess.run([exe, *argv[1:]], input=prompt.encode("utf-8"), capture_output=True,
                                  cwd=tmp, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            return e.stdout or b"", f"timed out after {timeout:.0f}s"
    if proc.returncode != 0:
        return proc.stdout, f"exit code {proc.returncode}: {proc.stderr.decode('utf-8', 'replace').strip()[:200]}"
    return proc.stdout, None


def _no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate keys {keys}")
    return dict(pairs)


def validate_output(stdout: bytes):
    """(answer, None) if stdout meets the output contract exactly, else (None, reason). Nothing is repaired."""
    try:
        envelope = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None, "stdout is not a UTF-8 JSON envelope"
    if not isinstance(envelope, dict) or envelope.get("is_error") is not False:
        return None, "error envelope (is_error is not false)"
    result = envelope.get("result")
    if not isinstance(result, str):
        return None, "envelope has no result string"
    try:
        answer = json.loads(result, object_pairs_hook=_no_duplicate_keys)
    except ValueError:
        return None, "result is not exactly one JSON object"
    if not isinstance(answer, dict) or set(answer) != KEYS:
        return None, f"result keys are not exactly {sorted(KEYS)}"
    if answer["verdict"] not in VERDICTS:
        return None, f"verdict {answer['verdict']!r} is not relevant/not_relevant"
    j = answer["justification"]
    if not isinstance(j, str) or not 1 <= len(j) <= 400:
        return None, "justification is not a 1-400 character string"
    for key, allowed in (("cited_resume_fields", RESUME_FIELDS), ("cited_posting_fields", POSTING_FIELDS)):
        v = answer[key]
        if not isinstance(v, list) or not v or not all(isinstance(x, str) and x in allowed for x in v):
            return None, f"{key} is empty or names a field outside {list(allowed)}"
    return answer, None


def judge(cfg, persona: dict, posting: dict, req_text: str, run_dir: Path, root: Path):
    """Returns (line fields, failure record or None). stdout of every attempt is saved unmodified."""
    prompt = fill_prompt(cfg.prompt_template, persona, posting["title"], posting["location"], req_text)
    paths, reasons = [], []
    for name in (f"claude_{posting['id']}.json", f"claude_{posting['id']}_retry1.json"):
        out, note = run_claude(cfg.claude_argv, prompt)
        (run_dir / name).write_bytes(out)
        paths.append((run_dir / name).relative_to(root).as_posix())
        answer, reason = validate_output(out)
        if answer:
            return {"claude_status": "ok", "claude_verdict": answer["verdict"], "claude_label": "judgment",
                    "claude_justification": answer["justification"],
                    "claude_cited_resume_fields": answer["cited_resume_fields"],
                    "claude_cited_posting_fields": answer["cited_posting_fields"], "claude_raw_paths": paths}, None
        reasons.append(reason + (f" ({note})" if note else ""))
    return {"claude_status": "invalid_output", "claude_verdict": None, "claude_label": "judgment",
            "claude_justification": None, "claude_cited_resume_fields": None, "claude_cited_posting_fields": None,
            "claude_raw_paths": paths}, {"reason": " | ".join(reasons), "raw_paths": paths}
