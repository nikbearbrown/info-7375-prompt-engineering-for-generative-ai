"""The written rule: seven checks, in order (CONTRACT.md, The rule). Its verdict is a record.

Anyone can recompute it by hand from the saved response and the résumé. The first check that fails
decides "not_relevant" and is the one cited; a relevant posting cites all seven.

How the contract's words are read here, in the order the checks use them:
- "Matching ignores case." Everything below compares lowercased text.
- A "word" (checks 3 and 4) is a whole word: no letter or digit right before or after it.
- "contains" (checks 4, 5 and 6) is plain containment, so "U.S. citizens" contains "U.S. citizen".
- Phrases are matched after runs of whitespace are collapsed to one space.
- Sentences (checks 5, 6 and 7) are split at ". ", "! ", "? " and line breaks, as the contract says. So a month
  written "Jan. 2027" is split from its year, and "U.S. export control" starts a new sentence at "export".
- Check 7 reads "years" only, as the contract writes it: "1 year" and "a 4 year degree" are not read.
"""

from __future__ import annotations

import re

LEVEL_WORDS = ("Senior", "Sr", "Staff", "Principal", "Lead", "Manager", "Director", "Head", "Distinguished",
               "Fellow", "VP", "Chief", "Architect", "Intern", "Internship")
US_PERSON_PHRASES = ("U.S. person", "US person", "U.S. citizen", "US citizen", "security clearance", "TS/SCI",
                     "Top Secret", "green card", "permanent resident")
SPONSORSHIP_PHRASES = ("unable to sponsor", "not able to sponsor", "cannot sponsor", "will not sponsor",
                       "does not sponsor", "do not sponsor", "no sponsorship", "without sponsorship",
                       "sponsorship is not available")
START_PHRASES = ("start immediately", "immediate start", "available immediately", "start ASAP",
                 "start as soon as possible")
CAUTION_PHRASE = "export control"
MONTHS = {name: number for number, names in enumerate(
    [("january", "jan"), ("february", "feb"), ("march", "mar"), ("april", "apr"), ("may",), ("june", "jun"),
     ("july", "jul"), ("august", "aug"), ("september", "sept", "sep"), ("october", "oct"), ("november", "nov"),
     ("december", "dec")], start=1) for name in names}
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "nine": 9, "ten": 10}
_NUM = r"(?:\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)"
# "N years", "N+ years", "N-M years" (hyphen or en dash), "N to M years", "N or more years".
YEARS = re.compile(
    rf"(?<![\w.])(?P<n>{_NUM})(?:\s*\+|\s*[-–]\s*{_NUM}\s*\+?|\s+to\s+{_NUM}|\s+or\s+more)?\s*years(?![a-z])",
    re.IGNORECASE)
_MONTH_YEAR = re.compile(r"(?<![a-z])(" + "|".join(sorted(MONTHS, key=len, reverse=True)) + r")\.?,?\s+(\d{4})(?!\d)",
                         re.IGNORECASE)
_ROLE_END = re.compile(r",|\||\(| [-–—] ")

CHECK_NAMES = {1: "employment type", 2: "location", 3: "level", 4: "role", 5: "status", 6: "start date",
               7: "years of experience"}


def judge(job: dict, resume: dict) -> dict:
    """The rule's verdict on one posting, with the citations the contract's Out section asks for."""
    checks, cautions = [], []
    for number, check in enumerate(CHECKS, start=1):
        result = check(job, resume)
        result.update(number=number, name=CHECK_NAMES[number])
        checks.append(result)
        if not result["passed"]:
            return _verdict("not_relevant", checks, [], number)
    for sentence in sentences(job.get("descriptionPlain") or ""):
        if CAUTION_PHRASE in _flat(sentence).lower():
            cautions.append(_flat(sentence).strip())
    return _verdict("relevant", checks, cautions, None)


def _verdict(verdict, checks, cautions, deciding):
    lines = []
    for c in checks:
        lines.append(f"Check {c['number']} ({c['name']}): {'passes' if c['passed'] else 'FAILS'}. {c['because']}")
    for quote in cautions:
        lines.append(f'Caution (not a blocker): descriptionPlain says "{quote}"')
    return {"judge": "rule", "label": "record", "verdict": verdict, "deciding_check": deciding,
            "checks": checks, "cautions": cautions, "lines": lines}


# The seven checks. Each returns passed, because (a sentence naming both fields), and the fields cited.

def check_employment_type(job, resume):
    wanted = resume["preferences"]["employment_types"]
    value = job.get("employmentType")
    passed = isinstance(value, str) and value.lower() in {w.lower() for w in wanted}
    return _cite(passed, "employmentType", value, "preferences.employment_types", wanted,
                 f"Posting employmentType is {_q(value)}; résumé preferences.employment_types is {_q(wanted)}.")


