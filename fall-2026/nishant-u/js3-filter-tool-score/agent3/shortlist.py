"""FILTER.md v1 evidence rules C1-C4, labeled against the posting's own text only.

Each label is supported, contradicted or insufficient, and quotes the exact text it rests
on (a substring of the field it read) or says "no text found".

Interpretations of FILTER.md v1 fixed here so they are visible:
- C2 has no contradiction rule in FILTER.md, so it is supported or insufficient only.
- C3 contradiction patterns are checked before support patterns, so "we do not sponsor
  visas" is never read as support.
- C4 reads the location first, then the text; within each, a contradiction (onsite,
  in-office, hybrid) is checked before "remote".
- Ranking (FILTER.md wrong version 3 says what it must not be): most supported claims
  first, then fewest contradicted, then posting id.
"""
import re

from agent3 import filter as flt

NO_TEXT = "no text found"

C3_CONTRADICT = [re.compile(p, re.IGNORECASE) for p in (
    r"\b(cannot|can ?not|can't|unable to|not able to|will not|won't|do not|does not|don't|doesn't)"
    r"\s+(offer\s+|provide\s+|currently\s+)?(visa\s+|employment\s+)?sponsor(ship|s)?\b",
    r"\bwithout\s+(the\s+need\s+for\s+)?(any\s+)?(current\s+or\s+future\s+|future\s+)?"
    r"(visa\s+|employer\s+|employment\s+)?sponsorship\b",
    r"\bno\s+(visa\s+)?sponsorship\b",
    r"\bnot\s+eligible\s+for\s+(visa\s+)?sponsorship\b",
    r"\b(requires?|required|must\s+be|must\s+have|must\s+hold)\b[^.]{0,40}?\b(u\.?s\.?|united\s+states)\s+citizen(ship|s)?\b",
    r"\b(u\.?s\.?|united\s+states)\s+citizenship\s+(is\s+)?required\b",
    r"\b(security|secret|top\s+secret|ts/sci)\s+clearance\b",
)]
C3_SUPPORT = [re.compile(p, re.IGNORECASE) for p in (
    r"\b(will|can|do|does|we|is\s+able\s+to|are\s+able\s+to)\s+(sponsor|support)\b[^.]{0,40}?\b(visas?|h-?1b|sponsorship)\b",
    r"\b(visa|h-?1b)\s+sponsorship\s+(is\s+)?(available|offered|provided)\b",
    r"\bsponsors?\s+(visas?|h-?1b)\b",
    r"\bsupports?\s+(visas?|h-?1b)\b",
)]
C4_CONTRADICT = re.compile(r"(?<!\w)(on[- ]?site|in[- ]office|hybrid)(?!\w)", re.IGNORECASE)
C4_REMOTE = re.compile(r"(?<!\w)remote(?!\w)", re.IGNORECASE)
# FILTER.md v2 change 8: "hybrid" contradicts only in a sentence that also says office, day(s) or schedule.
C4_SCHEDULE = re.compile(r"(?<!\w)(office|offices|day|days|schedule)(?!\w)", re.IGNORECASE)


def sentence_around(text, start, end):
    """The sentence holding text[start:end], exactly as it appears; at most ~300 characters."""
    left = max(text.rfind(". ", 0, start), text.rfind("! ", 0, start), text.rfind("? ", 0, start))
    left = 0 if left < 0 else left + 2
    right = len(text)
    for mark in (".", "!", "?"):
        i = text.find(mark, end)
        if i != -1:
            right = min(right, i + 1)
    left = max(left, start - 150)
    right = min(right, end + 150)
    return text[left:right].strip()


def _label(claim, text, label, field, quote):
    return {"claim": claim, "text": text, "label": label, "field": field, "quote": quote}


def label_c1(posting, version=1):
    field, location = posting["location_field"], posting["location"]
    if location is None:
        return _label("C1", "US-based", "insufficient", field, NO_TEXT)
    part = flt.us_part(location, version)
    if part:
        return _label("C1", "US-based", "supported", field, part)
    return _label("C1", "US-based", "contradicted", field, location)


def label_c2(posting, skill):
    field, text = posting["text_field"], posting["text"] or ""
    hit = flt.find_term(text, skill)
    if not hit:
        return _label("C2", f"Uses {skill}", "insufficient", field, NO_TEXT)
    # Quote the sentence around the whole-word match, not the first substring ("SQL" inside "MySQL").
    span = flt.find_span(text, skill)
    i, j = span if span else (text.find(hit), text.find(hit) + len(hit))
    return _label("C2", f"Uses {skill}", "supported", field, sentence_around(text, i, j))


def label_c3(posting):
    field, text = posting["text_field"], posting["text"] or ""
    for label, patterns in (("contradicted", C3_CONTRADICT), ("supported", C3_SUPPORT)):
        for pattern in patterns:
            m = pattern.search(text)
            if m:
                return _label("C3", "Sponsors visas", label, field, sentence_around(text, m.start(), m.end()))
    return _label("C3", "Sponsors visas", "insufficient", field, NO_TEXT)


def _c4_contradiction(value, is_location, version):
    """The first onsite/in-office/hybrid match that counts under this version, or None."""
    for m in C4_CONTRADICT.finditer(value):
        if version >= 2 and m.group(1).lower() == "hybrid":
            sentence = value if is_location else sentence_around(value, m.start(), m.end())
            if not C4_SCHEDULE.search(sentence):
                continue
        return m
    return None


def label_c4(posting, version=1):
    flt.rules(version)
    sources = [(posting["location_field"], posting["location"] or "", True),
               (posting["text_field"], posting["text"] or "", False)]
    for field, value, is_location in sources:
        for label, find in (("contradicted", lambda v: _c4_contradiction(v, is_location, version)),
                            ("supported", C4_REMOTE.search)):
            m = find(value)
            if m:
                quote = value if is_location else sentence_around(value, m.start(), m.end())
                return _label("C4", "Remote", label, field, quote)
    return _label("C4", "Remote", "insufficient", posting["text_field"], NO_TEXT)


def label_claims(posting, skills, version=1):
    claims = [label_c1(posting, version)]
    claims += [label_c2(posting, s) for s in flt.skills_in(posting["text"] or "", skills)]
    claims += [label_c3(posting), label_c4(posting, version)]
    return claims


def rank_key(entry):
    labels = [c["label"] for c in entry["claims"]]
    return (-labels.count("supported"), labels.count("contradicted"), entry["posting_id"])


def build_shortlist(postings, skills, version=1):
    entries = []
    for posting in postings:
        verdict = flt.evaluate(posting, skills, version=version)
        if verdict["verdict"] != "accept":
            continue
        entries.append({"posting_id": posting["posting_id"], "posting": posting,
                        "verdict": verdict, "claims": label_claims(posting, skills, version)})
    return sorted(entries, key=rank_key)
