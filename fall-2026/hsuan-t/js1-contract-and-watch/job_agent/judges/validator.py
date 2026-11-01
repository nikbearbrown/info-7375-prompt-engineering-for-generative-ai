"""The CONTRACT validator: checks Claude's reply before it is saved; any failed row means the reply is rejected.

The model's text is the one input this program does not control, so nothing it says becomes a
verdict until it has passed every row of the CONTRACT "validator" table. Each row below is one
function step, in table order, and the error message names the row so a TA can match it.
What this cannot check: whether the quote really supports the result. That is judgment, left to
the sampling report and the hand labels (CONTRACT, right under the table).
"""

import json
import re

from .verdict import NOT_RELEVANT, RELEVANT
from .words import strip_html

KEYS = {"posting_id", "verdict", "justification"}
LINE_KEYS = {"posting_field", "compared_to", "result", "quote"}
POSTING_FIELDS = ("title", "location.name", "content")
_SPACES = re.compile(r"\s+")


class Rejected(Exception):
    """The reply broke a CONTRACT validator row; the message becomes the verdict's error_message."""


def squash(text: str) -> str:
    """CONTRACT row 8 comparison form: HTML removed, lowercase, any run of spaces counts as one."""
    return _SPACES.sub(" ", strip_html(text)).strip().lower()


def validate(text: str, posting_id: int, fields: dict[str, str]) -> tuple[str, list[dict]]:
    """Return (verdict, justification) if every row passes; raise Rejected on the first row that fails.

    fields maps "title" / "location.name" / "content" to what Claude was shown, so quotes are
    checked against the same text, not the raw HTML.
    """
    # Row 1: valid JSON and only JSON. strip() only forgives surrounding whitespace; a ```json
    # fence or a sentence before the JSON is "not only JSON" and is rejected.
    try:
        reply = json.loads(text.strip())
    except json.JSONDecodeError:
        raise Rejected("reply is not valid JSON (or has text around the JSON)") from None
    # Row 2: exactly the three keys.
    if not isinstance(reply, dict) or set(reply) != KEYS:
        got = sorted(reply) if isinstance(reply, dict) else type(reply).__name__
        raise Rejected(f"reply must have exactly the keys {sorted(KEYS)}, got {got}")
    # Row 3: same posting. bool is excluded because True == 1 in Python.
    pid = reply["posting_id"]
    if isinstance(pid, bool) or pid != posting_id or not isinstance(pid, int):
        raise Rejected(f"posting_id {pid!r} does not match the posting sent ({posting_id})")
    # Row 4: only the two verdict words.
    if reply["verdict"] not in (RELEVANT, NOT_RELEVANT):
        raise Rejected(f"verdict must be relevant or not_relevant, got {reply['verdict']!r}")
    # Row 5: at least one line, each exactly four keys.
    lines = reply["justification"]
    if not isinstance(lines, list) or not lines:
        raise Rejected("justification must be a non-empty list")
    for i, line in enumerate(lines):
        if not isinstance(line, dict) or set(line) != LINE_KEYS:
            raise Rejected(f"justification[{i}] must have exactly the keys {sorted(LINE_KEYS)}")
        if not all(isinstance(line[k], str) and line[k].strip() for k in LINE_KEYS):
            raise Rejected(f"justification[{i}] fields must be non-empty strings")
        # Row 6: a field Claude was actually shown.
        if line["posting_field"] not in POSTING_FIELDS:
            raise Rejected(f"justification[{i}].posting_field {line['posting_field']!r} is not one of {list(POSTING_FIELDS)}")
        # Row 7: compared against the job seeker's data, not "common sense".
        if not line["compared_to"].startswith(("resume.", "profile.")):
            raise Rejected(f"justification[{i}].compared_to {line['compared_to']!r} must start with resume. or profile.")
        # Row 8: the evidence exists. An empty quote would be "found" in any text, hence the
        # non-empty check above.
        if squash(line["quote"]) not in squash(fields[line["posting_field"]]):
            raise Rejected(f"justification[{i}].quote not found in posting.{line['posting_field']}")
    return reply["verdict"], lines
