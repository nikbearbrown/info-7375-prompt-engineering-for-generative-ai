"""Contract §4: the written rule. Deterministic, so anyone can recompute it (label: record)."""
import html
import re

SENIOR = ["Senior", "Sr.", "Staff", "Principal", "Lead", "Director", "Head", "Manager", "III"]
STATES = set(("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND "
              "OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split())
CITIZEN = ["U.S. citizen", "US citizen", "United States citizen", "U.S. citizenship", "US citizenship",
           "green card", "permanent resident", "security clearance", "ITAR"]
EEO = ["regardless of", "without regard to", "discriminate"]
NO_SPONSOR = ["will not sponsor", "won't sponsor", "unable to sponsor", "not able to sponsor", "cannot sponsor",
              "do not sponsor", "does not sponsor", "not offer sponsorship", "sponsorship is not available",
              "sponsorship not available", "without sponsorship", "without the need for sponsorship",
              "without requiring sponsorship", "no sponsorship"]
YEARS = [r"(\d+)\s*\+\s*years", r"(\d+)\s+or\s+more\s+years", r"at\s+least\s+(\d+)\s+years",
         r"minimum\s+of\s+(\d+)\s+years", r"minimum\s+(\d+)\s+years", r"(\d+)\s*(?:-|–|to)\s*\d+\s+years",
         r"(\d+)\s+years\s+of"]


def plain(content):
    """Greenhouse `content` is HTML-escaped HTML: unescape, drop tags, collapse spaces."""
    t = html.unescape(html.unescape(content or ""))
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def word_in(needle, text):
    return re.search(r"(?<![A-Za-z0-9])" + re.escape(needle) + r"(?![A-Za-z0-9])", text, re.I) is not None


ABBREV = {"U.S.": "U․S․", "Ph.D.": "Ph․D․", "e.g.": "e․g․", "i.e.": "i․e․"}


def sentences(text):
    """Split on sentence ends, but not inside 'U.S.', 'Ph.D.', 'e.g.', 'i.e.' (found by test_r5: 'U.S. citizen' was cut in two)."""
    for k, v in ABBREV.items():
        text = text.replace(k, v)
    out = re.split(r"(?<=[.!?])\s+", text)
    for k, v in ABBREV.items():
        out = [s.replace(v, k) for s in out]
    return out


def stated_minimums(text):
    """Every stated minimum of years. Ranges are read first and masked, so '2-4 years of' gives 2, not also 4
    (found by test_r4: the 'N years of' pattern caught the range's upper bound)."""
    mins = []
    rng = r"(\d+)\s*(?:-|–|to)\s*\d+\s+years"
    mins += [int(m) for m in re.findall(rng, text, re.I)]
    rest = re.sub(rng, " ", text, flags=re.I)
    for pat in YEARS:
        if pat == r"(\d+)\s*(?:-|–|to)\s*\d+\s+years":
            continue
        mins += [int(m) for m in re.findall(pat, rest, re.I)]
    return sorted(set(mins))


MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                        "september", "october", "november", "december"], 1)}
SEASONS = {"spring": 5, "summer": 8, "fall": 12, "autumn": 12, "winter": 2}
DATE_RE = re.compile(r"\b(" + "|".join(list(MONTHS) + list(SEASONS)) + r")(?:\s*/\s*(?:" + "|".join(SEASONS) + r"))?\s+(20\d\d)\b", re.I)


def graduation_window(text):
    """R9 (revision 2026-10-30): the posting's graduation window as (start, end) 'YYYY-MM' strings, None if unstated.
    A season pair like 'spring/summer 2028' is read at its first season, so the window ends there (stated limit)."""
    for s in sentences(text):
        low = s.lower()
        if "graduat" not in low and not ("complete" in low and "degree" in low):
            continue
        dates = []
        for m in DATE_RE.finditer(s):
            word, year = m.group(1).lower(), int(m.group(2))
            dates.append(f"{year}-{(MONTHS.get(word) or SEASONS[word]):02d}")
        if not dates:
            continue
        if re.search(r"\bor earlier\b|\bby\b|\bbefore\b", low):
            return (None, max(dates))
        return (min(dates), max(dates))
    return None


PROVINCES = set("AB BC MB NB NL NS NT NU ON PE QC SK YT".split())