def check_location(job, resume):
    prefs = resume["preferences"]
    regions = {r.lower() for r in prefs["regions"]}
    cities = {c.lower() for c in prefs["cities"]}
    remote = {r.strip().lower() for r in prefs["remote_locations"]}
    places = [("location", job.get("location"), job.get("address"))]
    places += [(f"secondaryLocations[{i}].location", s.get("location"), s.get("address"))
               for i, s in enumerate(job.get("secondaryLocations") or []) if isinstance(s, dict)]
    for field, text, address in places:
        postal = address.get("postalAddress") if isinstance(address, dict) else None
        postal = postal if isinstance(postal, dict) else {}
        country = str(postal.get("addressCountry") or "")
        region = str(postal.get("addressRegion") or "")
        city = str(postal.get("addressLocality") or "")
        if country.lower() == "united states" and region.lower() in regions:
            return _cite(True, field, text, "preferences.regions", prefs["regions"],
                         f"Posting {field} {_q(text)} has address region {_q(region)} in the United States, "
                         f"which is in résumé preferences.regions {_q(prefs['regions'])}.")
        if country.lower() == "united states" and city.lower() in cities:
            return _cite(True, field, text, "preferences.cities", prefs["cities"],
                         f"Posting {field} {_q(text)} has address city {_q(city)} in the United States, "
                         f"which is in résumé preferences.cities {_q(prefs['cities'])}.")
        if isinstance(text, str) and text.strip().lower() in remote:
            return _cite(True, field, text, "preferences.remote_locations", prefs["remote_locations"],
                         f"Posting {field} is {_q(text)}, which is one of résumé preferences.remote_locations "
                         f"{_q(prefs['remote_locations'])}.")
    listed = "; ".join(f"{_q(text)}" for _, text, _ in places)
    return _cite(False, "location, secondaryLocations", listed,
                 "preferences.regions, preferences.cities, preferences.remote_locations",
                 [prefs["regions"], prefs["cities"], prefs["remote_locations"]],
                 f"Posting locations {listed} match none of résumé preferences.regions {_q(prefs['regions'])}, "
                 f"preferences.cities {_q(prefs['cities'])} or preferences.remote_locations "
                 f"{_q(prefs['remote_locations'])} (region and city count only with country United States).")


def check_level(job, resume):
    title = job.get("title") or ""
    have = resume["experience"]["full_time_years"]
    found = [w for w in LEVEL_WORDS if _has_word(title, w)]
    if found:
        return _cite(False, "title", title, "experience.full_time_years", have,
                     f"Posting title {_q(title)} contains the level word {_q(found[0])}. The level words are fixed "
                     f"in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check "
                     f"is experience.full_time_years {_q(have)}.")
    return _cite(True, "title", title, "experience.full_time_years", have,
                 f"Posting title {_q(title)} contains none of the level words (CONTRACT.md, check 3); résumé "
                 f"experience.full_time_years is {_q(have)}.")


def check_role(job, resume):
    prefs = resume["preferences"]
    title = job.get("title") or ""
    part = role_part(title)
    flat = _flat(part).lower()
    included = next((p for p in prefs["title_includes"] if _flat(p).lower() in flat), None)
    excluded = next((w for w in prefs["title_excludes"] if _has_word(part, w)), None)
    if included is None:
        return _cite(False, "title", title, "preferences.title_includes", prefs["title_includes"],
                     f"The role part of the title, {_q(part)}, contains none of résumé preferences.title_includes.")
    if excluded is not None:
        return _cite(False, "title", title, "preferences.title_excludes", prefs["title_excludes"],
                     f"The role part of the title, {_q(part)}, contains the word {_q(excluded)} from résumé "
                     f"preferences.title_excludes.")
    return _cite(True, "title", title, "preferences.title_includes, preferences.title_excludes",
                 [prefs["title_includes"], prefs["title_excludes"]],
                 f"The role part of the title, {_q(part)}, contains {_q(included)} from résumé "
                 f"preferences.title_includes and no word from preferences.title_excludes.")


def check_status(job, resume):
    auth = resume["work_authorization"]
    text = _flat(job.get("descriptionPlain") or "").lower()
    groups = []
    if auth["us_person"] is False:
        groups.append(("work_authorization.us_person", False, US_PERSON_PHRASES))
    if auth["needs_sponsorship"] is True:
        groups.append(("work_authorization.needs_sponsorship", True, SPONSORSHIP_PHRASES))
    for field, value, phrases in groups:
        for phrase in phrases:
            at = text.find(phrase.lower())
            if at >= 0:
                quote = _around(job.get("descriptionPlain") or "", phrase)
                return _cite(False, "descriptionPlain", quote, field, value,
                             f"Posting descriptionPlain says {_q(quote)}, which contains {_q(phrase)}; "
                             f"résumé {field} is {_q(value)}.")
    return _cite(True, "descriptionPlain", None, "work_authorization.us_person, work_authorization.needs_sponsorship",
                 [auth["us_person"], auth["needs_sponsorship"]],
                 "Posting descriptionPlain contains none of the status phrases for résumé "
                 f"work_authorization.us_person {_q(auth['us_person'])} and needs_sponsorship "
                 f"{_q(auth['needs_sponsorship'])}.")


