"""Rule judge (CONTRACT.md §4) and its justification (§2)."""

import html
import re

_TAG = re.compile(r"<[^>]*>")
_WHITESPACE = re.compile(r"\s+")

SKILLS_NEEDED = 2


def clean_content(content):
    """§4 cleanup steps 2-4. Step 1 (JSON parse) already ran in state.parse_board_response."""
    text = html.unescape(content)  # step 2: &lt;p&gt; becomes <p>
    text = _TAG.sub(" ", text)  # step 3: every <...> tag becomes a space
    return _WHITESPACE.sub(" ", text)  # step 4: collapse every whitespace run


def clean_field(value):
    """§4 cleanup for title and location.name: trim both ends, collapse inner whitespace."""
    return _WHITESPACE.sub(" ", value).strip()


def posting_field(posting, name):
    """The cleaned value of a §6 posting field name, or None when the posting lacks it."""
    if name == "content":
        raw = posting.get("content")
        return clean_content(raw) if isinstance(raw, str) else None
    if name == "title":
        raw = posting.get("title")
    elif name == "location.name":
        location = posting.get("location")
        raw = location.get("name") if isinstance(location, dict) else None
    else:
        raise ValueError(f"not a §6 posting field: {name!r}")
    return clean_field(raw) if isinstance(raw, str) else None


def find_term(term, text):
    """Case-insensitive plain substring (§4). Returns the text as it appears, or None."""
    if text is None:
        return None
    match = re.search(re.escape(term), text, re.IGNORECASE)
    return match.group(0) if match else None


def _hits(terms, text):
    """(résumé term, matched posting text) for every term found in text."""
    return [(term, found) for term in terms if (found := find_term(term, text)) is not None]


def judge(posting, persona):
    """Apply C1, C2 and C3 (always all three). Returns (rule_verdict, rule_justification)."""
    titles = list(persona["target_titles"])
    locations = list(persona["locations"])
    skills = list(dict.fromkeys(persona["skills"]))
    title = posting_field(posting, "title")
    location = posting_field(posting, "location.name")
    content = posting_field(posting, "content")

    c1 = _hits(titles, title)
    c2 = _hits(locations, location)
    if not c2 and location is not None and location.lower() == "remote":
        c2 = [(entry, location) for entry in locations if entry.lower().startswith("remote")]
    c3 = _hits(skills, content)  # skills are de-duplicated, so each counts once

    results = {"C1": bool(c1), "C2": bool(c2), "C3": len(c3) >= SKILLS_NEEDED}
    verdict = "relevant" if all(results.values()) else "not_relevant"
    justification = {
        # Every résumé value a condition was compared against.
        "resume_fields": [
            {"field": field, "value": value}
            for field, values in (("target_titles", titles), ("locations", locations), ("skills", skills))
            for value in values
        ],
        # Matched terms only, never the whole content.
        "posting_fields": [
            {"field": field, "matched": found}
            for field, hits in (("title", c1), ("location.name", c2), ("content", c3))
            for _, found in hits
        ],
        "conditions": {
            "C1": {
                "result": results["C1"],
                "resume_field": "target_titles",
                "resume_values": titles,
                "matched_resume_values": [term for term, _ in c1],
                "posting_field": "title",
                "posting_value": title,
            },
            "C2": {
                "result": results["C2"],
                "resume_field": "locations",
                "resume_values": locations,
                "matched_resume_values": [term for term, _ in c2],
                "posting_field": "location.name",
                "posting_value": location,
            },
            # Decision 2026-10-27: C3 records the skills found, never the content text.
            "C3": {
                "result": results["C3"],
                "resume_field": "skills",
                "resume_values": skills,
                "matched_resume_values": [term for term, _ in c3],
                "posting_field": "content",
                "content_present": content is not None,
                "distinct_skills_found": len(c3),
                "distinct_skills_needed": SKILLS_NEEDED,
            },
        },
        "failing_conditions": [name for name, passed in results.items() if not passed],
    }
    return verdict, justification
