"""FILTER.md v1 section 5: label each shortlist claim against the posting's own text."""
import re

from .filter import is_us

REQUIRED_HEAD = re.compile(r"(?i)(requirement|qualification|you have|you'?ll need|what you need|who you are|"
                           r"minimum|must have|responsibilit|what you'?ll do|you will|the role|about you|"
                           r"what we'?re looking for|skills)")
PREFERRED_HEAD = re.compile(r"(?i)(preferred|nice[- ]to[- ]have|bonus|plus|desired|ideally)")
INLINE_PREF = re.compile(r"(?i)(\ba plus\b|\bis a bonus\b|\bnice[- ]to[- ]have\b|\bpreferred\b|\bideally\b|"
                         r"\bbonus\b)")
LANGS = re.compile(r"(?<![A-Za-z])(Java(?!Script)|JavaScript|TypeScript|Python|Ruby|Go(?![-\w])|Golang|Scala|"
                   r"Kotlin|Rust|C\+\+|C#|Swift|Objective-C|PHP|Elixir|Haskell|Clojure|Erlang|Perl|R(?= ,))")
SKILL_PATTERNS = {
    "Java": r"\bJava\b(?!Script)", "Spring Boot": r"\bSpring Boot\b", "SQL": r"(?<![A-Za-z])SQL\b",
    "AWS": r"\bAWS\b", "PostgreSQL": r"\bPostgre(SQL|s)\b", "REST APIs": r"\bREST(ful)?\b",
    "microservices": r"\bmicro-?services?\b", "distributed systems": r"\bdistributed systems?\b",
}
CASE_SENSITIVE = {"REST APIs", "AWS"}
EARLY_TITLE = re.compile(r"(?i)\b(intern|internship|new grad|early career|co-?op|university grad|graduate)\b")
EARLY_BODY = re.compile(r"(?i)(new grad|recent graduate|0[-–]2 years|0\+ years|1\+ years? of|early[- ]career)")
YEARS = re.compile(r"(?i)(\d{1,2})\s*(?:\+|[-–]\s*\d{1,2})?\s*\+?\s*years?")
EARLY_MAX_YEARS = 2  # FILTER.md s5 contradiction half, [Claude, pending]: min required years >= 3 contradicts


def _is_heading(line):
    s = line.strip()
    return bool(s) and not s.startswith("-") and len(s) <= 60 and not s.endswith(".")


def sections(body):
    """[(kind, line)] with kind in required / preferred / other, decided by the nearest heading above."""
    kind, out = "other", []
    body = (body or "").replace("\u2019", "'")  # Stripe/Notion use curly apostrophes in headings
    for line in body.splitlines():
        if _is_heading(line):
            if PREFERRED_HEAD.search(line):
                kind = "preferred"
            elif REQUIRED_HEAD.search(line):
                kind = "required"
            else:
                kind = "other"
            out.append((kind, line.strip()))
            continue
        k = kind
        if k == "required" and line.strip().startswith("-") and INLINE_PREF.search(line):
            k = "preferred"
        out.append((k, line.strip()))
    return out


def _find(skill, body):
    pat = SKILL_PATTERNS.get(skill, re.escape(skill))
    flags = 0 if skill in CASE_SENSITIVE else re.I
    return [(k, ln) for k, ln in sections(body) if re.search(pat, ln, flags)]


def _skill(claim, p):
    body, skill, strength = p.get("body", ""), claim["skill"], claim.get("strength", "required")
    is_lang_claim = skill in ("Java",)
    if is_lang_claim and not LANGS.search(body):
        return {"label": "insufficient", "answer": "I cannot tell", "quote": "",
                "why": "the posting names no programming language at all (abstention rule)"}
    hits = _find(skill, body)
    req = [ln for k, ln in hits if k == "required"]
    pref = [ln for k, ln in hits if k == "preferred"]
    if strength == "required":
        if req:
            return {"label": "supported", "quote": req[0], "why": f"{skill} appears under a required section"}
        if pref:
            return {"label": "contradicted", "quote": pref[0],
                    "why": f"{skill} appears only as preferred/optional, not required"}
        if hits:
            return {"label": "insufficient", "quote": hits[0][1],
                    "why": f"{skill} is mentioned only outside requirements/responsibilities"}
        return {"label": "insufficient", "quote": "", "why": f"{skill} is not mentioned"}
    # strength == preferred / mentioned
    if hits:
        return {"label": "supported", "quote": hits[0][1], "why": f"{skill} is mentioned ({hits[0][0]})"}
    return {"label": "insufficient", "quote": "", "why": f"{skill} is not mentioned"}


def min_required_years(body):
    found = []
    for k, ln in sections(body):
        if k == "required":
            for m in YEARS.finditer(ln):
                found.append((int(m.group(1)), ln))
    return min(found) if found else None


def _level(claim, p):
    title, body = p.get("title", ""), p.get("body", "")
    yrs = min_required_years(body)
    if yrs and yrs[0] > EARLY_MAX_YEARS:
        return {"label": "contradicted", "quote": yrs[1],
                "why": f"requires {yrs[0]}+ years, above early-career ({EARLY_MAX_YEARS} max)"}
    if EARLY_TITLE.search(title):
        return {"label": "supported", "quote": title, "why": "title names an intern/new-grad/early-career role"}
    m = EARLY_BODY.search(body)
    if m or (yrs and yrs[0] <= EARLY_MAX_YEARS):
        q = yrs[1] if yrs else m.group(0)
        return {"label": "supported", "quote": q, "why": "posting states an early-career experience level"}
    return {"label": "insufficient", "quote": "", "why": "posting states no experience level"}


def _us(claim, p):
    v = is_us(p.get("location"))
    if v is None:
        return {"label": "insufficient", "quote": p.get("location", ""), "why": "location missing or not specific"}
    return {"label": "supported" if v else "contradicted", "quote": p.get("location", ""),
            "why": "location is in the US" if v else "location is outside the US"}


def label_claim(claim, posting):
    t = claim["type"]
    if t == "skill":
        r = _skill(claim, posting)
    elif t == "level":
        r = _level(claim, posting)
    elif t == "us":
        r = _us(claim, posting)
    else:
        r = {"label": "insufficient", "quote": "", "why": f"unknown claim type {t}"}
    r.setdefault("answer", None)
    return r


def justify(posting, decision, rules):
    """The shortlist's claims for one kept posting: one per matched topic word + level + location."""
    claims = [{"type": "skill", "skill": rules["topic"][t]["label"], "strength": "required"}
              for t in decision["topics"]]
    claims.append({"type": "level", "value": "early-career"})
    claims.append({"type": "us"})
    return [{"claim": c, **label_claim(c, posting)} for c in claims]
