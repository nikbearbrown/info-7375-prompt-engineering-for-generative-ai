"""FILTER.md section 1: sentences, normalization, tokens and the joined posting text.

    split_sentences(html_text) -> [str]        after the first html.unescape, before tags are stripped
    normalize_field(raw) -> [str]               the field's normalized sentences, empty ones dropped
    join_fields(fields) -> (text, sentences)    the posting text and one record per sentence
    normalize_single(raw) -> str | None         title or location: one field, sentences joined with a space

Order (FILTER.md section 1): first html.unescape; then split into sentences; then, within each
sentence, strip tags, html.unescape again and collapse whitespace. A sentence ends at ., ! or ?
when followed by whitespace or the end of the text, or at the end of an HTML block element
(p, li, h1 to h6, div, br). Within a field, sentences are joined with a single space; fields are
joined in section 5 order with a single newline, and every field boundary ends a sentence.
There is no 6000-character truncation.

Two consequences the text states only implicitly, written down here: a sentence that is empty
after normalization is dropped (joining it would leave a double space, which whitespace
collapsing forbids), and so is a field with no sentences (it would leave an empty line).
Tokens are the JS1 tokens (jobwatch/textmatch.py).
"""
import html
import re

from jobwatch.textmatch import tokens

_TAG = re.compile(r"<[^>]*>")
# End of a sentence: ., ! or ? followed by whitespace or the end of the text; or the end of a
# block element: a closing p, li, h1-h6 or div tag, or a br tag (any form).
_BOUNDARY = re.compile(r"[.!?](?=\s|$)|</(?:p|li|h[1-6]|div)\s*>|<br\s*/?\s*>", re.IGNORECASE)


def split_sentences(text):
    """Split `text` (already through the first html.unescape) at sentence ends. Raw pieces."""
    pieces, start = [], 0
    for m in _BOUNDARY.finditer(text):
        pieces.append(text[start:m.end()])
        start = m.end()
    pieces.append(text[start:])
    return pieces


def normalize_sentence(piece):
    """Within one sentence: strip tags, html.unescape again, collapse whitespace."""
    return " ".join(html.unescape(_TAG.sub(" ", piece)).split())


def normalize_field(raw):
    """A raw field value -> its normalized, non-empty sentences in order."""
    if not isinstance(raw, str):
        return []
    out = []
    for piece in split_sentences(html.unescape(raw)):
        s = normalize_sentence(piece)
        if s:
            out.append(s)
    return out


def normalize_single(raw):
    """Title or location: normalized as one field; None when missing (not a string)."""
    if not isinstance(raw, str):
        return None
    return " ".join(normalize_field(raw))


def join_fields(fields):
    """`fields`: ((name, raw), ...) in section 5 order.

    Returns (text, sentences, spans): `text` is the joined posting text; `sentences` is a list of
    {"field", "start", "end", "text"} with character offsets into `text`; `spans` lists each
    field's {"field", "start", "end"}."""
    parts, sentences, spans, pos = [], [], [], 0
    for name, raw in fields:
        sents = normalize_field(raw)
        if not sents:
            continue
        if parts:
            parts.append("\n")
            pos += 1
        field_start = pos
        for i, s in enumerate(sents):
            if i:
                parts.append(" ")
                pos += 1
            sentences.append({"field": name, "start": pos, "end": pos + len(s), "text": s})
            parts.append(s)
            pos += len(s)
        spans.append({"field": name, "start": field_start, "end": pos})
    text = "".join(parts)
    return text, sentences, spans


def has_tokens(text):
    return bool(tokens(text or ""))
