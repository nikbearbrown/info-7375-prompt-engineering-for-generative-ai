"""Rule judge ("record"). CONTRACT.md Final, The rule: checks 1-7, every check runs, no early exit.

Choices the contract leaves open are listed in IMPLEMENTATION_CHOICES.md.
"""

import html
import re

COMPANY = "Databricks"  # D6-C§13

# Check 1, role phrases (D1§2), compared after title normalization (D6-B§8).
ROLE_PHRASES = [
    "ai engineer",
    "ml engineer",
    "machine learning engineer",
    "junior ai engineer",
    "software engineer machine learning",
    "data engineer",
    "junior data engineer",
    "associate data engineer",
]
TITLE_SEPARATORS = re.compile(r"[,\-–—()/]")

# Check 2, seniority (D0§3, D6-C§9): complete words only; "Head of" in any department.
SENIORITY_RE = re.compile(r"\b(senior|sr|lead|staff|principal|manager|director)\b|\bhead of\b", re.I)

# Check 3, skills (D2§1, D6-B§1, D6-A§2, D3§2, D7§b).
EXCLUDED_SKILL_SECTIONS = {"familiar_with_not_shipped", "agent_note"}
TOOLS_FROM_EXPERIENCE = ["Databricks Genie API", "MLflow"]
ALIASES = {"AWS": ["Amazon Web Services"]}
MIN_SKILLS = 2

# "Databricks" counts only in a skill context (D8§1): one sentence must have a skill cue
# directly before the word, or a product word directly after it.
DATABRICKS_CUES_BEFORE = [
    "experience with", "experience in", "experience using", "experience on",
    "knowledge of", "proficiency in", "proficiency with", "proficient in", "proficient with",
    "familiarity with", "familiar with", "expertise in", "expertise with", "skills in",
]
DATABRICKS_WORDS_AFTER = [
    "platform", "lakehouse", "notebooks", "notebook", "workflows", "jobs", "sql", "runtime",
    "clusters", "cluster", "certification", "certified",
]
DATABRICKS_SKILL_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    + "|".join(r"\s+".join(map(re.escape, c.split())) for c in DATABRICKS_CUES_BEFORE)
    + r")\s+(?:the\s+)?(?P<before>Databricks)(?![A-Za-z0-9])"
    + r"|(?<![A-Za-z0-9])(?P<after>Databricks)\s+(?:"
    + "|".join(map(re.escape, DATABRICKS_WORDS_AFTER))
    + r")(?![A-Za-z0-9])",
    re.I,
)

# Preferred words (D6-B§2 without "plus", D7§c) and the words that override them.
PREFERRED_RE = re.compile(r"\b(preferred|nice to have|nice-to-have|bonus)\b", re.I)
REQUIRED_RE = re.compile(r"\brequired\b|\bmust have\b", re.I)

# Check 4, years (D6-A§3, D2§3, D4§2).
MAX_YEARS = 3
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
_NUM = r"(?:\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)"
_YRS = r"(?:years?|yrs?)\b"
YEARS_RE = re.compile(
    rf"\bminimum(?:\s+of)?\s+(?P<min>{_NUM})\s*\+?\s*{_YRS}"
    rf"|\bat\s+least\s+(?P<least>{_NUM})\s*\+?\s*{_YRS}"
    rf"|\b(?P<lo>{_NUM})\s*[-–—]\s*{_NUM}\s*\+?\s*{_YRS}"
    rf"|\b(?P<more>{_NUM})\s+or\s+more\s+{_YRS}"
    rf"|\b(?P<plus>{_NUM})\s*\+\s*{_YRS}"
    rf"|\b(?P<bare>{_NUM})\s+{_YRS}",
    re.I,
)

ENTRY_LEVEL_PHRASES = [
    "entry-level", "entry level", "new grad", "new graduate", "early career", "early-career", "junior",
]  # D3§4, report only (D5§6)

# Check 5, clearance (D6-A§4).
CLEARANCE_PHRASES = [
    "clearance required",
    "active security clearance required",
    "must possess a Secret clearance",
    "Top Secret/SCI required",
    "must be able to obtain a security clearance",
]

