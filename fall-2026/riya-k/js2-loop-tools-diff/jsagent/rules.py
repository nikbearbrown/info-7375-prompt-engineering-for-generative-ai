"""The written rule from CONTRACT.md, as code. A rule verdict is a record: anyone can recompute it."""

import html
import re

TITLE_WORDS = ["AI", "LLM", "GenAI", "Generative AI", "ML", "Machine Learning", "Data Engineer",
               "Data Platform", "Data Scientist", "Data Science", "Analytics"]
SENIORITY_WORDS = ["Senior", "Sr", "Staff", "Principal", "Director", "VP", "Vice President", "Head", "Manager"]
# Skills that never count (CONTRACT.md, rule 2 and amendment 1).
NOT_COUNTED = {"databricks", "unity catalog"}  # amendment 1: Unity Catalog is boilerplate
SKIP_GROUPS = {"familiar_with_not_shipped", "agent_note"}
MIN_SKILLS = 2

US_STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
             "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
             "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
             "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
             "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
             "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
             "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "District of Columbia"]
US_CODES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
            "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
            "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
            "WI", "WY", "DC"]
US_MARKERS = ["United States", "USA", "US"] + US_STATES
# Non-US countries that turn "Remote" into a non-US location.
NON_US = ["Canada", "Mexico", "Brazil", "Costa Rica", "United Kingdom", "UK", "Ireland", "Germany", "France",
          "Netherlands", "Belgium", "Spain", "Portugal", "Italy", "Switzerland", "Sweden", "Denmark", "Norway",
          "Finland", "Poland", "Serbia", "Estonia", "India", "China", "Japan", "Korea", "Singapore",
          "Australia", "New Zealand", "Israel", "UAE", "EMEA", "APAC", "LATAM", "Europe", "Asia"]


def find_word(term, text, case_sensitive=False):
    """Whole-word match: the term may not sit inside a longer word (so 'SQL' does not match 'NoSQL')."""
    pattern = r"(?<![A-Za-z0-9])" + r"\s+".join(map(re.escape, term.split())) + r"(?![A-Za-z0-9])"
    return re.search(pattern, text, 0 if case_sensitive else re.IGNORECASE) is not None


def plain_text(content):
    """Greenhouse sends content as escaped HTML; unescape twice and drop tags."""
    text = html.unescape(html.unescape(content or ""))
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def resume_skills(resume):
    """(group, skill) pairs from the résumé's shipped skill groups."""
    pairs = []
    for group, items in resume.get("skills", {}).items():
        if group in SKIP_GROUPS or not isinstance(items, list):
            continue
        pairs += [(group, s) for s in items if s.lower() not in NOT_COUNTED]
    return pairs


def is_us_location(location):
    if any(find_word(m, location) for m in US_MARKERS if m != "US") or find_word("US", location, True):
        return True
    if any(find_word(c, location, True) for c in US_CODES):
        return True
    return find_word("Remote", location) and not any(find_word(c, location) for c in NON_US)


def judge(posting, resume):
    """Apply the CONTRACT.md rule. Returns a verdict dict whose justification cites résumé and posting fields."""
    title = posting.get("title", "")
    location = (posting.get("location") or {}).get("name", "")
    body = title + " " + plain_text(posting.get("content", ""))

    title_hits = [w for w in TITLE_WORDS if find_word(w, title)]
    senior_hits = [w for w in SENIORITY_WORDS if find_word(w, title)]
    skill_hits = [(g, s) for g, s in resume_skills(resume) if find_word(s, body)]
    us = is_us_location(location)

    relevant = bool(title_hits) and len(skill_hits) >= MIN_SKILLS and us and not senior_hits
    skills_cited = "; ".join(f"skills.{g}: {s}" for g, s in skill_hits) or "skills.*: none matched"
    reasons = [
        f"title '{title}' " + (f"has title word(s) {title_hits}" if title_hits else "has no title word"),
        f"{len(skill_hits)} of résumé skills in title/content ({skills_cited}); need {MIN_SKILLS}",
        f"location.name '{location}' is " + ("US/Remote" if us else "not US/Remote"),
    ]
    if senior_hits:
        reasons.append(f"title has seniority word(s) {senior_hits}")
    return {
        "id": posting["id"],
        "title": title,
        "location": location,
        "url": posting.get("absolute_url", ""),
        "judge": "rule",
        "kind": "record",
        "verdict": "relevant" if relevant else "not_relevant",
        "resume_fields": sorted({f"skills.{g}" for g, _ in skill_hits}) or ["skills"],
        "posting_fields": ["title", "content", "location.name"],
        "justification": "; ".join(reasons),
    }
