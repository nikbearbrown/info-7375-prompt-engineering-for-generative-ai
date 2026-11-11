"""HTML cleanup for matching (CONTRACT §5, §6.2).

Greenhouse's ``content`` is HTML escaped into text (``&lt;p&gt;Java&lt;/p&gt;``). The
cleaned string is an in-memory representation only; evidence always cites the raw
field (``$.content``), never the cleaned text.
"""

from __future__ import annotations

import html
import re
from typing import Final

_TAG: Final = re.compile(r"<!--.*?-->|</?[A-Za-z][^<>]*>", re.DOTALL)
"""An HTML comment or a tag-shaped ``<name ...>`` / ``</name>``.

Only tag-shaped text is removed, so a literal comparison such as ``1 < 2`` survives.
"""

_WHITESPACE: Final = re.compile(r"\s+")
"""Any run of Unicode whitespace, including the no-break space U+00A0."""


def clean_html(text: str) -> str:
    """Cleans entity-escaped HTML into plain text, in the CONTRACT §5 order.

    1. Decode HTML entities (``&lt;p&gt;`` becomes ``<p>``).
    2. Replace every tag with a single space, so ``<li>Java</li><li>Python</li>``
       does not merge into ``JavaPython``.
    3. Decode entities that remain (``&amp;amp;`` → ``&amp;`` in step 1 → ``&``).
    4. Collapse whitespace runs (no-break spaces included) to one space and trim.

    Punctuation is never removed, so ``C#`` and ``Node.js`` stay intact (§6.2).

    Args:
        text: The raw field value.

    Returns:
        The cleaned text.
    """
    decoded = html.unescape(text)
    stripped = _TAG.sub(" ", decoded)
    return _WHITESPACE.sub(" ", html.unescape(stripped)).strip()
