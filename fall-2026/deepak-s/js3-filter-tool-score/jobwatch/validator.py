"""The validator: CONTRACT.md Out › Citations and Claude's output format.

It checks the rule's verdicts and Claude's alike. Each failure has one named reason.
"""
import json

from jobwatch.paths import Unresolved, resolve
from jobwatch.textmatch import whole_word_match

VERDICTS = ("relevant", "not_relevant")
OUTPUT_KEYS = {"posting_id", "verdict", "citations", "reason"}
CITATION_KEYS = {"source", "path", "value"}
REASON_LIMIT = 400


class Invalid(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def check_citations(citations, resume, posting_doc):
    if not isinstance(citations, list):
        raise Invalid("citations_not_list")
    sources = set()
    for c in citations:
        if not isinstance(c, dict) or set(c) != CITATION_KEYS:
            raise Invalid("citation_malformed")
        if c["source"] not in ("resume", "posting"):
            raise Invalid("citation_bad_source")
        if not isinstance(c["path"], str) or not isinstance(c["value"], str):
            raise Invalid("citation_malformed")
        try:
            found = resolve(resume if c["source"] == "resume" else posting_doc, c["path"])
        except Unresolved:
            raise Invalid("path_unresolved") from None
        if isinstance(found, bool) or not isinstance(found, (str, int, float)):
            raise Invalid("path_not_text")
        if c["value"] == "":
            raise Invalid("value_empty")
        if not whole_word_match(c["value"], found if isinstance(found, str) else str(found)):
            raise Invalid("value_not_found")
        sources.add(c["source"])
    if "resume" not in sources:
        raise Invalid("no_resume_citation")
    if "posting" not in sources:
        raise Invalid("no_posting_citation")


def check_verdict(verdict, resume, posting_doc):
    """A rule verdict {"verdict", "citations"}."""
    if verdict.get("verdict") not in VERDICTS:
        raise Invalid("bad_verdict")
    check_citations(verdict.get("citations"), resume, posting_doc)


class _DuplicateKey(ValueError):
    """A JSON object repeats a key."""


def _object_without_duplicates(pairs):
    keys = [k for k, _ in pairs]
    if len(set(keys)) != len(keys):
        raise _DuplicateKey()
    return dict(pairs)


def _reject_constant(name):
    raise ValueError(name)


def parse_output(text, posting_id, resume, posting_doc):
    """Claude's text must be exactly one JSON object in the contract's format; returns it."""
    try:
        obj = json.loads(text, object_pairs_hook=_object_without_duplicates, parse_constant=_reject_constant)
    except _DuplicateKey:
        raise Invalid("duplicate_key") from None
    except ValueError:
        raise Invalid("not_json") from None
    if not isinstance(obj, dict):
        raise Invalid("not_object")
    if set(obj) - OUTPUT_KEYS:
        raise Invalid("extra_keys")
    if OUTPUT_KEYS - set(obj):
        raise Invalid("missing_keys")
    if not isinstance(obj["posting_id"], str):
        raise Invalid("posting_id_not_string")
    if obj["posting_id"] != posting_id:
        raise Invalid("posting_id_mismatch")
    if not isinstance(obj["verdict"], str) or obj["verdict"] not in VERDICTS:
        raise Invalid("bad_verdict")
    if not isinstance(obj["reason"], str):
        raise Invalid("reason_not_string")
    if len(obj["reason"]) > REASON_LIMIT:
        raise Invalid("reason_too_long")
    check_citations(obj["citations"], resume, posting_doc)
    return obj
