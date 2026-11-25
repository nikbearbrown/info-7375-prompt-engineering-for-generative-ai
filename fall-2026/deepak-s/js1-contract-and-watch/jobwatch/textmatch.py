"""Whole-word matching, exactly as defined in CONTRACT.md The rule.

Lowercase with str.lower(); a token is a maximal run of characters that are str.isalnum() or one
of "+#"; a term matches when its token sequence appears contiguously in the text's tokens.
"""

_EXTRA = "+#"


def tokens(text):
    out, cur = [], []
    for ch in str(text).lower():
        if ch.isalnum() or ch in _EXTRA:
            cur.append(ch)
        elif cur:
            out.append("".join(cur))
            cur = []
    if cur:
        out.append("".join(cur))
    return out


def has_tokens(text):
    return bool(tokens(text))


def whole_word_match(term, text):
    t, x = tokens(term), tokens(text)
    if not t:
        return False
    n = len(t)
    return any(x[i : i + n] == t for i in range(len(x) - n + 1))


def first_match(terms, text):
    """Index of the lowest-index term that matches `text`, or None."""
    for i, term in enumerate(terms):
        if whole_word_match(term, text):
            return i
    return None
