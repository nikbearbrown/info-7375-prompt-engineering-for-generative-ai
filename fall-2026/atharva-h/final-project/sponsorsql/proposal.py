"""Parses a model reply into a checked proposal. Model text is data, never code."""

import json
import re
from dataclasses import dataclass, field
from typing import List

ANSWER_TYPES = ("count", "ranking", "table")


class ProposalError(Exception):
    """The reply could not be used."""


@dataclass
class Proposal:
    interpretation: str
    sql: str
    rows_sql: str
    answer_type: str
    limits: List[str] = field(default_factory=list)
    needs_clarification: bool = False


def _json_object(text):
    text = (text or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    elif not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ProposalError("no JSON object in the reply")
        text = text[start:end + 1]
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProposalError(f"reply is not valid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ProposalError("reply JSON is not an object")
    return value


def parse(text) -> Proposal:
    data = _json_object(text)
    clarify = data.get("needs_clarification", False)
    if not isinstance(clarify, bool):
        raise ProposalError("needs_clarification must be true or false")
    interpretation = data.get("interpretation", "")
    if not isinstance(interpretation, str) or not interpretation.strip():
        raise ProposalError("interpretation is missing")
    limits = data.get("limits", [])
    if isinstance(limits, str):
        limits = [limits] if limits.strip() else []
    if not isinstance(limits, list) or not all(isinstance(x, str) for x in limits):
        raise ProposalError("limits must be a string or a list of strings")
    if clarify:
        return Proposal(interpretation.strip(), "", "", "", limits, True)
    sql, rows_sql = data.get("sql", ""), data.get("rows_sql", "")
    if not isinstance(sql, str) or not sql.strip():
        raise ProposalError("sql is missing")
    if not isinstance(rows_sql, str) or not rows_sql.strip():
        raise ProposalError("rows_sql is missing")
    answer_type = data.get("answer_type", "")
    if answer_type not in ANSWER_TYPES:
        raise ProposalError(f"answer_type must be one of {', '.join(ANSWER_TYPES)}")
    return Proposal(interpretation.strip(), sql.strip(), rows_sql.strip(), answer_type, limits, False)
