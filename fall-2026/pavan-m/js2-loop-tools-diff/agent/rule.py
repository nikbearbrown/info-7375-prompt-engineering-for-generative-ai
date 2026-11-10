"""Deterministic relevance rule (the `record` verdict): title, skills and location must all pass."""

import html
import re

MIN_SKILLS = 3
TITLE_EXCLUSIONS = re.compile(r"\b(intern|internship|manager|director)\b", re.IGNORECASE)
_SCRIPT_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
_TAG = re.compile(r"<[^>]*>")
_WS = re.compile(r"\s+")


def clean_content(content) -> str:
    """Decode entities first (Glean escapes its markup), then drop script/style and tags, then normalize whitespace."""
    if not isinstance(content, str):
        return ""
    text = html.unescape(content)
    text = _SCRIPT_STYLE.sub(" ", text)
    # Tags become spaces so "<li>Java</li><li>Python</li>" does not fuse into one word.
    text = _TAG.sub(" ", text)
    return _WS.sub(" ", text).strip()


def _normalize(value) -> str:
    return _WS.sub(" ", value).strip() if isinstance(value, str) else ""


def _skill_pattern(skill: str) -> re.Pattern:
    # No letter or digit right before or after; internal spaces match any run of whitespace;
    # everything else (punctuation included) is literal.
    words = [re.escape(w) for w in skill.split()]
    return re.compile(r"(?<![^\W_])" + r"\s+".join(words) + r"(?![^\W_])", re.IGNORECASE)


def _title_check(title, target_titles) -> dict:
    title = title if isinstance(title, str) else ""
    if not title.strip():
        return {"passed": False, "matched": None, "posting_value": title, "reason": "posting title is missing or empty"}
    excluded = TITLE_EXCLUSIONS.search(title)
    if excluded:
        return {
            "passed": False,
            "matched": None,
            "posting_value": title,
            "reason": f"title contains excluded word {excluded.group(0)!r}",
        }
    for target in target_titles or []:
        if isinstance(target, str) and target.strip() and target.casefold() in title.casefold():
            return {"passed": True, "matched": target, "posting_value": title, "reason": f"title contains {target!r}"}
    return {"passed": False, "matched": None, "posting_value": title, "reason": "no target title is contained in the title"}


def _skills_check(cleaned: str, skills) -> dict:
    matched = []
    if cleaned:
        for skill in skills or []:
            if isinstance(skill, str) and skill.strip() and skill not in matched:
                if _skill_pattern(skill).search(cleaned):
                    matched.append(skill)
    return {"passed": len(matched) >= MIN_SKILLS, "matched": matched, "count": len(matched)}


def _location_check(location_name, locations) -> dict:
    posting_location = _normalize(location_name)
    if not posting_location:
        return {
            "passed": False,
            "matched": None,
            "posting_value": location_name,
            "reason": "posting location is missing or empty",
        }
    for target in locations or []:
        wanted = _normalize(target)
        if wanted and wanted.casefold() in posting_location.casefold():
            return {
                "passed": True,
                "matched": target,
                "posting_value": posting_location,
                "reason": f"location contains {target!r}",
            }
    return {
        "passed": False,
        "matched": None,
        "posting_value": posting_location,
        "reason": "no target location is contained in the location",
    }


def judge_rule(posting: dict, resume: dict) -> dict:
    location = posting.get("location")
    location_name = location.get("name") if isinstance(location, dict) else None
    cleaned = clean_content(posting.get("content"))

    # All three checks are always evaluated so every verdict cites all of its evidence.
    title = _title_check(posting.get("title"), resume.get("target_titles"))
    skills = _skills_check(cleaned, resume.get("skills"))
    loc = _location_check(location_name, resume.get("locations"))

    if not cleaned:
        skills_text = "content is missing or empty"
    elif skills["passed"]:
        skills_text = f"matched {skills['count']} skills: {', '.join(skills['matched'])}"
    else:
        found = ", ".join(skills["matched"]) or "none"
        skills_text = f"matched {skills['count']} of the required {MIN_SKILLS} skills ({found})"

    verdict = "relevant" if title["passed"] and skills["passed"] and loc["passed"] else "not_relevant"
    justification = (
        f"target_titles vs title: {'pass' if title['passed'] else 'fail'} ({title['reason']}); "
        f"skills vs content: {'pass' if skills['passed'] else 'fail'} ({skills_text}); "
        f"locations vs location.name: {'pass' if loc['passed'] else 'fail'} ({loc['reason']})"
    )

    return {
        "posting_id": posting.get("id"),
        "title": posting.get("title"),
        "source": "record",
        "verdict": verdict,
        "checks": {"title": title, "skills": skills, "location": loc},
        "resume_fields": ["target_titles", "skills", "locations"],
        "posting_fields": ["title", "content", "location.name"],
        "justification": justification,
    }


def judge_all_rule(postings, resume: dict) -> list:
    return [judge_rule(posting, resume) for posting in postings]
