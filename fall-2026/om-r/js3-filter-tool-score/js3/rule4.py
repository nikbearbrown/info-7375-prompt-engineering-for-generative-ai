"""Candidate rule 4 - experience / seniority / eligibility (filter
v1.1.0-candidate). Designed on the DEV split only (EXPERIMENT.md section 4,
logs/14_rule4_dev_evidence.txt). NOT part of FILTER.md v1.0.0.

FIRES (rejects) if ANY of:
  a. an explicit experience minimum of >= MIN_YEARS years in content:
     "N+ years", "N-M years" / "N to M years" (lower bound N), "at least N
     years", "minimum (of) N years", "N or more years". N is digits or a
     spelled-out number. Any qualifying mention counts, including one
     alternative path among several (e.g. "BS with 4-8 years").
  b. a seniority word in the TITLE, whole-word: Staff, Principal, Director,
     Manager, Head of.
  c. a people-management phrase in content: "managing managers", "lead a
     team of N", "manage/managing (a/the) <up to 2 words> team(s)", "own(s)
     the P&L", "P&L ownership/responsibility", "people management/manager",
     "direct reports".

FLAGS ONLY (never rejects; EXPERIMENT.md section 3, decision B):
  graduation-date requirements (a sentence with "graduat*" and a year 20xx)
  and security-clearance requirements. resume.json has no graduation date
  or clearance field, so a mechanical rule cannot know if they are met.

Matching runs on js3.filter.field_text (same normalization as rules 1-3);
every quote returned is an exact substring of that text.
"""
import re

from js3.filter import field_text, phrase_pattern

MIN_YEARS = 3
SENIORITY_TITLE_WORDS = ["Staff", "Principal", "Director", "Manager", "Head of"]

_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen".split())}
_NUM = r"(\d{1,2}|" + "|".join(_WORDS) + r")"
_YEARS = r"\s*years?\b"
_YEAR_PATTERNS = [
    re.compile(r"(?<![\w.])" + _NUM + r"\s*\+" + _YEARS, re.I),
    re.compile(r"(?<![\w.])" + _NUM + r"\s*(?:-|–|—|to)\s*" + _NUM + _YEARS, re.I),
    re.compile(r"\b(?:at\s+least\s+|(?:a\s+)?minimum\s+(?:of\s+)?)" + _NUM + _YEARS, re.I),
    re.compile(r"(?<![\w.])" + _NUM + r"\s+or\s+more" + _YEARS, re.I),
]
_SENIORITY_RE = {w: phrase_pattern(w) for w in SENIORITY_TITLE_WORDS}
_MGMT_PATTERNS = [
    re.compile(r"\bmanaging\s+managers\b", re.I),
    re.compile(r"\blead(?:ing)?\s+a\s+team\s+of\s+" + _NUM + r"\b", re.I),
    re.compile(r"\bmanag(?:e|es|ing)\s+(?:a\s+|the\s+)?(?:[\w&/-]+\s+){0,2}teams?\b", re.I),
    re.compile(r"\bown(?:s|ing)?\s+(?:the\s+)?P&L\b", re.I),
    re.compile(r"\bP&L\s+(?:ownership|responsibility)\b", re.I),
    re.compile(r"\bpeople\s+manag(?:er|ers|ement)\b", re.I),
    re.compile(r"\bdirect\s+reports\b", re.I),
]
_GRAD_RE = re.compile(r"\bgraduat\w*\b[^.]*?\b20\d{2}\b|\b20\d{2}\b[^.]*?\bgraduat\w*\b|\bclass\s+of\s+20\d{2}\b", re.I)
_CLEAR_RE = re.compile(r"\b(?:security\s+clearance|obtain\s+(?:a\s+)?clearance|clearance\s+required|"
                       r"(?:secret|TS/SCI|SC|DV)\s+clearance)\b", re.I)


def _n(tok):
    return int(tok) if tok.isdigit() else _WORDS[tok.lower()]


def _sentence(text, start, end):
    """The sentence around [start, end) - an exact substring of text."""
    s = text.rfind(". ", 0, start)
    s = 0 if s < 0 else s + 2
    e = text.find(". ", end)
    e = len(text) if e < 0 else e + 1
    return text[s:e].strip()


def check(posting):
    title, content = field_text(posting, "title"), field_text(posting, "content")
    out = {"fires": False, "reasons": [], "year_minimums": [], "seniority_title_word": None,
           "management_phrase": None, "eligibility_flags": []}

    seen = set()
    for rx in _YEAR_PATTERNS:
        for m in rx.finditer(content):
            if m.span() in seen:
                continue
            seen.add(m.span())
            n = _n(m.group(1))
            if n >= MIN_YEARS:
                out["year_minimums"].append({"n": n, "quote": m.group(0)})
    if out["year_minimums"]:
        y = out["year_minimums"][0]
        out["reasons"].append(f"rule 4: explicit experience minimum {y['quote']!r} (>= {MIN_YEARS} years)")

    for w, rx in _SENIORITY_RE.items():
        if rx.search(title):
            out["seniority_title_word"] = w
            out["reasons"].append(f"rule 4: seniority word {w!r} in title")
            break

    for rx in _MGMT_PATTERNS:
        m = rx.search(content)
        if m:
            out["management_phrase"] = m.group(0)
            out["reasons"].append(f"rule 4: people-management phrase {m.group(0)!r}")
            break

    for kind, rx in (("graduation", _GRAD_RE), ("clearance", _CLEAR_RE)):
        quotes = []
        for m in rx.finditer(content):
            q = _sentence(content, *m.span())
            if q not in quotes:
                quotes.append(q)
        out["eligibility_flags"] += [{"kind": kind, "quote": q} for q in quotes]

    out["fires"] = bool(out["reasons"])
    return out
