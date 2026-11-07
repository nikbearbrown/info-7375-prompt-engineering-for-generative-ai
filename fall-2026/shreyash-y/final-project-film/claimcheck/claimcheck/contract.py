"""The answer contract: the only shape an answer may take before the checker sees it."""

import json
from dataclasses import dataclass

STATUSES = ("answered", "not_in_documents")
FIELDS = ("answer", "quote", "doc_id", "status")

# Same contract, as a JSON schema, for the Claude answerer's structured output.
SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "quote": {"type": "string"},
        "doc_id": {"type": "string"},
        "status": {"type": "string", "enum": list(STATUSES)},
    },
    "required": list(FIELDS),
    "additionalProperties": False,
}


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Answer:
    answer: str
    quote: str
    doc_id: str
    status: str


def parse(raw: str) -> Answer:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(f"not valid JSON ({exc.msg})") from None
    if not isinstance(data, dict):
        raise ContractError("not a JSON object")
    missing = [f for f in FIELDS if f not in data]
    if missing:
        raise ContractError(f"missing field(s): {', '.join(missing)}")
    extra = sorted(set(data) - set(FIELDS))
    if extra:
        raise ContractError(f"unexpected field(s): {', '.join(extra)}")
    if not all(isinstance(data[f], str) for f in FIELDS):
        raise ContractError("every field must be a string")
    if data["status"] not in STATUSES:
        raise ContractError(f"status must be one of {STATUSES}, got {data['status']!r}")
    return Answer(**{f: data[f] for f in FIELDS})
