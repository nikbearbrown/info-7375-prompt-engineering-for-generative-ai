"""Claude judge (the `judgment` verdict): build the prompt, validate the reply strictly, retry once."""

import json
import os
from pathlib import Path

from agent.net import make_anthropic_http_client
from agent.rule import clean_content

DEFAULT_TEMPLATE = Path(__file__).parent.parent / "prompts" / "judge_v1.txt"
PERMITTED_RESUME_FIELDS = ("target_titles", "skills", "locations", "experience", "education")
CITABLE_POSTING_FIELDS = ("title", "content", "location.name")
VERDICTS = {"relevant", "not_relevant"}
REPLY_KEYS = {"verdict", "justification", "resume_fields", "posting_fields"}
MAX_ATTEMPTS = 2


def build_resume_payload(resume: dict) -> dict:
    # Never send name, email or phone: Claude may only see what it is allowed to cite.
    return {field: resume[field] for field in PERMITTED_RESUME_FIELDS if field in resume}


def build_posting_payload(posting: dict) -> dict:
    location = posting.get("location")
    return {
        "id": posting.get("id"),
        "title": posting.get("title"),
        "location": {"name": location.get("name") if isinstance(location, dict) else None},
        "content": clean_content(posting.get("content")),
    }


def _nonempty(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def build_prompt(posting: dict, resume: dict, prompt_template=None) -> str:
    template = Path(prompt_template or DEFAULT_TEMPLATE).read_text(encoding="utf-8")
    # str.replace, not str.format: the template may contain literal JSON braces.
    return template.replace("{resume}", json.dumps(build_resume_payload(resume), indent=2, ensure_ascii=False)).replace(
        "{posting}", json.dumps(build_posting_payload(posting), indent=2, ensure_ascii=False)
    )


def _reject_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate keys in JSON object")
    return dict(pairs)


def validate_reply(reply, resume_payload: dict, posting_payload: dict) -> dict:
    """Return the parsed reply or raise ValueError describing the first problem found."""
    if not isinstance(reply, str):
        raise ValueError("reply is not a string")
    try:
        data = json.loads(reply, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as e:
        raise ValueError(f"reply is not valid JSON only: {e.msg}") from None
    if not isinstance(data, dict):
        raise ValueError("reply is not a JSON object")

    keys = set(data)
    if keys != REPLY_KEYS:
        missing, extra = sorted(REPLY_KEYS - keys), sorted(keys - REPLY_KEYS)
        raise ValueError(f"wrong keys (missing {missing}, extra {extra})")

    if data["verdict"] not in VERDICTS:
        raise ValueError(f"verdict must be relevant or not_relevant, got {data['verdict']!r}")
    if not isinstance(data["justification"], str) or not data["justification"].strip():
        raise ValueError("justification must be a nonempty string")

    posting_values = {
        "title": posting_payload.get("title"),
        "content": posting_payload.get("content"),
        "location.name": posting_payload["location"]["name"],
    }
    for key, permitted, values in (
        ("resume_fields", PERMITTED_RESUME_FIELDS, resume_payload),
        ("posting_fields", CITABLE_POSTING_FIELDS, posting_values),
    ):
        cited = data[key]
        if not isinstance(cited, list) or not cited:
            raise ValueError(f"{key} must be a nonempty array")
        for field in cited:
            if not isinstance(field, str):
                raise ValueError(f"{key} must contain only strings")
            if field not in permitted:
                raise ValueError(f"{key} cites field {field!r} that is not permitted")
            if not _nonempty(values.get(field)):
                raise ValueError(f"{key} cites field {field!r} that is missing or empty in the input")
    return data


def judge_claude(posting: dict, resume: dict, call_model, prompt_template=None) -> dict:
    prompt = build_prompt(posting, resume, prompt_template)
    resume_payload = build_resume_payload(resume)
    posting_payload = build_posting_payload(posting)

    errors = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            reply = call_model(prompt)
        except Exception as e:  # an API failure counts as a failed attempt
            errors.append(f"attempt {attempt}: request failed: {type(e).__name__}: {e}")
            continue
        try:
            data = validate_reply(reply, resume_payload, posting_payload)
        except ValueError as e:
            errors.append(f"attempt {attempt}: {e}")
            continue
        return {
            "posting_id": posting.get("id"),
            "source": "judgment",
            "verdict": data["verdict"],
            "justification": data["justification"],
            "resume_fields": data["resume_fields"],
            "posting_fields": data["posting_fields"],
            "attempts": attempt,
            "error": None,
        }

    # Never fabricate a verdict or evidence after two failures.
    return {
        "posting_id": posting.get("id"),
        "source": "judgment",
        "verdict": "invalid",
        "justification": None,
        "resume_fields": [],
        "posting_fields": [],
        "attempts": MAX_ATTEMPTS,
        "error": "; ".join(errors),
    }


def make_call_model(model="claude-sonnet-5-5"):
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    # The SDK only accepts httpx2 clients; this one host-checks every request and redirect hop.
    # SDK-level retries are off so judge_claude's single retry is the only one.
    client = anthropic.Anthropic(
        api_key=api_key,
        base_url="https://api.anthropic.com",
        http_client=make_anthropic_http_client(),
        max_retries=0,
    )

    def call_model(prompt: str) -> str:
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if getattr(block, "type", None) == "text")

    return call_model