# Check 6, sponsorship (D6-B§5, D6-B§6, D6-C§5, D7§a, D7§d).
OFFERED_PHRASES = [
    "visa sponsorship available",
    "visa sponsorship provided",
    "we offer visa sponsorship",
    "we provide visa sponsorship",
    "H-1B sponsorship available",
    "will sponsor work visas",
]
DENIED_PHRASES_CONTRACT = [
    "no visa sponsorship",
    "sponsorship is not available",
    "must not require sponsorship now or in the future",
]
# Wordings beyond the three, per D7§a. Approved 2026-10-29 in IMPLEMENTATION_CHOICES.md
# (my own approval step, not a contract requirement).
DENIED_PHRASES_APPROVED = [
    "visa sponsorship is not available",
    "not able to sponsor",
    "unable to sponsor",
    "will not sponsor",
    "does not sponsor",
    "do not sponsor",
    "cannot sponsor",
    "can't sponsor",
    "does not offer visa sponsorship",
    "do not offer visa sponsorship",
    "not eligible for visa sponsorship",
    "not eligible for sponsorship",
    "sponsorship will not be provided",
    "without the need for sponsorship",
    "without the need for visa sponsorship",
    "without sponsorship",
    "without visa sponsorship",
    "will not require sponsorship",
    "not require visa sponsorship now or in the future",
    "will not provide sponsorship",
    "does not provide sponsorship",
]

# Check 7, work arrangement (D6-C§10), report only (D0§4).
LOCATION_WORDS = [
    ("remote", "remote"),
    ("hybrid", "hybrid"),
    ("on-site", "onsite"),
    ("onsite", "onsite"),
    ("in office", "onsite"),
    ("in-office", "onsite"),
]

CHECK_NAMES = {
    1: "role phrase in title",
    2: "no seniority term in title",
    3: f"at least {MIN_SKILLS} matching résumé skills",
    4: f"minimum experience not above {MAX_YEARS} years",
    5: "no explicit security clearance requirement",
    6: "sponsorship not denied (profile.needs_sponsorship)",
    7: "location reported (never rejects)",
}

_RE_CACHE = {}


def phrase_re(phrase, flags=re.I):
    """Complete words or phrases: no letter or digit may touch either end."""
    key = (phrase, flags)
    if key not in _RE_CACHE:
        body = r"\s+".join(re.escape(w) for w in phrase.split())
        _RE_CACHE[key] = re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", flags)
    return _RE_CACHE[key]


def _clean(fragment):
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


# A heading is an <h1>-<h6>, or a <p> whose whole text is one <strong> or <b>.
_BLOCK_RE = re.compile(
    r"<(?P<h>h[1-6])\b[^>]*>(?P<htext>.*?)</(?P=h)\s*>"
    r"|<p\b[^>]*>\s*<(?P<b>strong|b)\b[^>]*>(?P<btext>.*?)</(?P=b)\s*>\s*</p\s*>"
    r"|<li\b[^>]*>(?P<li>.*?)</li\s*>",
    re.S | re.I,
)


def sentence_records(content):
    """(sentence, under_preferred_heading) pairs.

    Each list item is one sentence. A list item under a heading that contains a preferred
    word is marked as under a preferred heading, until the next heading. Headings are their
    own sentences. All other text is split on . ! ? followed by whitespace.
    """
    doc = html.unescape(content or "")  # Greenhouse returns the HTML entity-escaped
    records, rest, pos, under_preferred = [], [], 0, False
    for m in _BLOCK_RE.finditer(doc):
        rest.append(doc[pos:m.start()])
        pos = m.end()
        heading = m.group("htext") if m.group("h") else m.group("btext") if m.group("b") else None
        if heading is not None:
            text = _clean(heading)
            under_preferred = bool(PREFERRED_RE.search(text))
            records.append((text, False))
        else:
            records.append((_clean(m.group("li")), under_preferred))
    rest.append(doc[pos:])
    rest_text = _clean(" ".join(rest))
    records += [(s, False) for s in re.split(r"(?<=[.!?])\s+", rest_text)] if rest_text else []
    return [(s, flag) for s, flag in records if s]


def sentences(content):
    return [s for s, _ in sentence_records(content)]


def normalize_title(title):
    return re.sub(r"\s+", " ", TITLE_SEPARATORS.sub(" ", title.lower())).strip()


