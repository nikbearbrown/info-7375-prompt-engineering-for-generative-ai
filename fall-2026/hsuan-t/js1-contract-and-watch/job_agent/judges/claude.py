"""The Claude judge (judgment, R18): asks the model about one posting and keeps only answers the validator accepts.

Why it is shaped this way: the model's reply is untrusted text, so it only becomes a verdict
through validator.validate(), and judge/kind are written by verdict.py, never taken from the reply
(Wrong version 5). The network call is a plain `ask(system, user)` function handed in from
outside, so this file runs the same through Claude Code (claude_cli), the API (claude_api) or a
test fake.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import verdict
from ..common.errors import ClaudeCallError
from ..common.posting import Posting
from .checks import Criteria
from .validator import Rejected, validate
from .words import strip_html

JUDGE = "claude"
MODEL = "claude-sonnet-5-5"   # PLAN 2026-10-30: judge model chosen by Isaac; both phone lines use it


@dataclass(frozen=True)
class Reply:
    """What came back, kept whole so a rejected answer can still be read later (sampling report)."""
    text: str
    stop_reason: str | None
    meta: dict = field(default_factory=dict)   # via, model, usage, request/session id


Ask = Callable[[str, str], Reply]


@dataclass(frozen=True)
class Prompt:
    """The system prompt plus its file name, so every saved answer says which prompt produced it (Step 9)."""
    name: str
    text: str

    @classmethod
    def load(cls, path: Path) -> "Prompt":
        return cls(path.stem, path.read_text())


@dataclass(frozen=True)
class ClaudeResult:
    verdict: dict
    raw: dict    # the reply as received, kept even when rejected (evidence for the sampling report)


def shown_fields(posting: Posting) -> dict[str, str]:
    """What Claude is shown, by CONTRACT field name. The JD goes without HTML: fewer tokens, and the
    validator checks quotes against this same text."""
    return {"title": posting.title, "location.name": posting.location, "content": strip_html(posting.content).strip()}


def user_message(posting: Posting, criteria: Criteria) -> str:
    fields = shown_fields(posting)
    return json.dumps({
        "posting": {"posting_id": posting.id, **fields},
        "resume": criteria.resume,
        "profile": criteria.profile,
    }, ensure_ascii=False, indent=1)


def judge(posting: Posting, criteria: Criteria, ask: Ask, prompt: Prompt) -> ClaudeResult:
    raw = {"posting_id": posting.id, "prompt": prompt.name}
    # Same rule as the rule judge: with no JD there is nothing to quote, so don't pay for a call.
    if not shown_fields(posting)["content"]:
        return ClaudeResult(verdict.error(JUDGE, posting.id, "posting.content is empty, Claude judge cannot run"), raw)
    try:
        reply = ask(prompt.text, user_message(posting, criteria))
    except ClaudeCallError as e:
        return ClaudeResult(verdict.error(JUDGE, posting.id, str(e)), {**raw, "error": str(e)})
    raw.update(text=reply.text, stop_reason=reply.stop_reason, **reply.meta)
    # A refused or cut-off reply is not an answer, even if its text happens to parse.
    if reply.stop_reason != "end_turn":
        return ClaudeResult(verdict.error(JUDGE, posting.id, f"Claude stopped with {reply.stop_reason!r}, not a full answer"), raw)
    try:
        v, lines = validate(reply.text, posting.id, shown_fields(posting))
    except Rejected as e:
        # CONTRACT: rejected -> status error, not_relevant, the reason in error_message, no retry.
        return ClaudeResult(verdict.error(JUDGE, posting.id, f"rejected by validator: {e}"), raw)
    return ClaudeResult(verdict.ok(JUDGE, posting.id, v, lines), raw)


def judge_new(postings: list[Posting], criteria: Criteria, ask: Ask | None, prompt: Prompt,
              no_ask_reason: str = "") -> list[ClaudeResult]:
    """Judge every new posting (R18: each new posting gets a rule AND a Claude verdict). ask=None
    means Claude can't run at all (e.g. claude CLI missing): each posting gets an error verdict so
    the run still finishes with the rule's verdicts (CONTRACT In)."""
    results = []
    for p in postings:
        if ask is None:
            results.append(ClaudeResult(verdict.error(JUDGE, p.id, no_ask_reason), {"posting_id": p.id, "error": no_ask_reason}))
        else:
            results.append(judge(p, criteria, ask, prompt))
    return results
