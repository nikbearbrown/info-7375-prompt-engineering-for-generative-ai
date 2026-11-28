"""The student's FILTER.md v0.1 as code.

Every word list and number below is copied from FILTER.md; tests/test_filter_doc.py fails if
one of them no longer appears there. Where FILTER.md is silent, the choice is Claude Code's
and is marked "Claude Code's reading" (README, "Claude Code's readings of FILTER.md").

Origins of the numbers (Chapter 9): ROLE_POINTS, TITLE_TOPIC_POINTS, DESCRIPTION_TOPIC_POINTS
and CUTOFF are hand-set by the student ("I set the weights and cutoff by hand for v0.1"). The
tokenizer is inherited from JS1 (jobwatch/normalize.py)."""

from dataclasses import dataclass

from jobwatch import experience, location
from jobwatch.normalize import contains_phrase, tokens

FILTER_VERSION = "v0.1"

ROLE_WORDS = ("engineer", "developer")
LEVEL_WORDS = ("senior", "sr", "staff", "principal", "lead", "manager", "director", "head",
               "intern", "internship")
TITLE_TOPICS = ("machine learning", "ml", "ai", "inference", "model serving", "data engineer",
                "data platform", "data infrastructure")
DESCRIPTION_TOPICS = ("machine learning", "model inference", "model serving", "ml infrastructure",
                      "data pipeline", "data pipelines", "data platform")

ROLE_POINTS = 1
TITLE_TOPIC_POINTS = 2
DESCRIPTION_TOPIC_POINTS = 1
CUTOFF = 2

# v0.2's one change (FILTER.md, "After the reject audit"): "Reject when the description sets a
# minimum of 3+ years that is not marked preferred." None here is v0.1 (no experience rule);
# variants/v0.2-experience-minimum.json sets 3. jobwatch/experience.py reads the description.
EXPERIENCE_MINIMUM_YEARS = None


@dataclass(frozen=True)
class Item:
    """One posting as FILTER.md reads it ('The expected sources')."""
    board: str          # "greenhouse/anthropic", "greenhouse/databricks", "ashby/linear"
    key: str            # Greenhouse id as text, or Ashby jobUrl
    title: str
    location: str       # Greenhouse location.name, Ashby location
    description: str    # Greenhouse content, Ashby descriptionHtml (HTML)
    captured_at: str    # the time of the request that fetched the board


def _matches(text_tokens, phrases):
    """Whole words or consecutive word sequences; each phrase counts once."""
    return [p for p in phrases if contains_phrase(text_tokens, p)]


def _role(title_tokens):
    return _matches(title_tokens, ROLE_WORDS)


def _level(title_tokens):
    return _matches(title_tokens, LEVEL_WORDS)


def _title_topic(title_tokens):
    return _matches(title_tokens, TITLE_TOPICS)


def _description_topic(description_tokens):
    return _matches(description_tokens, DESCRIPTION_TOPICS)


def _award(hits, points):
    """Claude Code's reading of "Add 2 points for ... or data infrastructure": one award for any match."""
    return points if hits else 0


def _description_points(description_hits, title_topic_points):
    """"If the title earns no topic points, add 1 point for ..."."""
    return DESCRIPTION_TOPIC_POINTS if description_hits and title_topic_points == 0 else 0


def _experience_rejects(minimum_years):
    return (EXPERIENCE_MINIMUM_YEARS is not None and minimum_years is not None
            and minimum_years >= EXPERIENCE_MINIMUM_YEARS)


def score(item):
    title_tokens = tokens(item.title)
    description_tokens = tokens(item.description)
    role, level = _role(title_tokens), _level(title_tokens)
    title_hits, description_hits = _title_topic(title_tokens), _description_topic(description_tokens)

    parts = {"role": _award(role, ROLE_POINTS), "title_topic": _award(title_hits, TITLE_TOPIC_POINTS)}
    parts["description_topic"] = _description_points(description_hits, parts["title_topic"])
    total = sum(parts.values())
    where = location.classify(item.location)

    reasons, review_reasons = [], []
    if not role:
        reasons.append("role")
    if level:
        reasons.append("level")
    read = None
    if EXPERIENCE_MINIMUM_YEARS is not None:
        read = experience.read(item.description)
        if _experience_rejects(read["minimum_years"]):
            reasons.append("experience")
    description_blank = not description_tokens
    if total < CUTOFF:
        if description_blank and parts["title_topic"] == 0:
            # "leave any unresolved topic decision open for review"
            review_reasons.append("description blank")
        else:
            reasons.append("score")
    if where["outcome"] == "outside":
        reasons.append("location")
    elif where["outcome"] == "unresolved":
        review_reasons.append("location unresolved")

    fate = "rejected" if reasons else ("review" if review_reasons else "kept")
    record = {
        "board": item.board,
        "key": item.key,
        "title": item.title,
        "captured_at": item.captured_at,
        "filter_version": FILTER_VERSION,
        "score": total,
        "parts": parts,
        "matched": {"role": role, "level": level, "title_topic": title_hits,
                    "description_topic": description_hits},
        "description_blank": description_blank,
        "location": where,
        "fate": fate,
        "reasons": reasons,
        "review_reasons": review_reasons,
    }
    if read is not None:
        record["experience"] = {"threshold": EXPERIENCE_MINIMUM_YEARS, **read}
    return record


def rank(records):
    """Kept and review records only: descending score, then board identifier, then posting key.
    Claude Code's reading: board and key compare as text."""
    eligible = [r for r in records if r["fate"] in ("kept", "review")]
    return sorted(eligible, key=lambda r: (-r["score"], r["board"], r["key"]))
