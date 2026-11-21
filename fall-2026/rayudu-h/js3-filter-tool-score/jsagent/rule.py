"""The written rule from CONTRACT.md. Its verdict is a RECORD: anyone can recompute it.

Relevant if and only if all three hold:
  1. title contains "AI" or "Engineer" (words of experience[].title minus "Co-op"),
     and "Engineering" also counts;
  2. content names at least one skill (not familiar_with_not_shipped);
  3. title does not contain "Manager", "Director" or "Head".
Whole words, ignoring case. A missing/empty title or content -> cannot judge.
location.name is shown but never decides.
"""
from __future__ import annotations

import html
import re

from . import resume as resume_mod

RELEVANT = "relevant"
NOT_RELEVANT = "not relevant"
CANNOT_JUDGE = "cannot judge"
VERDICTS = (RELEVANT, NOT_RELEVANT, CANNOT_JUDGE)

IGNORED_TITLE_WORDS = {"co-op"}
TITLE_ALIASES = {"engineer": ["Engineering"]}
MANAGEMENT_WORDS = ["Manager", "Director", "Head"]


def plain_text(content: str) -> str:
    """Greenhouse `content` is HTML that is itself HTML-escaped. Return plain text."""
    text = html.unescape(content or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _word_pattern(term: str) -> re.Pattern:
    parts = [re.escape(p) for p in term.split()]
    return re.compile(r"(?<![A-Za-z0-9])" + r"\s+".join(parts) + r"(?![A-Za-z0-9])", re.IGNORECASE)


def find_words(text: str, terms) -> list:
    """Terms that occur in text as whole words, ignoring case, in the given order."""
    return [t for t in terms if _word_pattern(t).search(text or "")]


def title_terms(resume: dict) -> list:
    terms = []
    for title in resume_mod.experience_titles(resume):
        for word in title.split():
            if word.lower() in IGNORED_TITLE_WORDS:
                continue
            if word not in terms:
                terms.append(word)
            for alias in TITLE_ALIASES.get(word.lower(), []):
                if alias not in terms:
                    terms.append(alias)
    return terms


def judge(posting: dict, resume: dict) -> dict:
    """Return {key, id, title, location, verdict, justification, tests} for one normalized posting.

    JS2: postings come from providers.py as {key, system, board, id, title, location, text, url};
    `text` is the plain-text description (Greenhouse `content` / Ashby `descriptionPlain`).
    """
    title = (posting.get("title") or "").strip()
    location = (posting.get("location") or "").strip()
    content = (posting.get("text") or "").strip()
    out = {"key": posting.get("key"), "id": posting.get("id"), "title": title, "location": location}

    missing = [f for f, v in (("title", title), ("content", content)) if not v]
    if missing:
        out["verdict"] = CANNOT_JUDGE
        out["tests"] = {}
        out["justification"] = f"missing field: {', '.join(missing)}; location: {location or '(none)'} (not used)"
        return out

    title_hits = find_words(title, title_terms(resume))
    skill_hits = find_words(content, resume_mod.skills(resume))
    mgmt_hits = find_words(title, MANAGEMENT_WORDS)
    tests = {"title": bool(title_hits), "skills": bool(skill_hits), "not_management": not mgmt_hits}
    out["tests"] = tests

    parts = []
    if title_hits:
        parts.append(f'title "{title}" matched experience[].title word(s) ' + ", ".join(f'"{w}"' for w in title_hits))
    else:
        parts.append(f'title "{title}" matched no experience[].title word')
    if skill_hits:
        parts.append("content matched skills: " + ", ".join(skill_hits))
    else:
        parts.append("content matched no skill")
    if mgmt_hits:
        parts.append("title contains management word(s): " + ", ".join(f'"{w}"' for w in mgmt_hits))
    else:
        parts.append("title has no management word")
    parts.append(f"location: {location or '(none)'} (not used)")

    failed = [name for name, ok in (("title test", tests["title"]), ("skills test", tests["skills"]),
                                    ("management test", tests["not_management"])) if not ok]
    out["verdict"] = RELEVANT if not failed else NOT_RELEVANT
    if failed:
        parts.append("failed: " + ", ".join(failed))
    out["justification"] = "; ".join(parts)
    return out
