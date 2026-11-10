"""Skill matcher, ported unchanged from JS1 (js1-contract-and-watch/agent/rule.py:
_word() and the matching loop in check_skills()).

Known defect carried over on purpose (JS1 README, "Skill matching counts ordinary
English words"): whole-word matching still counts "react to new insights" as the
skill React and "go-to designer" as the skill Go. This is the defect the JS2
review packet fixes; see REVIEW_PACKET.md.
"""

import html
import re


def _word(token, any_case=True):
    flags = re.IGNORECASE if any_case else 0
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(token) + r"(?![A-Za-z0-9])", flags)


def lever_text(posting: dict) -> str:
    """Plain text of a Lever posting: title, description, lists, additional."""
    parts = [posting.get("text") or "", posting.get("descriptionPlain") or ""]
    for lst in posting.get("lists") or []:
        parts.append(lst.get("text") or "")
        parts.append(re.sub(r"<[^>]+>", " ", html.unescape(lst.get("content") or "")))
    parts.append(posting.get("additionalPlain") or "")
    return " ".join(parts)


def match_skills(text: str, skills: list[str]) -> list[str]:
    """Return the skills found in text, in the order given, without duplicates."""
    matched, seen = [], set()
    for skill in skills:
        if skill.lower() in seen:
            continue
        if _word(skill).search(text):
            seen.add(skill.lower())
            matched.append(skill)
    return matched