def check_start_date(job, resume):
    earliest = resume["availability"]["earliest_full_time_start"]
    limit = (int(earliest[:4]), int(earliest[5:7]))
    description = job.get("descriptionPlain") or ""
    text = _flat(description).lower()
    for phrase in START_PHRASES:
        if phrase.lower() in text:
            quote = _around(description, phrase)
            return _cite(False, "descriptionPlain", quote, "availability.earliest_full_time_start", earliest,
                         f"Posting descriptionPlain says {_q(quote)}; résumé availability.earliest_full_time_start "
                         f"is {_q(earliest)}.")
    for sentence in sentences(description):
        if not _has_word(sentence, "start"):
            continue
        for month, year in _MONTH_YEAR.findall(sentence):
            when = (int(year), MONTHS[month.lower()])
            if when < limit:
                quote = _flat(sentence).strip()
                return _cite(False, "descriptionPlain", quote, "availability.earliest_full_time_start", earliest,
                             f"Posting descriptionPlain says {_q(quote)}, a start before résumé "
                             f"availability.earliest_full_time_start {_q(earliest)}.")
    return _cite(True, "descriptionPlain", None, "availability.earliest_full_time_start", earliest,
                 f"Posting descriptionPlain asks for no start before résumé availability.earliest_full_time_start "
                 f"{_q(earliest)}.")


def check_years(job, resume):
    have = resume["experience"]["full_time_years"]
    found = years_asked(job.get("descriptionPlain") or "")
    if not found:
        return _cite(True, "descriptionPlain", None, "experience.full_time_years", have,
                     "Posting descriptionPlain states no years of experience, which is not a requirement; "
                     f"résumé experience.full_time_years is {_q(have)}.")
    n, quote = min(found, key=lambda pair: pair[0])
    passed = n <= have
    return _cite(passed, "descriptionPlain", quote, "experience.full_time_years", have,
                 f"Posting descriptionPlain says {_q(quote)}, so N = {n}, which is "
                 f"{'at most' if passed else 'more than'} résumé experience.full_time_years {_q(have)}.")


CHECKS = (check_employment_type, check_location, check_level, check_role, check_status, check_start_date,
          check_years)


# Helpers, shared with the tests.

def role_part(title: str) -> str:
    """The title up to its first comma, "|", "(", or a spaced hyphen, en dash or em dash."""
    match = _ROLE_END.search(title)
    return (title[: match.start()] if match else title).strip()


def sentences(text: str) -> list:
    return [s for s in re.split(r"(?<=[.!?]) |\r\n|\r|\n", text) if s.strip()]


def years_asked(text: str) -> list:
    """(N, sentence) for every number of years in a sentence that contains "experience"."""
    found = []
    for sentence in sentences(text):
        if "experience" not in sentence.lower():
            continue
        for match in YEARS.finditer(sentence):
            word = match.group("n").lower()
            found.append((int(word) if word.isdigit() else NUMBER_WORDS[word], _flat(sentence).strip()))
    return found


def _has_word(text: str, word: str) -> bool:
    pattern = r"\s+".join(re.escape(piece) for piece in word.split())
    return re.search(rf"(?<![A-Za-z0-9]){pattern}(?![A-Za-z0-9])", text, re.IGNORECASE) is not None


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _around(text: str, phrase: str, width: int = 110) -> str:
    """The description's own words around the phrase (whitespace collapsed), cut at spaces, for the citation.

    A window, not a sentence: splitting at ". " would cut "U.S. person" in two.
    """
    flat = _flat(text)
    at = flat.lower().find(phrase.lower())
    if at < 0:
        return phrase
    start, end = max(0, at - width), min(len(flat), at + len(phrase) + width)
    if start > 0 and " " in flat[start:at]:
        start = flat.index(" ", start) + 1
    if end < len(flat) and " " in flat[at + len(phrase):end]:
        end = flat.rindex(" ", at + len(phrase), end)
    return ("..." if start > 0 else "") + flat[start:end].strip() + ("..." if end < len(flat) else "")


def _q(value) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(_q(v) for v in value) + "]"
    return "none" if value is None else str(value)


def _cite(passed, posting_field, posting_value, resume_field, resume_value, because):
    return {"passed": bool(passed), "posting_field": posting_field, "posting_value": posting_value,
            "resume_field": resume_field, "resume_value": resume_value, "because": because}
