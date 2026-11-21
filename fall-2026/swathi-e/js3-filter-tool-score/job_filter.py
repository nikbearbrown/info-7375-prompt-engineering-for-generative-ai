"""The JS3 filter: FILTER.md version 1 and its 2026-11-17 revisions, applied literally.

evaluate(posting) takes {id, title, location, url, description_html} and returns
a record anyone can recompute: the verdict ("shortlisted", "not shortlisted",
"rejected", "I cannot tell"), the score (None when rejected or "I cannot tell"),
the points, R1-R7 results with exact quotes, and the evidence claims
(supported / contradicted / insufficient) with exact quotes. Every quote is a
contiguous piece of the title, the location, or descriptions.html_to_text() of
the description. Standard library only; no network, no model call.
"""
import re

import descriptions
import loop
import rule

VERSION = "v1.1"  # FILTER.md change log 2026-11-19
SOURCE = f"filter {VERSION} (record)"
JS3_URLS = {"greenhouse": loop.URLS["greenhouse"] + "?content=true", "ashby": loop.URLS["ashby"]}

# R1 role (title), R2 "Analyst", R3 seniority (title)
ROLE_TERMS = ("AI", "ML", "Machine Learning", "GenAI", "Data Engineer", "Data Engineering", "Data Scientist",
              "Data Science", "Analytics")
SWE_EARLY_TERMS = ("New Grad", "Early Career", "Entry", "University")
R2_WORDS = ("data", "analytics", "SQL", "machine learning", "AI")
SENIORITY_TERMS = ("Senior", "Sr", "Sr.", "Staff", "Principal", "Lead", "Leader", "Manager", "Director", "Head",
                   "Intern", "Internship")
# R5 experience; early-career words (D3)
EARLY_WORDS = ("new grad", "entry level", "early career", "university")
# R6 requirement wording (D5)
R6_PATTERNS = (r"must be (?:a )?U\.?S\.? citizens?", r"U\.?S\.? citizenship (?:is )?required",
               r"will not sponsor", r"unable to sponsor", r"without sponsorship",
               # change log 2026-11-19: citizenship required in the same sentence
               r"requires? U\.?S\.? citizenship",
               r"U\.?S\.? citizenship\b(?:(?!\.\s)[^\n]){0,120}?\b(?:is|are)\s+required")
# R6 clearance (change log 2026-11-19): a qualified clearance with requirement wording on the same line,
# unless that line calls it preferred, an advantage or a plus
_CLEARANCE = re.compile(r"(?:security|secret|top\s+secret|TS/SCI|government|active)\b[^.\n;]{0,40}?\bclearances?\b"
                        r"|\bclearances?\b[^.\n;]{0,30}?(?:TS/SCI|secret)", re.I)
_REQUIRED = re.compile(r"(?<!\w)(?:required|requires|require|must|mandatory)(?!\w)", re.I)
_CLEARANCE_OPTIONAL = re.compile(r"(?<!\w)(?:preferred|advantage|a plus)(?!\w)", re.I)
# R7 topic words and the score
TOPIC_WORDS = ("machine learning", "deep learning", "LLM", "NLP", "Python", "SQL", "Spark", "data pipeline",
               "statistics")
WEIGHTS = {"role": 3, "early": 2, "topic": 1}
TOPIC_MAX = 3
THRESHOLD = 5

CLAIMS = ("role match", "asks 0-1 years", "no sponsorship restriction", "in the US")
_QUOTE_RADIUS = 90


def _pattern(term):
    if term.lower() == "sr.":
        return re.compile(r"(?<!\w)Sr\.(?!\w)", re.I)
    if term.lower() == "sr":
        return re.compile(r"(?<!\w)Sr(?!\w)(?!\.)", re.I)
    body = r"[\s-]+".join(re.escape(w) for w in term.split())
    return re.compile(r"(?<!\w)" + body + r"(?!\w)", re.I)


