"""The rule-based verdict (a RECORD: anyone can recompute it by hand).

CONTRACT.md, "The rule": a posting is relevant if, and only if, its title or
content contains at least 2 of the 6 skills below (case-insensitive,
whole-word match). Otherwise not relevant. No other conditions.
"""
import html
import re
from dataclasses import dataclass

RULE_SKILLS = ["Python", "RAG", "LLM", "PyTorch", "LangChain", "vector databases"]
THRESHOLD = 2
FIELDS = ("title", "content")
QUOTE_CONTEXT = 40  # characters of content shown on each side of a match


class JustificationError(ValueError):
    """Raised when a justification cannot name a real, verifiable match."""


@dataclass(frozen=True)
class Match:
    skill: str
    field: str  # "title" or "content"
    quote: str  # exact substring of field_text(posting, field)


def skill_pattern(skill):
    words = [re.escape(w) for w in skill.split()]
    return re.compile(r"(?<!\w)" + r"\s+".join(words) + r"(?!\w)", re.IGNORECASE)


_PATTERNS = {s: skill_pattern(s) for s in RULE_SKILLS}


def field_text(posting, field):
    """Plain text of a posting field. Greenhouse sends content as
    HTML-escaped HTML, so unescape, drop tags, and collapse whitespace."""
    raw = posting.get(field) or ""
    text = html.unescape(raw)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _quote(text, field, m):
    if field == "title":
        return text
    start = max(0, m.start() - QUOTE_CONTEXT)
    end = min(len(text), m.end() + QUOTE_CONTEXT)
    # widen to whole words so the quote doesn't start or end mid-word
    while start > 0 and not text[start - 1].isspace():
        start -= 1
    while end < len(text) and not text[end].isspace():
        end += 1
    return text[start:end]


def matched_skills(posting):
    """Each of the 6 skills found, counted once, citing the first field
    (title before content) it appears in."""
    texts = {f: field_text(posting, f) for f in FIELDS}
    matches = []
    for skill in RULE_SKILLS:
        for field in FIELDS:
            m = _PATTERNS[skill].search(texts[field])
            if m:
                matches.append(Match(skill, field, _quote(texts[field], field, m)))
                break
    return matches


def verdict(posting):
    return "relevant" if len(matched_skills(posting)) >= THRESHOLD else "not relevant"


def _resume_skills(resume):
    have = {s.lower() for s in resume.get("key_skills", [])}
    missing = [s for s in RULE_SKILLS if s.lower() not in have]
    if missing:
        raise JustificationError(f"resume.key_skills is missing rule skills: {missing}")


def _verify(posting, resume, match):
    if match.skill not in _PATTERNS:
        raise JustificationError(f"{match.skill!r} is not one of the rule's 6 skills")
    if match.skill.lower() not in {s.lower() for s in resume.get("key_skills", [])}:
        raise JustificationError(f"{match.skill!r} is not in resume.key_skills")
    if match.field not in FIELDS:
        raise JustificationError(f"unknown posting field {match.field!r}")
    if match.quote not in field_text(posting, match.field):
        raise JustificationError(
            f"quote for {match.skill!r} is not in posting.{match.field}: {match.quote!r}"
        )
    if not _PATTERNS[match.skill].search(match.quote):
        raise JustificationError(
            f"quote does not contain {match.skill!r} as a whole word: {match.quote!r}"
        )


def build_justification(posting, resume, matches):
    """Turn matches into a justification, verifying every cited term against
    the posting itself. Raises JustificationError rather than emit a claim
    it cannot back with a real matched term."""
    _resume_skills(resume)
    for m in matches:
        _verify(posting, resume, m)
    v = "relevant" if len(matches) >= THRESHOLD else "not relevant"
    head = (
        f"record (rule): {v} - {len(matches)} of {len(RULE_SKILLS)} "
        f"resume.key_skills matched in posting.title/posting.content (need >={THRESHOLD})"
    )
    if not matches:
        checked = ", ".join(f'"{s}"' for s in RULE_SKILLS)
        return (
            f"{head}. None of {checked} appears as a whole word in "
            f'posting.title "{field_text(posting, "title")}" or posting.content.'
        )
    cited = "; ".join(f'"{m.skill}" in posting.{m.field}: "{m.quote}"' for m in matches)
    return f"{head}: {cited}"


def justify(posting, resume):
    return build_justification(posting, resume, matched_skills(posting))


def evaluate(postings, resume):
    """One record per posting, in the same order as the input. Verdict and
    justification are computed per posting, never zipped from separate lists."""
    results = []
    for p in postings:
        matches = matched_skills(p)
        results.append({
            "id": p["id"],
            "title": p.get("title", ""),
            "absolute_url": p.get("absolute_url", ""),
            "kind": "record",
            "verdict": "relevant" if len(matches) >= THRESHOLD else "not relevant",
            "matched_skills": [m.skill for m in matches],
            "justification": build_justification(p, resume, matches),
        })
    return results
