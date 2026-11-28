"""FILTER.md 'The evidence rules' as code: the quote check and the label.

The quote check is mechanical: a quote counts as found only if it appears in the saved
posting text word for word, with case kept and only whitespace normalized. It says nothing
about meaning. The label is a person's: FILTER.md says "I mark it supported after reading the
original passage in context". So final_label never turns a found quote into "supported";
a claim without the person's label stays "not reviewed"."""

from jobwatch.normalize import plain_text

LABELS = ("supported", "contradicted", "insufficient", "not reviewed")
CANNOT_TELL_SPONSORSHIP = "I cannot tell whether this role offers sponsorship."


def plain(html_text):
    """The saved posting as text: entities decoded, markup removed, whitespace collapsed, case kept."""
    return plain_text(html_text or "")


def _squash(text):
    return " ".join(text.split())


def quote_found(text, quote):
    if not quote or not quote.strip():
        return False
    return _squash(quote) in _squash(text)


def check_quote(text, quote):
    if quote is None or not str(quote).strip():
        return "no quote"
    return "quote found" if quote_found(text, quote) else "quote not found"


def final_label(human_label, quote_check):
    """The person's label, or "not reviewed". The quote check never decides the label."""
    if human_label is None:
        return "not reviewed"
    if human_label not in LABELS:
        raise ValueError(f"unknown label {human_label!r}; use one of {', '.join(LABELS)}")
    return human_label
