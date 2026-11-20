"""The written rule from CONTRACT.md section 5, made computable as INTERPRETATIONS.md says.
Its output is a record: anyone can recompute it from the posting and the resume."""
import re

TITLE_PHRASES = ["Software Engineer", "Software Developer", "Backend Engineer",
                 "Full Stack Engineer", "Full Stack Developer", "AI Engineer", "ML Engineer",
                 "Machine Learning Engineer", "LLM Engineer"]
DEPARTMENTS = ["Engineering", "Software Engineering", "Machine Learning", "AI",
               "Artificial Intelligence", "Data Science"]
EXCLUDED_TITLE_WORDS = ["Director", "Staff", "Principal", "Manager", "Lead"]
MIN_SKILLS = 2

US_STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
             "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
             "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
             "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
             "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
             "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
             "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
             "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen".split())}

NUM = r"\b(\d{1,2}|" + "|".join(NUMBER_WORDS) + r")"
YEARS_RE = re.compile(NUM + r"\s*\+?\s*(?:(?:-|–|to)\s*" + NUM + r"\s*\+?\s*)?years?\b([^.;]{0,60})",
                      re.IGNORECASE)
RELOCATION_RE = re.compile(r"must relocate|required to relocate|requires relocation|"
                           r"relocation (?:is )?required", re.IGNORECASE)
CONTRACT_TEXT_RE = re.compile(r"contract-only|contract only|contract position|contract role|\b1099\b",
                              re.IGNORECASE)


def term_re(term):
    """Whole term, case-insensitive: no letter or digit on either side."""
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", re.IGNORECASE)


def find_terms(terms, text):
    return [t for t in terms if term_re(t).search(text)]


def line(n, passed, resume_fields, posting_fields, detail):
    return {"n": n, "passed": passed, "resume_fields": resume_fields,
            "posting_fields": posting_fields, "detail": detail}


def c1_title(p, r):
    rf, pf = ["resume.target_roles"], ["posting.title"]
    if not p["title"]:
        return line(1, False, rf, pf, "posting.title is missing")
    hits = find_terms(TITLE_PHRASES, p["title"])
    if hits:
        return line(1, True, rf, pf, f"posting.title {p['title']!r} contains {hits[0]!r}")
    return line(1, False, rf, pf, f"posting.title {p['title']!r} contains none of the title phrases")


def c2_department(p, r):
    rf, pf = ["resume.target_roles"], ["posting.departments"]
    if not p["departments"]:
        return line(2, False, rf, pf, "posting.departments is missing")
    wanted = {d.lower() for d in DEPARTMENTS}
    hits = [d for d in p["departments"] if d.strip().lower() in wanted]
    if hits:
        return line(2, True, rf, pf, f"posting.departments includes {hits[0]!r}")
    return line(2, False, rf, pf, f"posting.departments {p['departments']} is not one of {DEPARTMENTS}")


def names_us(p):
    places = [p["location"]] + p["offices"]
    us = re.compile(r"United States|U\.S\.|\bUSA\b|\bUS\b")
    if any(us.search(x) for x in places) or us.search(p["content"]):
        return True
    remote_state = re.compile(r"Remote\s*\((" + "|".join(US_STATES) + r")\)", re.IGNORECASE)
    return any(remote_state.search(o) for o in p["offices"])


def c3_location(p, r):
    rf, pf = ["resume.location", "resume.remote_ok"], ["posting.location", "posting.offices"]
    if not p["location"] and not p["offices"]:
        return line(3, False, rf, pf, "posting.location is missing")
    if term_re("Boston").search(p["location"]):
        return line(3, True, rf, pf, f"posting.location {p['location']!r} is Boston, matching resume.location")
    remote = any(term_re("Remote").search(x) for x in [p["location"]] + p["offices"])
    if remote and r.get("remote_ok") and names_us(p):
        return line(3, True, rf, pf, f"posting.location {p['location']!r} / posting.offices {p['offices']} "
                                     "is remote within the United States and resume.remote_ok is true")
    if remote and not r.get("remote_ok"):
        why = "is remote but resume.remote_ok is false"
    elif remote:
        why = "says Remote but does not name the United States"
    else:
        why = f"is not Boston and not remote (resume.location {r.get('location')!r})"
    return line(3, False, rf, pf, f"posting.location {p['location']!r} {why}")


def c4_skills(p, r):
    rf, pf = ["resume.skills"], ["posting.content"]
    if not p["content"]:
        return line(4, False, rf, pf, "posting.content is missing")
    hits = find_terms(r.get("skills", []), p["content"])
    ok = len(hits) >= MIN_SKILLS
    return line(4, ok, rf, pf, f"posting.content mentions {len(hits)} of resume.skills {hits}"
                               f" ({'at least' if ok else 'fewer than'} {MIN_SKILLS})")


def to_int(s):
    return int(s) if s.isdigit() else NUMBER_WORDS[s.lower()]


def required_years(content):
    found = []
    for m in YEARS_RE.finditer(content):
        if "experience" in m.group(3).lower():
            found.append((to_int(m.group(1)), m.group(0)[:60].strip()))
    return max(found) if found else None


def c5_experience(p, r):
    rf, pf = ["resume.experience_years"], ["posting.content"]
    have = r.get("experience_years")
    req = required_years(p["content"])
    if req is None:
        return line(5, True, rf, pf, "posting.content: no experience requirement stated "
                                     "(passes without assuming a match)")
    years, phrase = req
    ok = years <= have
    return line(5, ok, rf, pf, f"posting.content requires {years} years ({phrase!r}); "
                               f"resume.experience_years is {have}")


def c6_exclusions(p, r, boston):
    rf, pf = ["resume.exclusions"], ["posting.title", "posting.content"]
    reasons = []
    words = find_terms(EXCLUDED_TITLE_WORDS, p["title"])
    if words:
        reasons.append(f"posting.title has excluded word {words[0]!r}")
    text = p["title"] + " " + p["content"]
    if term_re("unpaid").search(text):
        reasons.append("posting says unpaid")
    if find_terms(["Contract", "Contractor"], p["title"]) or CONTRACT_TEXT_RE.search(p["content"]):
        reasons.append("posting is contract-only")
    if RELOCATION_RE.search(p["content"]) and not boston:
        reasons.append("posting.content requires relocation outside Boston")
    if reasons:
        return line(6, False, rf, pf, "; ".join(reasons))
    return line(6, True, rf, pf, "posting.title and posting.content hit none of resume.exclusions")


def judge(p, r):
    """Apply all six conditions. Returns the record with verdict and justification."""
    lines = [c1_title(p, r), c2_department(p, r), c3_location(p, r), c4_skills(p, r),
             c5_experience(p, r)]
    lines.append(c6_exclusions(p, r, boston=bool(term_re("Boston").search(p["location"]))))
    failed = [l["n"] for l in lines if not l["passed"]]
    ordered = [l for l in lines if not l["passed"]] + [l for l in lines if l["passed"]]
    text = "\n".join(
        f"C{l['n']} {'PASS' if l['passed'] else 'FAIL'} [posting.id={p['id']}; "
        f"{', '.join(l['resume_fields'])}; {', '.join(l['posting_fields'])}]: {l['detail']}"
        for l in ordered)
    return {
        "posting_id": p["id"],
        "board_token": p["board_token"],
        "title": p["title"],
        "verdict": "Not Relevant" if failed else "Relevant",
        "failed_conditions": failed,
        "justification": text,
        "conditions": lines,
        "judge": "rule (record)",
    }
