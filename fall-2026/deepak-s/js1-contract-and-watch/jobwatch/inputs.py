"""Token and résumé checks: CONTRACT.md In, Refuses 2, Order steps 1-2.

Refusal messages name a field path, never the value found there.
"""
import json
import re
from pathlib import Path

import jsonschema

from jobwatch.errors import REFUSED, Stop
from jobwatch.paths import pointer
from jobwatch.textmatch import has_tokens

TOKEN = re.compile(r"[a-z0-9][a-z0-9_-]{0,62}")
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "resume.schema.json"
TARGET_LISTS = ("roles", "locations", "exclude_title_terms")

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")
_PHONE = re.compile(
    r"""
    (?<![\d+])
    (?:
        \+\d[\d\s().-]{6,}\d                                     # written with a leading +
      | (?:1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}  # with an area code
      | \d{3}[\s.-]\d{4}                                         # seven digits
    )
    (?!\d)
    """,
    re.VERBOSE,
)


def check_token(token):
    if not isinstance(token, str) or not TOKEN.fullmatch(token):
        raise Stop(REFUSED, "board token refused: it must match ^[a-z0-9][a-z0-9_-]{0,62}$")


def load_resume(path):
    """Return (résumé, raw bytes), or raise Stop(2)."""
    try:
        raw = Path(path).read_bytes()
    except OSError:
        raise Stop(REFUSED, f"résumé refused: cannot read {path}") from None
    try:
        data = json.loads(raw)
    except ValueError:
        raise Stop(REFUSED, "résumé refused: not valid JSON") from None
    _check_schema(data)
    _check_target_terms(data)
    found = privacy_findings(data)
    if found:
        raise Stop(REFUSED, "résumé refused: " + "; ".join(found))
    return data, raw


def _check_schema(data):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    error = jsonschema.exceptions.best_match(jsonschema.Draft202012Validator(schema).iter_errors(data))
    if error is None:
        return
    where = pointer(*error.absolute_path) or "/"
    if error.validator == "required" and isinstance(error.instance, dict):
        missing = [k for k in error.validator_value if k not in error.instance]
        raise Stop(REFUSED, f"résumé refused: {where} is missing {', '.join(missing)}")
    if list(error.absolute_path) == ["fictional"]:
        raise Stop(REFUSED, 'résumé refused: /fictional must be exactly true')
    raise Stop(REFUSED, f"résumé refused: {where} does not match the schema ({error.validator})")


def _check_target_terms(data):
    for name in TARGET_LISTS:
        for i, term in enumerate(data["targets"][name]):
            if not has_tokens(term):
                raise Stop(REFUSED, f"résumé refused: {pointer('targets', name, i)} has no word characters")


def _strings(node, path=()):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _strings(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, path + (i,))


def _phone_allowed(written):
    digits = re.sub(r"\D", "", written)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        exchange, line = digits[3:6], digits[6:]
    elif len(digits) == 7:
        exchange, line = digits[:3], digits[3:]
    else:
        return False
    return exchange == "555" and 100 <= int(line) <= 199


def privacy_findings(data):
    """Field paths holding a non-@example.com email or a phone outside 555-0100..0199."""
    found = []
    for path, text in _strings(data):
        where = pointer(*path) or "/"
        if any(m.group(1).lower() != "example.com" for m in _EMAIL.finditer(text)):
            found.append(f"{where} contains an email address outside @example.com")
        if any(not _phone_allowed(m.group(0)) for m in _PHONE.finditer(text)):
            found.append(f"{where} contains a phone number outside 555-0100 to 555-0199")
    return found
