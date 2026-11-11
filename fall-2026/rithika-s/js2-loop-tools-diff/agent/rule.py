"""The relevance rule from CONTRACT.md, recomputable by hand.

A verdict is a dict:
    posting_id      int
    verdict         "relevant" | "not_relevant"
    failed_condition  None, or 1/2/3 (the first condition that failed)
    citations       [{"field", "term", "posting_fields", "matched"}]
    justification   [str], one line per citation, plus a summary line

Each citation names a résumé/target field path and the posting fields it was
checked against, e.g. "skills.languages: Python matched in posting.content".
"""

import html
import re

from agent.resume import counted_skills

RELEVANT = "relevant"
NOT_RELEVANT = "not_relevant"
CONDITION_NAMES = {1: "no exclusion", 2: "title gate", 3: "skill evidence"}
MIN_SKILLS = 2

_TAG = re.compile(r"<[^>]*>")
_SPACE = re.compile(r"\s+")


def prepare(text):
    """Unescape entities, remove tags, lowercase, collapse whitespace.

    Greenhouse escapes the whole HTML body, so entities are unescaped once to
    reveal the tags and once more for entities that sat inside the HTML
    (e.g. "&amp;nbsp;" -> "&nbsp;" -> non-breaking space).
    """
    text = html.unescape(text or "")
    text = _TAG.sub(" ", text)
    text = html.unescape(text)
    return _SPACE.sub(" ", text).strip().lower()


def _term_pattern(term):
    words = [re.escape(w) for w in term.lower().split()]
    return re.compile(r"(?<![a-z0-9])" + r"\s+".join(words) + r"(?![a-z0-9])")


def contains(prepared_text, term):
    """Whole-word, case-insensitive match on already-prepared text."""
    return _term_pattern(term).search(prepared_text) is not None


def prepared_fields(posting):
    return {
        "posting.title": prepare(posting.get("title", "")),
        "posting.content": prepare(posting.get("content", "")),
    }


def _cite(field, term, posting_fields, matched):
    return {"field": field, "term": term,
            "posting_fields": list(posting_fields), "matched": matched}


def render(citation):
    state = "matched" if citation["matched"] else "not matched"
    return (f"{citation['field']}: {citation['term']} {state} in "
            f"{', '.join(citation['posting_fields'])}")


def _verdict(posting_id, verdict, failed, citations, summary):
    return {
        "posting_id": posting_id,
        "verdict": verdict,
        "failed_condition": failed,
        "citations": citations,
        "justification": [render(c) for c in citations] + [summary],
    }


def evaluate(posting, resume, target):
    """Apply conditions 1, 2, 3 in order and return one verdict."""
    pid = posting["id"]
    fields = prepared_fields(posting)
    title, content = fields["posting.title"], fields["posting.content"]

    # 1. No exclusion, in title or content.
    exclusion_cites = []
    for term in target["excluded_terms"]:
        hits = [name for name, text in fields.items() if contains(text, term)]
        if hits:
            exclusion_cites.append(
                _cite("target.excluded_terms", term, hits, True))
    if exclusion_cites:
        return _verdict(pid, NOT_RELEVANT, 1, exclusion_cites,
                        "condition 1 (no exclusion) failed: excluded term "
                        "matched")
    pass_cites = [_cite("target.excluded_terms", term,
                        ["posting.title", "posting.content"], False)
                  for term in target["excluded_terms"]]

    # 2. Title gate.
    keywords = target["target_title_keywords"]
    title_hits = [k for k in keywords if contains(title, k)]
    if not title_hits:
        cites = [_cite("target.target_title_keywords", k, ["posting.title"],
                       False) for k in keywords]
        return _verdict(pid, NOT_RELEVANT, 2, cites,
                        "condition 2 (title gate) failed: no target title "
                        "keyword matched in posting.title")
    pass_cites += [_cite("target.target_title_keywords", k, ["posting.title"],
                         True) for k in title_hits]

    # 3. Skill evidence: distinct counted skills in content.
    matched, unmatched, seen = [], [], set()
    for field, skill in counted_skills(resume):
        if skill.lower() in seen:
            continue
        seen.add(skill.lower())
        if contains(content, skill):
            matched.append(_cite(field, skill, ["posting.content"], True))
        else:
            unmatched.append(_cite(field, skill, ["posting.content"], False))
    if len(matched) < MIN_SKILLS:
        return _verdict(pid, NOT_RELEVANT, 3, matched + unmatched,
                        f"condition 3 (skill evidence) failed: {len(matched)} "
                        f"distinct counted skill(s) matched in "
                        f"posting.content; {MIN_SKILLS} required")
    return _verdict(pid, RELEVANT, None, pass_cites + matched,
                    f"all conditions hold: {len(matched)} distinct counted "
                    f"skills matched in posting.content")


def evaluate_all(postings, resume, target):
    return [evaluate(p, resume, target) for p in postings]
