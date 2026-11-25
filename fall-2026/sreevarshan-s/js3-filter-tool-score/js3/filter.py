"""Posting filter implementing FILTER.md v0.1.

Matching semantics (applies to every word list):
- Case-insensitive.
- A term must start at a word boundary; its end is left open. So
  "data engineer" matches "Data Engineering", while "etl" does not fire
  inside "settlement" and "vp" does not fire inside "MVP".

Decision order for each posting:
1. Hard reject on title (section 4) -> reason "hard_reject".
2. Role word in title (section 2), other than "software engineer"
   -> "title_and_topic" if topic words were also found, else "title_match".
3. "software engineer" in title -> passes only with a topic word
   ("title_and_topic"); otherwise "no_match".
4. Anything else -> "no_match".

Topic words (section 3) are searched in the description fields and lists
(Lever) and in metadata values (Greenhouse). When no description text is
present, ``description_available`` is False and topic evidence is
"insufficient" -- a missing description is never itself a reason to reject.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

ROLE_WORDS = [
    "machine learning",
    "ml engineer",
    "data engineer",
    "data scientist",
    "ml platform",
    "mlops",
    "data platform",
    "analytics engineer",
]
SOFTWARE_ENGINEER = "software engineer"

TOPIC_WORDS = [
    "python",
    "pytorch",
    "tensorflow",
    "spark",
    "sql",
    "dbt",
    "airflow",
    "kafka",
    "kubernetes",
    "ml pipeline",
    "feature store",
    "data warehouse",
    "etl",
]

HARD_REJECT_WORDS = [
    "manager",
    "director",
    "vp",
    "head of",
    "counsel",
    "legal",
    "recruiter",
    "executive",
]
PRINCIPAL = "principal"
PRINCIPAL_EXEMPT = ["engineer", "scientist"]

# Lever description-bearing fields (section 3: "description or lists").
DESCRIPTION_FIELDS = [
    "descriptionPlain",
    "description",
    "descriptionBodyPlain",
    "descriptionBody",
]


def _pattern(term: str) -> re.Pattern[str]:
    return re.compile(r"\b" + re.escape(term), re.IGNORECASE)


_PATTERNS = {
    t: _pattern(t)
    for t in ROLE_WORDS
    + [SOFTWARE_ENGINEER]
    + TOPIC_WORDS
    + HARD_REJECT_WORDS
    + [PRINCIPAL]
    + PRINCIPAL_EXEMPT
}


def _find(terms: Iterable[str], text: str) -> list[str]:
    return [t for t in terms if _PATTERNS[t].search(text)]


def _as_text(value: Any) -> str:
    """Flatten a field value of any shape into searchable text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return " ".join(_as_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(_as_text(v) for v in value.values())
    return str(value)


def _title(posting: dict) -> str:
    # Greenhouse uses "title", Lever uses "text".
    return _as_text(posting.get("title") or posting.get("text"))


def _description_text(posting: dict) -> str:
    parts = [_as_text(posting.get(f)) for f in DESCRIPTION_FIELDS]
    lists = posting.get("lists")
    if isinstance(lists, list):
        for item in lists:
            if isinstance(item, dict):
                parts.append(_as_text(item.get("text")))
                parts.append(_as_text(item.get("content")))
            else:
                parts.append(_as_text(item))
    return " ".join(p for p in parts if p).strip()


def _metadata_text(posting: dict) -> str:
    metadata = posting.get("metadata")
    if not isinstance(metadata, list):
        return ""
    values = [_as_text(m.get("value")) for m in metadata if isinstance(m, dict)]
    return " ".join(v for v in values if v).strip()


def load_postings(raw: Any) -> list[dict]:
    """Return the posting list from a raw board payload.

    Greenhouse: {"jobs": [...], "meta": {...}}. Lever: a top-level list.
    Anything else yields an empty list (a missing board, not zero matches,
    is for the caller to report).
    """
    if isinstance(raw, dict):
        jobs = raw.get("jobs")
        return [j for j in jobs if isinstance(j, dict)] if isinstance(jobs, list) else []
    if isinstance(raw, list):
        return [p for p in raw if isinstance(p, dict)]
    return []


class Filter:
    def __init__(self, postings: list[dict] | None = None):
        self.postings: list[dict] = list(postings or [])

    @classmethod
    def from_raw(cls, raw: Any) -> "Filter":
        """Build a Filter from a raw Greenhouse or Lever payload."""
        return cls(load_postings(raw))

    @staticmethod
    def evaluate(posting: dict) -> dict:
        if not isinstance(posting, dict):
            posting = {}
        title = _title(posting)
        description = _description_text(posting)
        metadata = _metadata_text(posting)
        description_available = bool(description)

        role = _find(ROLE_WORDS, title)
        software_engineer = _find([SOFTWARE_ENGINEER], title)
        topic = _find(TOPIC_WORDS, " ".join(p for p in (description, metadata) if p))

        reject = _find(HARD_REJECT_WORDS, title)
        if _find([PRINCIPAL], title) and not _find(PRINCIPAL_EXEMPT, title):
            reject.append(PRINCIPAL)

        if reject:
            passed, reason = False, "hard_reject"
        elif role:
            passed, reason = True, ("title_and_topic" if topic else "title_match")
        elif software_engineer and topic:
            passed, reason = True, "title_and_topic"
        else:
            passed, reason = False, "no_match"

        return {
            "id": posting.get("id"),
            "title": title,
            "passed": passed,
            "reason": reason,
            "matched_words": {
                "role": role + software_engineer,
                "topic": topic,
                "reject": reject,
            },
            "description_available": description_available,
            # FILTER.md section 5: absent field or word not found -> insufficient.
            "topic_evidence": "supported" if topic else "insufficient",
        }

    def run(self) -> list[dict]:
        return [self.evaluate(p) for p in self.postings]
