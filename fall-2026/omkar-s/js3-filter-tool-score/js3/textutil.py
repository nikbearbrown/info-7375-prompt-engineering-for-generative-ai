"""Text helpers for FILTER.md v1: whole-word matching, years statements (1c), requirement sections (2).

Everything here is deterministic and small enough to apply by hand to one posting.
"""
import html as _html
import re

from .js2.rule import clean_content  # JS1/JS2 cleaner, unchanged


def clean(raw):
    return clean_content(raw)


def ww(phrase):
    """Whole-word, case-insensitive: no letter or digit may touch either end (JS1 rule)."""
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(phrase) + r"(?![A-Za-z0-9])", re.I)


def has_any(text, phrases):
    """First phrase from `phrases` found whole-word in `text`, else None."""
    for ph in phrases:
        if ww(ph).search(text or ""):
            return ph
    return None


# --- 1c. years statements ---------------------------------------------------------------
_Y = r"(?:years?|yrs?)"
_N = r"(\d{1,2})"
YEARS_PATTERNS = [
    re.compile(r"(?:at least|a minimum of|minimum of)\s+" + _N + r"\s*\+?\s*" + _Y, re.I),
    re.compile(_N + r"\s*\+?\s*(?:-|–|—|to)\s*\d{1,2}\s*\+?\s*" + _Y, re.I),
    re.compile(_N + r"\s*\+\s*" + _Y, re.I),
    re.compile(_N + r"\s+or more\s+" + _Y, re.I),
]
_EXPERIENCE_WITHIN = 60


_PLUS_ALONE = re.compile(r"(?<![\d.])(\d{1,2})\s*\+\s*(?:years?|yrs?)(?![A-Za-z])", re.I)


def years_statements(text, plus_alone=False):
    """[(minimum_years, quote)] for every FILTER 1c statement followed within 60 chars by 'experience'.
    With plus_alone (v1.5) an explicit 'N+ years' counts even without the word 'experience'."""
    return [(n, q) for n, q, _ in _statements(text, plus_alone)]


_SUB = re.compile(r"(?<![A-Za-z])(?:with|including|of which|plus)\s+(?:at least\s+)?$", re.I)


def _statements(text, plus_alone=False):
    out, seen = [], set()
    text = text or ""
    for pat in YEARS_PATTERNS:
        for m in pat.finditer(text):
            if m.start() in seen:
                continue
            n = int(m.group(1))
            if not 0 <= n <= 20:
                continue
            tail = text[m.end():m.end() + _EXPERIENCE_WITHIN + len("experience")]
            if "experience" not in tail.lower():
                continue
            k = tail.lower().index("experience")
            if k > _EXPERIENCE_WITHIN:
                continue
            seen.add(m.start())
            s = max(0, m.start() - 60)
            out.append((n, ("…" if s else "") + text[s:m.end() + k + len("experience")].strip(), m.start()))
    if plus_alone:
        for m in _PLUS_ALONE.finditer(text):
            n = int(m.group(1))
            if 0 <= n <= 20 and not any(abs(m.start() - x) < 3 for x in seen):
                seen.add(m.start())
                s = max(0, m.start() - 60)
                out.append((n, ("…" if s else "") + text[s:m.end() + 50].strip() + "…", m.start()))
    return out


def min_years(text, plus_alone=False, ignore_sub=False):
    """Smallest stated minimum. With ignore_sub (v1.6) a statement right after 'with' / 'including' /
    'of which' / 'plus' ("5+ years of engineering, with 2+ years building ML") is a sub-requirement and does
    not set the minimum, unless every statement is one."""
    full = _statements(text, plus_alone)
    st = [(n, q) for n, q, _ in full]
    if not st:
        return None, st
    use = full
    if ignore_sub:
        t = text or ""
        main = [x for x in full if not _SUB.search(t[max(0, x[2] - 25):x[2]])]
        use = main or full
    return min(n for n, _, _ in use), st


# --- 2. requirement sections ------------------------------------------------------------
_HEAD_TAG = re.compile(r"<(h[1-4]|strong|b)\b[^>]*>(.*?)</\1\s*>", re.I | re.S)
_BLOCK = re.compile(r"<\s*/?\s*(p|li|br|div|ul|ol|h[1-6]|tr|section)\b[^>]*>", re.I)
_TAG = re.compile(r"<[^>]+>")
H0, H1 = "\x01", "\x02"


def lines_with_headings(raw):
    """[(is_heading, text)] from Greenhouse/Ashby HTML, Lever 'label: <ul>…' or plain text.

    A bold/heading tag counts as a heading only when it is the whole line, so an inline
    <strong>Python</strong> inside a sentence is not a heading. A plain line of <= 80 chars
    ending in ':' is a heading too (FILTER.md section 2)."""
    s = raw or ""
    if "&lt;" in s:
        s = _html.unescape(s)
    # h1-h4 always start a new line; <strong>/<b> only mark their text, so a bold run is a heading only
    # when it fills its whole line (block tags around it supply the line breaks)
    s = _HEAD_TAG.sub(lambda m: ("\n" if m.group(1).lower().startswith("h") else "") + H0 +
                      _TAG.sub(" ", m.group(2)) + H1 + ("\n" if m.group(1).lower().startswith("h") else ""), s)
    s = _BLOCK.sub("\n", s)
    s = _TAG.sub(" ", s)
    s = _html.unescape(s)
    out = []
    for line in s.split("\n"):
        t = re.sub(r"\s+", " ", line).strip()
        if not t:
            continue
        bare = t.replace(H0, "").replace(H1, "").strip()
        if not bare:
            continue
        is_head = (t.startswith(H0) and t.endswith(H1) and H0 not in t[1:]) or \
                  (len(bare) <= 80 and bare.endswith(":"))
        out.append((is_head, bare))
    return out


def heading_has(t, phrases, plural=False):
    """Like has_any, for headings. With plural=True a phrase also matches with a trailing 's'
    ("Nice to Haves"), FILTER.md v1.3."""
    if not plural:
        return has_any(t, phrases)
    for ph in phrases:
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(ph) + r"s?(?![A-Za-z0-9])", t or "", re.I):
            return ph
    return None


def segments(raw, req_headings, end_headings, plural_headings=False):
    """[(in_requirements, heading, line)] for every line. A heading line is included too, with the
    state that holds after it (so a sub-heading "Python" inside a requirements section counts)."""
    out, in_req, head = [], False, None
    for is_head, t in lines_with_headings(raw):
        if is_head:
            head = t
            if heading_has(t, end_headings, plural_headings):
                in_req = False
            elif heading_has(t, req_headings, plural_headings):
                in_req = True
            # a heading that is neither leaves the state unchanged (FILTER.md section 2)
        out.append((in_req, head, t))
    return out


def skill_context(segs, skill, negations):
    """Where `skill` appears: ('required'|'negated'|'outside'|'absent', quote, heading)."""
    pat = ww(skill)
    best = ("absent", "", None)
    neg = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(n) for n in negations) +
                     r")\s+(?:\w+\s+){0,2}$", re.I)
    for in_req, head, t in segs:
        m = pat.search(t)
        if not m:
            continue
        quote = t if len(t) <= 220 else ("…" + t[max(0, m.start() - 100):m.end() + 100] + "…")
        if neg.search(t[:m.start()]):
            if best[0] == "absent":
                best = ("negated", quote, head)
            continue
        if in_req:
            return ("required", quote, head)
        if best[0] in ("absent", "negated"):
            best = ("outside", quote, head)
    return best