def is_optional(sentence, under_preferred_heading=False):
    """Preferred word (or a preferred heading above it), and no "required" / "must have"."""
    preferred = under_preferred_heading or bool(PREFERRED_RE.search(sentence))
    return preferred and not REQUIRED_RE.search(sentence)


def _number(token):
    token = token.lower()
    return int(token) if token.isdigit() else NUMBER_WORDS[token]


def _resume_strings(resume):
    """(field path, text) for every résumé field a skill can be cited from."""
    for section, items in resume.get("skills", {}).items():
        if section in EXCLUDED_SKILL_SECTIONS or not isinstance(items, list):
            continue
        for i, text in enumerate(items):
            yield f"skills.{section}[{i}]", text
    for key in ("experience", "projects"):
        for i, entry in enumerate(resume.get(key, [])):
            for field, value in entry.items():
                if isinstance(value, str):
                    yield f"{key}[{i}].{field}", value
                elif isinstance(value, list):
                    for j, text in enumerate(value):
                        if isinstance(text, str):
                            yield f"{key}[{i}].{field}[{j}]", text


def countable_skills(resume):
    """Skill name -> every résumé field it appears in. Each skill counts once (D7§b)."""
    names = []
    for section, items in resume.get("skills", {}).items():
        if section not in EXCLUDED_SKILL_SECTIONS and isinstance(items, list):
            names += [n for n in items if n not in names]
    for key in ("experience", "projects"):
        texts = [t for path, t in _resume_strings(resume) if path.startswith(key)]
        for tool in TOOLS_FROM_EXPERIENCE:
            if tool not in names and any(phrase_re(tool, 0).search(t) for t in texts):
                names.append(tool)
    fields = list(_resume_strings(resume))
    return {n: [path for path, text in fields if phrase_re(n).search(text)] for n in names}


def _find(patterns, sources):
    """First match of any pattern per source field, as evidence."""
    found = []
    for field, text in sources:
        for pattern in patterns:
            m = phrase_re(pattern).search(text)
            if m:
                found.append({"posting_field": field, "phrase": m.group(0)})
                break
    return found


def _phrases_in(phrases, records):
    hits = []
    for s, under_preferred in records:
        for p in phrases:
            m = phrase_re(p).search(s)
            if m:
                hits.append({"posting_field": "content", "phrase": m.group(0), "sentence": s,
                             "under_preferred_heading": under_preferred})
    return hits


def _databricks_in_skill_context(title, sents):
    for field, s in [("title", title)] + [("content", s) for s in sents]:
        m = DATABRICKS_SKILL_RE.search(s)
        if m:
            return [{"posting_field": field, "phrase": m.group(0), "sentence": s}]
    return []


def _check(number, passed, reason, evidence=None):
    return {"check": number, "name": CHECK_NAMES[number], "passed": passed, "reason": reason,
            "evidence": evidence or []}


