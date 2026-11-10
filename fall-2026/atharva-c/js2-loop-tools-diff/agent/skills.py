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


# Skills whose names are also ordinary English words. For these, a whole-word,
# any-case match is not enough: "react to new insights" and "the go-to designer"
# are English. Instead the name must appear capitalized (React, Go), or as an
# unambiguous technical spelling in any case (ReactJS, React.js, Golang).
# "Go" is also not allowed to be followed by a hyphen, so "Go-to" does not count.
_B = r"(?<![A-Za-z0-9])"   # no letter or digit before
_E = r"(?![A-Za-z0-9])"    # no letter or digit after
AMBIGUOUS_SKILLS = {
    "react": [
        re.compile(_B + r"React" + _E),
        re.compile(_B + r"react(?:js|\.js)" + _E, re.IGNORECASE),
    ],
    "go": [
        re.compile(_B + r"Go" + r"(?![A-Za-z0-9-])"),
        re.compile(_B + r"golang" + _E, re.IGNORECASE),
    ],
}


def _found(skill: str, text: str) -> bool:
    patterns = AMBIGUOUS_SKILLS.get(skill.lower())
    if patterns is None:
        return bool(_word(skill).search(text))
    return any(p.search(text) for p in patterns)


def match_skills(text: str, skills: list[str]) -> list[str]:
    """Return the skills found in text, in the order given, without duplicates."""
    matched, seen = [], set()
    for skill in skills:
        if skill.lower() in seen:
            continue
        if _found(skill, text):
            seen.add(skill.lower())
            matched.append(skill)
    return matched
