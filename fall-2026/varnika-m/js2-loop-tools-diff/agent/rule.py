"""The deterministic rule: Rules 1-5 of CONTRACT.md section 4.

Every check names the posting field and résumé field it compared, with their values,
so anyone can recompute the verdict from the saved response and the persona file.
"""

import html
import re

TITLE_PHRASES = ["Software Engineer", "Backend Engineer", "Infrastructure Engineer", "Platform Engineer",
                 "Site Reliability Engineer", "DevOps Engineer", "Data Engineer", "Cloud Engineer"]
SENIORITY_WORDS = ["Senior", "Sr", "Staff", "Principal", "Lead", "Manager", "Director", "Head", "VP",
                   "Intern", "Internship"]
US_CODES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM "
            "NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
US_LOCATION = re.compile(r"(?i:United States)|, (?:%s)(?![A-Za-z0-9])" % "|".join(US_CODES))
SKILL_FIELDS = ["languages", "backend_automation", "database_cloud", "devops_cicd"]
MAX_YEARS = 3

# Digit-based years phrases only; numbers written as words are not counted (Rule 4).
YEARS_PATTERNS = [
    (re.compile(r"(?<![\d.])(\d+)\s*\+\s*years(?![A-Za-z])", re.I), lambda m: int(m.group(1))),
    (re.compile(r"(?<![A-Za-z])at least (\d+) years(?![A-Za-z])", re.I), lambda m: int(m.group(1))),
    (re.compile(r"(?<![\d.])(\d+)\s*[-–—]\s*(\d+)\s*years(?![A-Za-z])", re.I),
     lambda m: max(int(m.group(1)), int(m.group(2)))),
]


def term_pattern(term):
    """Case-insensitive, complete words: no letter or digit right before or after."""
    return re.compile(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(term), re.I)


def description_text(content):
    """Greenhouse sends HTML that is itself HTML-escaped: decode, drop the tags, decode again."""
    markup = html.unescape(content or "")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup))).strip()


def experience_months(resume):
    months = 0
    for job in resume.get("experience", []):
        (y1, m1), (y2, m2) = [map(int, job[k].split("-")[:2]) for k in ("start_date", "end_date")]
        months += (y2 - y1) * 12 + (m2 - m1)
    return months


def resume_skills(resume):
    """(skill, résumé field) pairs from the four skill lists Rule 5 reads."""
    pairs, seen = [], set()
    for field in SKILL_FIELDS:
        for skill in resume.get("skills", {}).get(field, []):
            if skill.lower() not in seen:
                seen.add(skill.lower())
                pairs.append((skill, "skills." + field))
    return pairs


def find_skills(title, description, resume):
    matches = []
    for skill, field in resume_skills(resume):
        found_in = [name for name, text in (("title", title), ("content", description))
                    if term_pattern(skill).search(text)]
        if found_in:
            matches.append({"skill": skill, "resume_field": field, "posting_fields": found_in})
    return matches


def years_phrases(description):
    found = []
    for pattern, years in YEARS_PATTERNS:
        for m in pattern.finditer(description):
            found.append((m.start(), {"phrase": m.group(0), "years": years(m)}))
    return [item for _, item in sorted(found, key=lambda pair: pair[0])]


def judge(posting, resume):
    title = posting.get("title") or ""
    location = (posting.get("location") or {}).get("name") or ""
    description = description_text(posting.get("content"))
    months = "%d months" % experience_months(resume)
    experience_dates = "experience[].start_date, experience[].end_date"

    roles = [p for p in TITLE_PHRASES if term_pattern(p).search(title)]
    r1 = {"rule": "R1", "name": "Job title", "passed": bool(roles),
          "posting_field": "title", "posting_value": title,
          "resume_field": "experience[].title", "resume_value": [j.get("title") for j in resume.get("experience", [])],
          "explanation": ('title contains "%s"' % roles[0]) if roles
          else "title contains none of: " + ", ".join(TITLE_PHRASES)}

    senior = [w for w in SENIORITY_WORDS if term_pattern(w).search(title)]
    r2 = {"rule": "R2", "name": "Seniority", "passed": not senior, "excluded_words_found": senior,
          "posting_field": "title", "posting_value": title,
          "resume_field": experience_dates, "resume_value": months,
          "explanation": ("title contains excluded word(s): " + ", ".join(senior)) if senior
          else "title contains none of the excluded seniority words"}

    us = [part.strip() for part in re.split(r"[|;]", location) if US_LOCATION.search(part)]
    r3 = {"rule": "R3", "name": "Location", "passed": bool(us), "us_locations": us,
          "posting_field": "location.name", "posting_value": location,
          "resume_field": "personal.location", "resume_value": resume.get("personal", {}).get("location"),
          "explanation": ("US location(s): " + "; ".join(us)) if us
          else "no location in location.name has \"United States\" or a US state/DC code after a comma"}

    years = years_phrases(description)
    highest = max((y["years"] for y in years), default=None)
    r4 = {"rule": "R4", "name": "Experience", "passed": highest is None or highest <= MAX_YEARS,
          "years_found": years, "posting_field": "content", "posting_value": [y["phrase"] for y in years],
          "resume_field": experience_dates, "resume_value": months,
          "explanation": "no digit-based years phrase in the description" if highest is None
          else "highest years phrase is %d (limit %d)" % (highest, MAX_YEARS)}

    skills = find_skills(title, description, resume)
    r5 = {"rule": "R5", "name": "Skills", "passed": len(skills) >= 2, "matches": skills,
          "posting_field": "title, content", "posting_value": [m["skill"] for m in skills],
          "resume_field": ", ".join("skills." + f for f in SKILL_FIELDS),
          "resume_value": [skill for skill, _ in resume_skills(resume)],
          "explanation": "%d skill(s) found, 2 needed%s" % (len(skills), "".join(
              "; %s (%s, in %s)" % (m["skill"], m["resume_field"], " and ".join(m["posting_fields"]))
              for m in skills))}

    checks = [r1, r2, r3, r4, r5]
    return {"kind": "record", "verdict": "MATCH" if all(c["passed"] for c in checks) else "NOT_MATCH",
            "checks": checks}
