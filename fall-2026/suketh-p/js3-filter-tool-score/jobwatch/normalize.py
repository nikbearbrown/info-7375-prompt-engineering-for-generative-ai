"""Text normalization, exactly as CONTRACT.md 'The relevance rule' defines it:
decode entities until nothing changes, remove markup with an HTML parser (adjacent
text blocks separated by spaces), lowercase, split on every character outside a-z0-9."""

import html
import re
from html.parser import HTMLParser

_SEPARATORS = re.compile(r"[^a-z0-9]+")


def decode_entities(text):
    while True:
        decoded = html.unescape(text)
        if decoded == text:
            return text
        text = decoded


class _TextBlocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []

    def handle_data(self, data):
        self.blocks.append(data)


def strip_markup(text):
    parser = _TextBlocks()
    parser.feed(text)
    parser.close()
    return " ".join(parser.blocks)


def tokens(text):
    lowered = strip_markup(decode_entities(text)).lower()
    return [token for token in _SEPARATORS.split(lowered) if token]


def contains_phrase(text_tokens, phrase):
    """True when the phrase's tokens appear consecutively; a single word must be a whole token."""
    wanted = tokens(phrase)
    if not wanted:
        return False
    width = len(wanted)
    return any(text_tokens[i:i + width] == wanted for i in range(len(text_tokens) - width + 1))


def find_phrase(text_tokens, phrase):
    """Index of the first consecutive match, or None."""
    wanted = tokens(phrase)
    width = len(wanted)
    for i in range(len(text_tokens) - width + 1):
        if wanted and text_tokens[i:i + width] == wanted:
            return i
    return None


def plain_text(text):
    """Posting content as Claude receives it: decoded, markup removed, whitespace
    collapsed, capitalization kept (so quotes can be checked against it)."""
    return " ".join(strip_markup(decode_entities(text)).split())
