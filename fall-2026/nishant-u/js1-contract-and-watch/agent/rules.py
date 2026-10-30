"""The rule R1-R4 from CONTRACT.md. Its verdict is a record: anyone can recompute it by hand.

Each verdict carries citations. A citation either quotes text found in a posting field,
or, for a check that passed or failed because something was absent, has quote None and
lists the absent_terms so the absence can be re-checked.
"""
import html
import re

POSTING_FIELDS = ("title", "location.name", "content")


def strip_html(content):
    # Greenhouse sends content as escaped HTML: unescape, drop tags, unescape entities left inside.
    text = re.sub(r"<[^>]+>", " ", html.unescape(content or ""))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def field_text(posting, field):
    if field == "title":
        return posting.get("title") or ""
    if field == "location.name":
        return (posting.get("location") or {}).get("name") or ""
    if field == "content":
        return strip_html(posting.get("content"))
    raise ValueError(f"unknown posting field: {field}")


def find_term(text, term):
    """The text that matches term as a whole word, ignoring case, or None."""
    match = re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.IGNORECASE)
    return match.group(0) if match else None


def shipped_skills(resume, requirements):
    """(list name, skill) for every skill in the shipped lists named in requirements."""
    found = []
    for field in requirements["skill_lists"]:
        value = resume["skills"].get(field)
        if not isinstance(value, list) or not all(isinstance(s, str) for s in value):
            raise ValueError(f"skills.{field} must be a list of strings")
        found.extend((field, skill) for skill in value)
    return found


def us_location_part(location, markers):
    """The first ;-separated part that ends in a US state marker or equals 'Remote - US'."""
    for part in (p.strip() for p in location.split(";")):
        for marker in markers:
            if marker.startswith(","):
                if part.lower().endswith(marker.lower()):
                    return part
            elif part.lower() == marker.lower():
                return part
    return None


def _cite(check, resume_field, posting_field, quote):
    return {"check": check, "resume_field": resume_field, "posting_field": posting_field, "quote": quote}


def _absent(check, resume_field, posting_field, terms):
    return dict(_cite(check, resume_field, posting_field, None), absent_terms=list(terms))


def _first_term(text, terms):
    return next((hit for hit in (find_term(text, t) for t in terms) if hit), None)


def evaluate(posting, resume, requirements, skills_fn=shipped_skills):
    citations = []

    def verdict(failed_check, justification):
        return {
            "posting_id": posting["id"],
            "title": posting.get("title"),
            "verdict": "not_relevant" if failed_check else "relevant",
            "label": "record",
            "failed_check": failed_check,
            "justification": justification,
            "citations": citations,
        }

    title = field_text(posting, "title")
    hit = _first_term(title, requirements["title_terms"])
    if not hit:
        citations.append(_absent("R1", None, "title", requirements["title_terms"]))
        return verdict("R1", f"R1 failed: title {title!r} contains none of the title terms.")
    citations.append(_cite("R1", None, "title", hit))

    excluded = _first_term(title, requirements["exclude_terms"])
    if excluded:
        citations.append(_cite("R2", None, "title", excluded))
        return verdict("R2", f"R2 failed: title {title!r} contains the excluded term {excluded!r}.")
    citations.append(_absent("R2", None, "title", requirements["exclude_terms"]))

    location = field_text(posting, "location.name")
    part = us_location_part(location, requirements["us_location_markers"])
    if not part:
        citations.append(_cite("R3", None, "location.name", location))
        return verdict("R3", f"R3 failed: no part of location.name {location!r} is a US location.")
    citations.append(_cite("R3", None, "location.name", part))

    content = field_text(posting, "content")
    by_list = {}
    for field, skill in skills_fn(resume, requirements):
        by_list.setdefault(field, []).append(skill)
    matched = []
    for field, skills in by_list.items():
        for skill in skills:
            quote = find_term(content, skill)
            if quote:
                matched.append((field, skill, quote))
    distinct = {skill.lower() for _, skill, _ in matched}
    if len(distinct) < requirements["min_skills"]:
        for field, skills in by_list.items():
            citations.append(_absent("R4", f"skills.{field}", "content", skills))
        return verdict("R4", f"R4 failed: content names fewer than {requirements['min_skills']} "
                             "skill(s) from the shipped skill lists.")
    for field, _, quote in matched:
        citations.append(_cite("R4", f"skills.{field}", "content", quote))
    return verdict(None, f"All four checks passed: title term {hit!r}, no excluded term, US location "
                         f"{part!r}, skills in content: {', '.join(q for _, _, q in matched)}.")


def judge_all(postings, resume, requirements):
    return [evaluate(p, resume, requirements) for p in postings]
