"""Text handling shared by the rule and the validator (CONTRACT.md, The rule, condition 3)."""
import html
import re

_TAG = re.compile(r"<[^>]+>")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def strip_html(content):
    # Greenhouse sends `content` as entity-escaped HTML ("&lt;p&gt;..."):
    # decode once to get real tags, drop the tags, then decode remaining entities.
    return html.unescape(_TAG.sub(" ", html.unescape(content)))


def normalize(text):
    """Lowercase, turn every non-alphanumeric run into one space, trim."""
    return " ".join(_NON_ALNUM.sub(" ", text.lower()).split())


def contains_sequence(normalized_text, normalized_phrase):
    """True if the phrase appears with a space or string boundary on each side."""
    if not normalized_phrase:
        return False
    return f" {normalized_phrase} " in f" {normalized_text} "


def find_original(text, phrase):
    """Return the span of `text` that normalizes to `phrase`, as it was written.

    Used only to quote evidence; the verdict itself is decided by contains_sequence.
    """
    tokens = normalize(phrase).split()
    if not tokens:
        return None
    pattern = r"(?<![A-Za-z0-9])" + r"[^A-Za-z0-9]+".join(map(re.escape, tokens)) + r"(?![A-Za-z0-9])"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(0) if match else None
