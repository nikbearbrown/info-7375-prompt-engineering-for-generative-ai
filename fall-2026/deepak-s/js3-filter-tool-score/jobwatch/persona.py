"""Persona checks for the JS2 loop path, with no file I/O.

Copied from JS1 jobwatch/inputs.py at commit b91c877 (personal repo,
fall2026/deepak-kumaran-ts/js1-contract-and-watch/jobwatch/inputs.py):
    lines 17-32   TARGET_LISTS, _EMAIL, _PHONE              verbatim
    lines 39-55   load_resume                                as check_resume(raw, schema): the
                                                             file read (lines 41-44) is removed and
                                                             it returns the data, not (data, raw)
    lines 57-68   _check_schema                              takes the schema as an argument instead
                                                             of reading SCHEMA_PATH (line 58)
    lines 71-111  _check_target_terms, _strings,
                  _phone_allowed, privacy_findings           verbatim
The loop reads examples/persona_resume.json and schema/resume.schema.json through
jobwatch/tools.py read_file and passes the bytes and the parsed schema here, so the loop
path never imports jobwatch/inputs.py (GATE.md Amendments, A-1).
tests/js2/test_persona.py checks that this copy and JS1's inputs.load_resume agree.
"""
import json
import re

import jsonschema

from jobwatch.errors import REFUSED, Stop
from jobwatch.paths import pointer
from jobwatch.textmatch import has_tokens

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


def check_resume(raw, schema):
    """JS1 load_resume (inputs.py lines 39-55) on bytes already read; returns the résumé or raises Stop(2)."""
    try:
        data = json.loads(raw)
    except ValueError:
        raise Stop(REFUSED, "résumé refused: not valid JSON") from None
    _check_schema(data, schema)
    _check_target_terms(data)
    found = privacy_findings(data)
    if found:
        raise Stop(REFUSED, "résumé refused: " + "; ".join(found))
    return data


def _check_schema(data, schema):
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
