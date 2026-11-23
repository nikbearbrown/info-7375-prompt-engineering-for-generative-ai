"""Resolving the field paths that justifications are required to name.

CONTRACT.md O2 says a justification must name a resume field and a posting
field that actually resolve in the documents that were loaded, and must quote
evidence that really occurs in the posting field it names. That is only
checkable if "naming a field" has one definition, so it lives here and both
the rule judge uses it. (In JS1 the model-output validator used it too;
there is no model in this package — see GATE.md §5.4 and §8 A3.)
"""

from __future__ import annotations

import json
import re

_STEP = re.compile(r"([^.\[\]]+)|\[(\d+)\]")

_MISSING = object()


def resolve(doc, path: str):
    """Resolve a dotted/indexed path such as ``metadata[4].value``.

    Returns ``_MISSING`` (exposed as :data:`MISSING`) when the path does not
    resolve, rather than raising, so callers can report "cites a field that is
    not there" as a contract violation instead of an exception.
    """
    cur = doc
    for name, index in _STEP.findall(path):
        if name:
            if not isinstance(cur, dict) or name not in cur:
                return _MISSING
            cur = cur[name]
        else:
            i = int(index)
            if not isinstance(cur, list) or i >= len(cur):
                return _MISSING
            cur = cur[i]
    return cur


MISSING = _MISSING


def field_text(value) -> str:
    """The case-folded text that evidence quoted from a field must occur in.

    Strings are compared as themselves; anything else is compared against its
    canonical JSON form, so that citing an empty ``departments`` array with
    evidence ``"[]"`` is checkable by the same rule as citing a title.
    """
    if isinstance(value, str):
        return value.casefold()
    return json.dumps(value, sort_keys=True, ensure_ascii=False).casefold()


def whole_word(token: str, text: str) -> bool:
    """True when ``token`` occurs in ``text`` bounded by non-letters.

    Both arguments are expected case-folded. "Bounded by a non-letter" is the
    definition in CONTRACT.md §4, and it is what keeps ``sr`` out of ``sre``
    and ``lead`` out of ``leadership``.
    """
    pattern = r"(?<![a-z])" + re.escape(token) + r"(?![a-z])"
    return re.search(pattern, text) is not None