def judge(posting, resume, profile):
    title = posting.get("title", "")
    location = (posting.get("location") or {}).get("name", "")
    records = sentence_records(posting.get("content", ""))
    sents = [s for s, _ in records]
    content_text = " ".join(sents)
    checks = []

    # 1. role phrase
    norm = normalize_title(title)
    roles = [p for p in ROLE_PHRASES if f" {p} " in f" {norm} "]
    checks.append(_check(1, bool(roles),
                         f"title contains {roles}" if roles else "title contains no approved role phrase",
                         [{"posting_field": "title", "phrase": p} for p in roles]))

    # 2. seniority
    senior = sorted({m.group(0) for m in SENIORITY_RE.finditer(norm)})
    checks.append(_check(2, not senior,
                         f"title contains seniority term(s) {senior}" if senior else "no seniority term in title",
                         [{"posting_field": "title", "phrase": s} for s in senior]))

    # 3. skills
    sources = [("title", title), ("content", content_text)]
    matched = []
    for name, cited in countable_skills(resume).items():
        if name == "Databricks":
            hits = _databricks_in_skill_context(title, sents)
        else:
            hits = _find([name] + ALIASES.get(name, []), sources)
        if hits:
            matched.append({"skill": name, "resume_fields": cited, "posting_evidence": hits})
    familiar = [n for n in resume.get("skills", {}).get("familiar_with_not_shipped", [])
                if _find([n], sources)]
    checks.append(_check(3, len(matched) >= MIN_SKILLS,
                         f"{len(matched)} matching résumé skill(s): {[m['skill'] for m in matched]}",
                         [{"skill": m["skill"], "resume_fields": m["resume_fields"]} for m in matched]))

    # 4. years
    year_hits = []
    for field, s, under_preferred in [("title", title, False)] + [("content", s, f) for s, f in records]:
        optional = is_optional(s, under_preferred)
        for m in YEARS_RE.finditer(s):
            token = next(v for v in m.groupdict().values() if v)
            year_hits.append({"posting_field": field, "phrase": m.group(0), "minimum": _number(token),
                              "optional": optional, "under_preferred_heading": under_preferred, "sentence": s})
    mandatory = [h for h in year_hits if not h["optional"]]
    min_years = max(h["minimum"] for h in mandatory) if mandatory else "not specified"
    years_ok = min_years == "not specified" or min_years <= MAX_YEARS
    checks.append(_check(4, years_ok,
                         "no mandatory minimum stated" if min_years == "not specified"
                         else f"highest mandatory minimum is {min_years} years", year_hits))

    entry_level = sorted({h["phrase"].lower() for h in _find_all(ENTRY_LEVEL_PHRASES, sources)})

    # 5. clearance
    clearance = [dict(h, optional=is_optional(h["sentence"], h["under_preferred_heading"]))
                 for h in _phrases_in(CLEARANCE_PHRASES, records)]
    required_clearance = [h for h in clearance if not h["optional"]]
    checks.append(_check(5, not required_clearance,
                         "explicit clearance requirement" if required_clearance
                         else ("clearance mentioned only as optional" if clearance else "no clearance requirement"),
                         clearance))

    # 6. sponsorship
    denied = _phrases_in(DENIED_PHRASES_CONTRACT + DENIED_PHRASES_APPROVED, records)
    offered = _phrases_in(OFFERED_PHRASES, records)
    sponsorship = "denied" if denied else "offered" if offered else "unknown"
    needs = profile.get("needs_sponsorship") is True
    checks.append(_check(6, not (needs and denied),
                         f"sponsorship {sponsorship}; profile.needs_sponsorship is {profile.get('needs_sponsorship')}",
                         denied + offered))

    # 7. work arrangement, report only
    in_loc = sorted({kind for word, kind in LOCATION_WORDS if phrase_re(word).search(location)})
    in_desc = sorted({kind for word, kind in LOCATION_WORDS if phrase_re(word).search(content_text)})
    kinds = sorted(set(in_loc) | set(in_desc))
    arrangement = "not specified" if not kinds else kinds[0] if len(kinds) == 1 else "conflict"
    conflict = {"location.name": in_loc, "content": in_desc} if len(kinds) > 1 else None
    checks.append(_check(7, True, f"work arrangement {arrangement}"))

    failed = [c for c in checks if not c["passed"]]
    verdict = "not relevant" if failed else "relevant"
    explanation = (
        "; ".join(f"check {c['check']} failed: {c['reason']}" for c in failed)
        if failed else "all checks passed"
    ) + (f". Skills cited from résumé: " + ", ".join(f"{m['skill']} ({', '.join(m['resume_fields'])})"
                                                   for m in matched) if matched else ". No résumé skills matched")

    return {
        "label": "record",
        "posting_id": posting.get("id"),
        "title": title,
        "company": COMPANY,
        "location": location,
        "url": posting.get("absolute_url"),
        "verdict": verdict,
        "failed_checks": [{"check": c["check"], "name": c["name"], "reason": c["reason"], "evidence": c["evidence"]}
                          for c in failed],
        "checks": checks,
        "matched_skills": matched,
        "familiar_not_counted": familiar,
        "min_years_required": min_years,
        "entry_level_phrases": entry_level,
        "sponsorship": {"value": sponsorship, "evidence": denied or offered,
                        "profile_field": "profile.needs_sponsorship"},
        "work_arrangement": arrangement,
        "work_arrangement_conflict": conflict,
        "explanation": explanation,
    }


def _find_all(patterns, sources):
    found = []
    for field, text in sources:
        for pattern in patterns:
            for m in phrase_re(pattern).finditer(text):
                found.append({"posting_field": field, "phrase": m.group(0)})
    return found


def judge_all(postings, resume, profile):
    return [judge(p, resume, profile) for p in postings]
