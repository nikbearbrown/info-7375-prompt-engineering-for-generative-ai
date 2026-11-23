"""The JS3 filter, v1.0.0 - implemented against FILTER.md "The filter".

Every verdict is a RECORD: anyone can recompute it by hand from the posting.
Rules are evaluated in this order:

  3. insufficient_data (checked FIRST): content empty or missing after HTML
     is stripped -> bucket "insufficient_data". No relevance verdict is
     produced from the title alone, and the posting is in neither the
     relevant nor the rejected bucket, nor the reject audit's sampling pool.
  1. Title or content contains >= 2 of the 6 role/skill words, whole-word,
     case-insensitive (JS1 agent/rule.py, ported unchanged; see below).
  2. Title contains a sales/GTM/people-ops word -> rejected, UNLESS content
     contains an AI-systems-building phrase.

A posting is RELEVANT only if rules 1 and 2 both pass. Otherwise "rejected",
with every failing rule listed in reasons.

Matching semantics are deliberately literal (FILTER.md lists exact words):
"LLMs" does not match LLM (JS1's documented gap), "training" does not match
"train", "fine-tuning" does not match "fine-tune", "Recruiting" does not
match "Recruiter".

Ported from ~/Desktop/js1-contract-and-watch/agent/rule.py (skill_pattern,
field_text, quote windowing) rather than imported, because JS1 and JS2 both
name their package `agent` and JS3 imports JS2's.
"""
import html
import re

VERSION = "1.0.0"

ROLE_SKILLS = ["Python", "RAG", "LLM", "PyTorch", "LangChain", "vector databases"]
SKILL_THRESHOLD = 2
SALES_TITLE_WORDS = ["Sales", "Account Executive", "Solutions Architect", "Compensation", "Recruiter", "HR"]
AI_BUILDING_PHRASES = ["train", "fine-tune", "RAG pipeline", "build an agent", "LLM application"]
FIELDS = ("title", "content")
QUOTE_CONTEXT = 40
BUCKETS = ("relevant", "rejected", "insufficient_data")


def phrase_pattern(phrase):
    """Whole-word, case-insensitive; internal whitespace matches any run of
    whitespace. Same construction as JS1's skill_pattern."""
    words = [re.escape(w) for w in phrase.split()]
    return re.compile(r"(?<!\w)" + r"\s+".join(words) + r"(?!\w)", re.IGNORECASE)


_SKILL_RE = {s: phrase_pattern(s) for s in ROLE_SKILLS}
_SALES_RE = {s: phrase_pattern(s) for s in SALES_TITLE_WORDS}
_AI_RE = {s: phrase_pattern(s) for s in AI_BUILDING_PHRASES}


def field_text(posting, field):
    """Plain text of a posting field. Greenhouse content is HTML-escaped HTML,
    so unescape, drop tags, unescape again, collapse whitespace. Lever's
    descriptionPlain passes through unchanged apart from whitespace."""
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
    while start > 0 and not text[start - 1].isspace():
        start -= 1
    while end < len(text) and not text[end].isspace():
        end += 1
    return text[start:end]


def _first(patterns, text):
    for name, rx in patterns.items():
        if rx.search(text):
            return name
    return None


def classify(posting):
    texts = {f: field_text(posting, f) for f in FIELDS}
    result = {"board": posting.get("board"), "id": posting["id"], "title": posting.get("title"),
              "url": posting.get("url"), "filter_version": VERSION, "bucket": None, "reasons": [],
              "matched_skills": [], "sales_title_word": None, "ai_building_phrase": None}

    # Rule 3 first: no text, no verdict.
    if not texts["content"]:
        result["bucket"] = "insufficient_data"
        result["reasons"].append("rule 3: content empty or missing - no relevance verdict produced")
        return result

    # Rule 1.
    for skill in ROLE_SKILLS:
        for field in FIELDS:
            m = _SKILL_RE[skill].search(texts[field])
            if m:
                result["matched_skills"].append(
                    {"skill": skill, "field": field, "quote": _quote(texts[field], field, m)})
                break
    n = len(result["matched_skills"])
    if n < SKILL_THRESHOLD:
        result["reasons"].append(f"rule 1: {n} of {len(ROLE_SKILLS)} role/skill words (need >= {SKILL_THRESHOLD})")

    # Rule 2.
    result["sales_title_word"] = _first(_SALES_RE, texts["title"])
    if result["sales_title_word"]:
        result["ai_building_phrase"] = _first(_AI_RE, texts["content"])
        if not result["ai_building_phrase"]:
            result["reasons"].append(
                f"rule 2: title contains {result['sales_title_word']!r} and content has no "
                f"AI-systems-building phrase")

    result["bucket"] = "rejected" if result["reasons"] else "relevant"
    return result


def run_filter(postings):
    results = [classify(p) for p in postings]
    out = {"filter_version": VERSION, "results": results, **{b: [] for b in BUCKETS}}
    for r in results:
        out[r["bucket"]].append(r)
    return out


def reject_sampling_pool(filter_output):
    """Only genuinely rejected postings - insufficient_data is never in here,
    because a posting with no text can't be hand-judged."""
    return [r for r in filter_output["rejected"] if r["bucket"] == "rejected"]


def summary(filter_output):
    return {"total": len(filter_output["results"]), **{b: len(filter_output[b]) for b in BUCKETS}}