def _segment_is_us(seg):
    """R3 for one ';'-separated location segment. Revision 2026-10-30: a segment that also names a Canadian
    province (e.g. 'Toronto, ON, CA') reads its trailing CA as Canada, not California."""
    if re.search(r"\b(United States|USA|US)\b", seg):
        return True
    codes = re.findall(r",\s*([A-Z]{2})\b", seg)
    if any(c in PROVINCES for c in codes):
        return False
    return any(c in STATES for c in codes)


def _r(check, resume_field, posting_field, ok, evidence):
    return {"check": check, "resume_field": resume_field, "posting_field": posting_field,
            "result": "pass" if ok else "fail", "evidence": evidence}


def judge(posting, resume):
    title = posting.get("title", "")
    loc = (posting.get("location") or {}).get("name", "")
    text = plain(posting.get("content", ""))
    wa = resume["work_authorization"]
    exp = resume["experience_years"]
    out = []

    hits = [t for t in resume["target_roles"] if t.lower() in title.lower()]
    out.append(_r("R1", "target_roles", "title", bool(hits), f"title '{title}' contains {hits or 'no target role'}"))

    if exp < 3:
        sen = [w for w in SENIOR if word_in(w, title)]
        out.append(_r("R2", "experience_years", "title", not sen, f"title '{title}' senior words: {sen or 'none'}"))
    else:
        out.append(_r("R2", "experience_years", "title", True, f"does not apply (experience_years={exp})"))

    us = any(_segment_is_us(seg) for seg in loc.split(";"))
    country_ok = us if wa["country"] == "US" else False
    out.append(_r("R3", "work_authorization.country", "location.name", country_ok,
                  f"location '{loc}' {'is' if country_ok else 'is not shown to be'} in {wa['country']}"))

    if exp < 3:
        mins = stated_minimums(text)
        over = [m for m in mins if m >= 3]
        out.append(_r("R4", "experience_years", "content", not over, f"stated minimum years: {mins or 'none'}"))
    else:
        out.append(_r("R4", "experience_years", "content", True, f"does not apply (experience_years={exp})"))

    if not wa["us_citizen"]:
        found = [p for s in sentences(text) if not any(e in s.lower() for e in EEO)
                 for p in CITIZEN if word_in(p, s)]   # whole words: 'ITAR' once matched inside 'military'
        out.append(_r("R5", "work_authorization.us_citizen", "content", not found, f"citizenship/clearance phrases: {sorted(set(found)) or 'none'}"))
    else:
        out.append(_r("R5", "work_authorization.us_citizen", "content", True, "does not apply (us_citizen=true)"))

    if wa["needs_sponsorship"]:
        found = [p for p in NO_SPONSOR if word_in(p, text)]
        out.append(_r("R6", "work_authorization.needs_sponsorship", "content", not found, f"no-sponsorship phrases: {found or 'none'}"))
    else:
        out.append(_r("R6", "work_authorization.needs_sponsorship", "content", True, "does not apply (needs_sponsorship=false)"))

    has_phd = any(str(e.get("degree", "")).lower() in ("phd", "ph.d.", "doctorate") for e in resume["education"])
    if not has_phd:
        req = [s for s in sentences(text)
               if re.search(r"\b(PhD|Ph\.D\.|doctorate|doctoral)", s, re.I)
               and re.search(r"\b(required|requires|must)\b", s, re.I) and "preferred" not in s.lower()]
        out.append(_r("R7", "education[].degree", "content", not req, f"PhD-required sentences: {len(req)}"))
    else:
        out.append(_r("R7", "education[].degree", "content", True, "does not apply (has a PhD)"))

    win = graduation_window(text)
    edu = resume["education"][0]
    g0, g1 = edu.get("graduation"), edu.get("graduation_latest") or edu.get("graduation")
    if win is None or not g0:
        out.append(_r("R9", "education[0].graduation", "content", True,
                      "no graduation window stated" if win is None else "persona has no graduation date"))
    else:
        start, end = win
        ok = (start is None or g1 >= start) and (end is None or g0 <= end)
        out.append(_r("R9", "education[0].graduation", "content", ok,
                      f"posting window {start or '…'} to {end or '…'}; persona {g0} to {g1}"))

    sk = [s for s in resume["skills"] if word_in(s, text)]
    out.append(_r("R8", "skills", "content", len(sk) >= 2, f"résumé skills found in content: {sk}"))

    verdict = "relevant" if all(c["result"] == "pass" for c in out) else "not_relevant"
    return {"verdict": verdict, "label": "record", "reasons": out}