_EARLY = {
    "new grad": re.compile(r"(?<!\w)new[\s-]+grad(?:uate)?s?(?!\w)", re.I),
    "entry level": re.compile(r"(?<!\w)entry[\s-]+level(?!\w)", re.I),
    "early career": re.compile(r"(?<!\w)early[\s-]+career(?!\w)", re.I),
    "university": re.compile(r"(?<!\w)university(?!\w)", re.I),
}
_NOT_FOR_NEW_GRADS = re.compile(r"not (?:for|open to|suitable for) new[\s-]+grad(?:uate)?s?", re.I)
_DASH = r"\s*(?:-|–|—|to)\s*"
# change log 2026-11-19: written-out numbers, optionally followed by the digit: "seven", "five (5)"
_WORD_NUMBERS = {w: i for i, w in enumerate(
    ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"), start=1)}
_NUM = r"(?:\d+|" + "|".join(_WORD_NUMBERS) + r")(?:\s*\(\d+\))?"
_Y = r"(?:years?|yrs?)(?!\w)"
_YEARS = (  # (pattern, kind); group 1 (and 2 for a range) is the number
    (re.compile(r"(?<![\d.])(\d+)" + _DASH + r"(\d+)\s*\+?\s*" + _Y, re.I), "range"),
    (re.compile(r"(?<![\d.])(\d+)\s*\+\s*" + _Y, re.I), "plus"),
    (re.compile(r"(?<![\d.\w])(" + _NUM + r")\s*" + _Y + r"\s*\+", re.I), "plus"),  # "5 years+"
    (re.compile(r"(?<![\d.\w])(" + _NUM + r")\s+or\s+more\s+" + _Y, re.I), "plus"),  # "7 or more years"
    (re.compile(r"(?<![\d.\w])(" + _NUM + r")\s*" + _Y + r"['’]?\s+or\s+more", re.I), "plus"),  # "7 years or more"
    (re.compile(r"(?:at least|minimum of|a minimum of|minimum|more than|over)\s+(" + _NUM + r")\s*\+?\s*" + _Y, re.I),
     "plus"),
    (re.compile(r"(?<![\d.\-–+\w])(" + _NUM + r")\s*" + _Y + r"['’]?\s+(?:of\s+)?(?:[\w'’-]+\s+){0,3}?experience",
                re.I), "single"),
)
# change log 2026-11-19: years of education are not work experience; optional statements do not reject
_EDUCATION = re.compile(r"\s*(?:of\s+)?(?:\S+\s+){0,2}?(?:degree|education|study|studies|coursework|schooling)(?!\w)",
                        re.I)
# addendum 2026-11-19: an optional word counts only in the statement's clause; "ideal"/"ideally" removed
_OPTIONAL = re.compile(r"(?<!\w)(?:preferred|a plus|nice to have|bonus|recommended)(?!\w)", re.I)
_OPTIONAL_HEADING = re.compile(r"(?<!\w)(?:preferred|nice to have|bonus)(?!\w)", re.I)


def _quote(text, start, end):
    """A contiguous slice of one line of text around [start, end)."""
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    line_end = len(text) if line_end == -1 else line_end
    return text[max(line_start, start - _QUOTE_RADIUS):min(line_end, end + _QUOTE_RADIUS)].strip()


def _find(terms, text):
    """[(term, quote)] for terms found as whole words in text, in list order."""
    found = []
    for term in terms:
        m = _pattern(term).search(text or "")
        if m:
            found.append((term, _quote(text, m.start(), m.end())))
    return found


def _rule(result, reason, quotes=()):
    return {"result": result, "reason": reason, "quotes": list(quotes)}


def _is_english(text):
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum(c.isascii() for c in letters) / len(letters) >= 0.5


def _number(token):
    """5 from "5", "five" or "five (5)"; the digit in parentheses wins."""
    digits = re.findall(r"\d+", token)
    return int(digits[-1]) if digits else _WORD_NUMBERS[token.strip().lower()]


def _line_at(text, pos):
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    return start, len(text) if end == -1 else end


def _clause_at(text, start, end):
    """The clause around [start, end): commas, semicolons, full stops and line ends are boundaries."""
    before = max(text.rfind(c, 0, start) for c in ",;.\n") + 1
    after = [i for i in (text.find(c, end) for c in ",;.\n") if i != -1]
    return text[before:min(after) if after else len(text)]


def _is_education(text, m):
    """True when one of the first words after "years" (before "experience" or the end of the clause) names
    education, as in "two years of university education"."""
    years = list(re.finditer(_Y, m.group(), re.I))[-1]
    after = text[m.start() + years.end():]
    clause = re.split(r"experience|[.;,\n]", after, maxsplit=1, flags=re.I)[0]
    return bool(_EDUCATION.match(clause))


def _experience_statements(text, optional_lines=frozenset()):
    """[(low, high, quote)] for mandatory work experience stated in years; high is None for open-ended.

    Change log 2026-11-19 and addendum: years of education and optional statements (an optional word in
    the statement's clause, or a line in optional_lines) are left out; on a line whose statements are
    alternatives joined by "or", the alternatives above 1 year are left out when another alternative fits
    0-1 years.
    """
    found, taken = [], []
    for pattern, kind in _YEARS:
        for m in pattern.finditer(text):
            if any(s < m.end() and m.start() < e for s, e in taken):
                continue
            taken.append((m.start(), m.end()))
            line = text[slice(*_line_at(text, m.start()))]
            if (_is_education(text, m) or _OPTIONAL.search(_clause_at(text, m.start(), m.end()))
                    or line.strip() in optional_lines):
                continue
            low = _number(m.group(1))
            high = _number(m.group(2)) if kind == "range" else (low if kind == "single" else None)
            found.append((m.start(), m.end(), low, high, _quote(text, m.start(), m.end())))
    found.sort()
    kept = []
    for i, (start, end, low, high, quote) in enumerate(found):
        same_line = [f for f in found if _line_at(text, f[0]) == _line_at(text, start)]
        alternatives = len(same_line) > 1 and all(
            re.search(r"(?<!\w)or(?!\w)", text[a[1]:b[0]]) for a, b in zip(same_line, same_line[1:]))
        fits = lambda f: f[3] is not None and f[3] <= 1
        if alternatives and not fits(found[i]) and any(fits(f) for f in same_line):
            continue
        kept.append((low, high, quote))
    return kept


def score_points(role, early, topics):
    return (WEIGHTS["role"] * bool(role) + WEIGHTS["early"] * bool(early)
            + WEIGHTS["topic"] * min(int(topics), TOPIC_MAX))


def is_shortlisted(points, role):
    return bool(role) and points >= THRESHOLD


def order_shortlist(entries):
    """Shortlisted entries only, by score (highest first), then board name, then posting id (as text)."""
    shortlisted = [e for e in entries if e.get("verdict") == "shortlisted"]
    return sorted(shortlisted, key=lambda e: (-e["score"], str(e["board"]), str(e["id"])))


def _cannot_tell(posting, reason):
    rules = {r: _rule("not applied", reason) for r in ("R1", "R2", "R3", "R4", "R5", "R6", "R7")}
    return {"id": posting.get("id"), "title": posting.get("title"), "location": posting.get("location"),
            "verdict": "I cannot tell", "score": None, "reason": reason,
            "points": {"role": 0, "early": 0, "topics": 0}, "rules": rules,
            "claims": [{"claim": c, "label": "insufficient", "quote": None, "section": None} for c in CLAIMS],
            "source": SOURCE}


def evaluate(posting):
    title = posting.get("title") or ""
    location = posting.get("location") or ""
    html = posting.get("description_html") or ""
    text = descriptions.html_to_text(html)
    if not text.strip():
        return _cannot_tell(posting, "the description is missing or empty, so the text rules cannot be applied")
    if not _is_english(text):
        return _cannot_tell(posting, "the description is not in English (D6)")

    sections = descriptions.split_sections(html)
    counts = [s for s in sections if s.kind == "counts"]
    counts_text = "\n".join(s.text for s in counts)
    rules, claims = {}, {}

    # R1 role (title)
    role_hits = _find(ROLE_TERMS, title)
    if not role_hits and _pattern("Software Engineer").search(title):
        early_title = _find(SWE_EARLY_TERMS, title)
        if early_title:
            role_hits = [("Software Engineer", title)] + early_title
    rules["R1"] = (_rule("pass", "title names " + ", ".join(t for t, _ in role_hits), [title])
                   if role_hits else _rule("fail", "title names no R1 role term"))

    # R2 "Analyst": Data/AI words in a "counts" section only
    if _pattern("Analyst").search(title):
        if not counts:
            rules["R2"] = _rule("cannot tell", "no recognized responsibilities or skills section")
        else:
            hits = _find(R2_WORDS, counts_text)
            rules["R2"] = (_rule("pass", "a counts section names " + ", ".join(t for t, _ in hits), [q for _, q in hits])
                           if hits else _rule("fail", "no counts section names data, analytics, SQL, machine learning or AI"))
    else:
        rules["R2"] = _rule("not applied", "the title has no 'Analyst'")
    role = rules["R1"]["result"] == "pass" or rules["R2"]["result"] == "pass"
    role_quote = (rules["R1"]["quotes"] or rules["R2"]["quotes"] or [None])[0] if role else None
    claims["role match"] = ("supported", role_quote, "title" if rules["R1"]["result"] == "pass" else "counts") \
        if role else ("insufficient", None, None)

    # R3 seniority (title)
    senior = _find(SENIORITY_TERMS, title)
    rules["R3"] = (_rule("fail", "title names " + ", ".join(t for t, _ in senior), [title]) if senior
                   else _rule("pass", "no seniority or internship term in the title"))

    # R4 location
    us = rule.find_terms(location, rule.US_TERMS + rule.US_STATES)
    remote = rule.find_terms(location, ("Remote",))
    foreign = rule.find_terms(location, rule.NON_US_COUNTRIES)
    if us:
        rules["R4"] = _rule("pass", "location names " + ", ".join(us), [location])
        claims["in the US"] = ("supported", location, "location")
    elif not location.strip():
        rules["R4"] = _rule("cannot tell", "no location given")
        claims["in the US"] = ("insufficient", None, None)
    elif remote and not foreign:
        rules["R4"] = _rule("cannot tell", "'Remote' with no country (D2)", [location])
        claims["in the US"] = ("insufficient", None, None)
    else:
        why = ("remote, limited to " + ", ".join(foreign)) if remote else (
            "location names " + ", ".join(foreign) if foreign else "location names neither the US, a US state, nor Remote")
        rules["R4"] = _rule("fail", why, [location])
        claims["in the US"] = ("contradicted" if foreign else "insufficient", location if foreign else None,
                               "location" if foreign else None)

    # R5 experience (whole description); early-career words only in the title or a counts section (D3);
    # "university" only in the title (change log 2026-11-19)
    not_for = _NOT_FOR_NEW_GRADS.search(text)
    optional_lines = frozenset(line.strip() for s in sections if _OPTIONAL_HEADING.search(s.heading)
                               for line in s.text.split("\n"))
    statements = _experience_statements(text, optional_lines)
    too_much = [(lo, hi, q) for lo, hi, q in statements if hi is None or hi > 1]
    fits = [(lo, hi, q) for lo, hi, q in statements if hi is not None and hi <= 1]
    early_hits = [(w, q) for w, pat in _EARLY.items()
                  for src in ((title,) if w == "university" else (title, counts_text)) for m in [pat.search(src)] if m
                  for q in [_quote(src, m.start(), m.end())]]
    if not_for:
        q = _quote(text, not_for.start(), not_for.end())
        rules["R5"] = _rule("fail", "says it is not for new graduates", [q])
        claims["asks 0-1 years"] = ("contradicted", q, "description")
    elif too_much:
        rules["R5"] = _rule("fail", "asks for more than 1 year", [q for _, _, q in too_much])
        claims["asks 0-1 years"] = ("contradicted", too_much[0][2], "description")
    elif fits or early_hits:
        quotes = [q for _, _, q in fits] + [q for _, q in early_hits]
        rules["R5"] = _rule("pass", "explicit early-career evidence", quotes)
        claims["asks 0-1 years"] = ("supported", fits[0][2], "description") if fits else ("insufficient", None, None)
    else:
        rules["R5"] = _rule("cannot tell", "no experience stated and no early-career words describing the job")
        claims["asks 0-1 years"] = ("insufficient", None, None)
    early = rules["R5"]["result"] == "pass"

    # R6 work authorization (whole description, requirement wording only)
    r6 = []
    for pat in R6_PATTERNS:
        m = re.search(pat, text, re.I)
        if m:
            r6.append(_quote(text, m.start(), m.end()))
    for line in text.split("\n"):
        m = _CLEARANCE.search(line)
        if m and _REQUIRED.search(line) and not _CLEARANCE_OPTIONAL.search(line):
            r6.append(_quote(line, m.start(), m.end()))
    rules["R6"] = (_rule("fail", "requires citizenship or clearance, or will not sponsor", r6) if r6
                   else _rule("pass", "no citizenship, clearance or sponsorship requirement wording"))
    claims["no sponsorship restriction"] = ("contradicted", r6[0], "description") if r6 else ("insufficient", None, None)

    # R7 topic words, counts sections only (D1)
    topics = _find(TOPIC_WORDS, counts_text)
    rules["R7"] = _rule("pass" if topics else "fail",
                        f"{len(topics)} distinct topic word(s) in counts sections: " + ", ".join(t for t, _ in topics),
                        [q for _, q in topics])

    points = {"role": WEIGHTS["role"] if role else 0, "early": WEIGHTS["early"] if early else 0,
              "topics": min(len(topics), TOPIC_MAX) * WEIGHTS["topic"]}
    if any(rules[r]["result"] == "fail" for r in ("R3", "R4", "R5", "R6")):
        verdict, score = "rejected", None
        reason = "fails " + ", ".join(r for r in ("R3", "R4", "R5", "R6") if rules[r]["result"] == "fail")
    elif any(rules[r]["result"] == "cannot tell" for r in ("R2", "R4", "R5")):
        verdict, score = "I cannot tell", None
        reason = "cannot tell: " + ", ".join(r for r in ("R2", "R4", "R5") if rules[r]["result"] == "cannot tell")
    else:
        score = score_points(role, early, len(topics))
        verdict = "shortlisted" if is_shortlisted(score, role) else "not shortlisted"
        reason = f"score {score}" + ("" if role else "; no role match (R1/R2 required)")
    return {"id": posting.get("id"), "title": title, "location": location, "verdict": verdict, "score": score,
            "reason": reason, "points": points, "rules": rules,
            "claims": [{"claim": c, "label": claims[c][0], "quote": claims[c][1], "section": claims[c][2]}
                       for c in CLAIMS],
            "source": SOURCE}
