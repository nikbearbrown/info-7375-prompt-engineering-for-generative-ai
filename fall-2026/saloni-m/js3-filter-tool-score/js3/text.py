"""Word splitting and phrase matching shared by the filter and the evidence checker.

The JS1 rule: lower-case, split on anything that is not a letter or digit, match whole word
sequences. "ml" matches "ML Engineer"; it never matches "HTML".
"""
import html
import re

_WORD = re.compile(r"[a-z0-9]+")
_SENTENCE = re.compile(r"(?<=[.!?;])\s+|\n+|\s+[•·▪]\s+")


def words(text):
    return _WORD.findall((text or "").lower())


def phrase_positions(text_words, phrase):
    target = words(phrase)
    n = len(target)
    if n == 0:
        return []
    return [i for i in range(len(text_words) - n + 1) if text_words[i:i + n] == target]


def has_phrase(text, phrase):
    return bool(phrase_positions(words(text), phrase))


def plain_text(content):
    """Greenhouse content is HTML that is itself HTML-escaped; undo both, drop tags."""
    text = html.unescape(html.unescape(content or ""))
    text = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<li[^>]*>", "\n• ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    return re.sub(r"\n\s*", "\n", text).strip()


def sentences(text):
    return [s.strip() for s in _SENTENCE.split(text or "") if s and s.strip()]


def norm(s):
    """Case- and whitespace-insensitive form used to check that a quote is really in the text."""
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()
