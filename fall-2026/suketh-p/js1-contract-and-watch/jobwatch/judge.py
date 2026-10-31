"""The Claude judge (CONTRACT.md 'Claude output contract'): a fixed prompt, one posting per
call, and a validator that rejects any reply outside the contract. A valid reply is still
a model judgment, not a verified fact."""

import json
from pathlib import Path

from jobwatch.errors import JudgeError
from jobwatch.normalize import plain_text

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
# The student switched future runs to v2 on 2026-10-31 (reports/PROMPT-EXPERIMENT.md).
# Runs 1 and 2 used judge_v1; each results.json records the prompt it used.
DEFAULT_PROMPT = "judge_v2"
KEYS = {"posting_id", "verdict", "justification", "resume_evidence", "posting_evidence"}
EVIDENCE_KEYS = {"field", "quote"}
VERDICTS = ("relevant", "not_relevant")
NOTE = ("Model judgment under a prompt contract. Not a verified fact about eligibility, "
        "qualifications, or hiring outcomes.")


def posting_input(posting):
    """The only posting fields Claude receives. Links and other metadata stay behind."""
    return {
        "id": posting.id,
        "title": posting.title,
        "location": {"name": posting.location_name},
        "content": plain_text(posting.content),
    }


def load_prompt(name=DEFAULT_PROMPT):
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def build_request(resume, posting, prompt=DEFAULT_PROMPT):
    """System text is the fixed prompt file; the user message is data only."""
    return load_prompt(prompt), json.dumps({"resume": resume, "posting": posting}, ensure_ascii=False, indent=2)


def judge_posting(resume, posting, send, prompt=DEFAULT_PROMPT):
    system, user = build_request(resume, posting, prompt)
    reply = send(system, user)
    try:
        data = validate_response(reply, resume, posting)
    except JudgeError as error:
        raise JudgeError(f"posting {posting['id']}: {error}", reply=reply) from None
    return {
        "kind": "model_judgment",
        "note": NOTE,
        "prompt": prompt,
        "verdict": data["verdict"],
        "justification": data["justification"],
        "resume_evidence": data["resume_evidence"],
        "posting_evidence": data["posting_evidence"],
        "call": getattr(reply, "meta", None),
        "raw_reply": str(reply),
    }


def _no_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        raise JudgeError("reply repeats a key")
    return dict(pairs)


def _resolve(field, side, inputs, where):
    parts = field.split(".")
    if parts[0] != side or len(parts) < 2:
        raise JudgeError(f'{where}.field "{field}" must be a path starting with "{side}."')
    value = inputs
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            raise JudgeError(f'{where}.field "{field}" is not a path in the supplied input')
        value = value[part]
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and value and all(isinstance(item, str) for item in value):
        return value
    raise JudgeError(f'{where}.field "{field}" is not a text field or a list of text')


def _check_evidence(items, name, side, inputs):
    if not isinstance(items, list) or not items:
        raise JudgeError(f"{name} must be a nonempty array")
    for i, item in enumerate(items):
        where = f"{name}[{i}]"
        if not isinstance(item, dict) or set(item) != EVIDENCE_KEYS:
            raise JudgeError(f"{where} must be an object with exactly field and quote")
        field, quote = item["field"], item["quote"]
        if not isinstance(field, str) or not isinstance(quote, str) or not quote.strip():
            raise JudgeError(f"{where} needs a string field and a nonempty string quote")
        sources = _resolve(field, side, inputs, where)
        wanted = " ".join(quote.split())
        if not any(wanted in " ".join(source.split()) for source in sources):
            raise JudgeError(f'{where}.quote "{quote}" does not appear in {field}')


def validate_response(text, resume, posting):
    """Return the parsed reply, or raise JudgeError. Nothing outside one JSON object is
    allowed; every citation must name a real path and quote text that is in it."""
    if not isinstance(text, str):
        raise JudgeError("reply is not text")
    try:
        data = json.loads(text, object_pairs_hook=_no_duplicate_keys)
    except ValueError as error:
        raise JudgeError(f"reply is not exactly one JSON object ({error})") from None
    if not isinstance(data, dict):
        raise JudgeError("reply must be a JSON object")
    if set(data) != KEYS:
        raise JudgeError(f"reply keys must be exactly {sorted(KEYS)}; got {sorted(data)}")
    if not isinstance(data["posting_id"], str) or data["posting_id"] != str(posting["id"]):
        raise JudgeError(f"posting_id must be the supplied id as a decimal string, \"{posting['id']}\"")
    if data["verdict"] not in VERDICTS:
        raise JudgeError(f"verdict must be one of {list(VERDICTS)}")
    if not isinstance(data["justification"], str) or not data["justification"].strip():
        raise JudgeError("justification must be a nonempty string")
    _check_evidence(data["resume_evidence"], "resume_evidence", "resume", {"resume": resume})
    _check_evidence(data["posting_evidence"], "posting_evidence", "posting", {"posting": posting})
    return data
