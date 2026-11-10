"""Claude judgment for one posting, via the Claude Code CLI (`claude -p`).

The verdict is a judgment, never a record: it is labeled as such in reports
and never overrides the rule verdict. Output that fails validate() is
recorded as "rejected"; if the CLI cannot run, the result is "not run".
Nothing here ever fills in a verdict on Claude's behalf.
"""

import json
import subprocess

from agent.resume import NOT_COUNTED_GROUP, SKILL_GROUPS
from agent.rule import NOT_RELEVANT, RELEVANT, prepare

NOT_RUN = "not run"
REJECTED = "rejected"
JUDGED = "judged"
EXPECTED_KEYS = frozenset(
    {"posting_id", "verdict", "resume_fields", "posting_fields", "reason"})
MAX_CONTENT_CHARS = 12000
CLI_TIMEOUT_SECONDS = 180
CLI_COMMAND = ["claude", "-p", "--output-format", "text", "--tools", ""]


class ClaudeOutputInvalid(Exception):
    """Raised by validate() for output that is not exactly the contract shape."""


def build_prompt(posting, resume, target):
    """Build the prompt contract for one posting. No contact fields included."""
    skills = {f"skills.{g}": resume["skills"].get(g, [])
              for g in SKILL_GROUPS + (NOT_COUNTED_GROUP,)}
    content = prepare(posting.get("content", ""))[:MAX_CONTENT_CHARS]
    schema = ('{"posting_id": <int>, "verdict": "relevant" | "not_relevant", '
              '"resume_fields": [<str>, ...], "posting_fields": [<str>, ...], '
              '"reason": <str>}')
    return "\n".join([
        "You are judging whether one job posting is relevant to a candidate.",
        "Your answer is a judgment; a separate keyword rule is the record.",
        "",
        "Candidate skills (field path: values):",
        *[f"- {path}: {', '.join(values)}" for path, values in skills.items()],
        f"(skills.{NOT_COUNTED_GROUP} were not shipped; weigh them lightly.)",
        f"Target title keywords: {', '.join(target['target_title_keywords'])}",
        f"Excluded terms (any match means not_relevant): "
        f"{', '.join(target['excluded_terms'])}",
        "",
        f"posting.id: {posting['id']}",
        f"posting.title: {prepare(posting.get('title', ''))}",
        f"posting.content: {content}",
        "",
        "Respond with JSON only: no prose, no Markdown, no code fences.",
        f"Exact shape: {schema}",
        f"- posting_id must be {posting['id']}.",
        "- resume_fields: non-empty list of field paths you relied on, each "
        "starting with \"skills.\" or \"target.\" (e.g. \"skills.languages\").",
        "- posting_fields: non-empty list drawn from \"posting.title\", "
        "\"posting.content\".",
        "- reason: one or two sentences.",
    ])


def validate(raw, expected_posting_id):
    """Return the parsed verdict, or raise ClaudeOutputInvalid."""
    if not isinstance(raw, str):
        raise ClaudeOutputInvalid("output is not text")
    try:
        data = json.loads(raw.strip())
    except json.JSONDecodeError as exc:
        raise ClaudeOutputInvalid(f"not JSON-only output: {exc.msg}") from None
    if not isinstance(data, dict):
        raise ClaudeOutputInvalid("top-level JSON is not an object")
    if set(data) != EXPECTED_KEYS:
        extra = sorted(set(data) - EXPECTED_KEYS)
        missing = sorted(EXPECTED_KEYS - set(data))
        raise ClaudeOutputInvalid(f"wrong keys: extra={extra} missing={missing}")
    pid = data["posting_id"]
    if not isinstance(pid, int) or isinstance(pid, bool):
        raise ClaudeOutputInvalid("posting_id is not an int")
    if pid != expected_posting_id:
        raise ClaudeOutputInvalid(
            f"posting_id {pid} does not match {expected_posting_id}")
    if data["verdict"] not in (RELEVANT, NOT_RELEVANT):
        raise ClaudeOutputInvalid(f"unknown verdict {data['verdict']!r}")
    for key, prefixes in (("resume_fields", ("skills.", "target.")),
                          ("posting_fields", ("posting.",))):
        values = data[key]
        if not isinstance(values, list) or not values:
            raise ClaudeOutputInvalid(f"{key} must be a non-empty list")
        for value in values:
            if not isinstance(value, str) or not value.startswith(prefixes):
                raise ClaudeOutputInvalid(
                    f"{key} entry {value!r} must start with {prefixes}")
    if not isinstance(data["reason"], str) or not data["reason"].strip():
        raise ClaudeOutputInvalid("reason must be a non-empty string")
    return data


def run_claude_cli(prompt):
    """Call `claude -p` with the prompt on stdin. Returns stdout, or None.

    Tests replace this function with a fake; it is the only place a
    subprocess is started.
    """
    try:
        result = subprocess.run(CLI_COMMAND, input=prompt, capture_output=True,
                                text=True, timeout=CLI_TIMEOUT_SECONDS,
                                check=False)
    except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def judge(posting, resume, target, runner=None):
    """Return {"status": judged|rejected|not run, "verdict"?, "error"?}."""
    runner = runner or run_claude_cli
    raw = runner(build_prompt(posting, resume, target))
    if raw is None:
        return {"status": NOT_RUN}
    try:
        return {"status": JUDGED, "verdict": validate(raw, posting["id"])}
    except ClaudeOutputInvalid as exc:
        return {"status": REJECTED, "error": str(exc)}
