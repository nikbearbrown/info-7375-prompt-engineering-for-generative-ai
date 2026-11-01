"""The written rule (CONTRACT.md "The rule"). Output is a record: anyone can recompute it."""
import re

_WORD = re.compile(r"[a-z0-9]+")


def words(text):
    return _WORD.findall(text.lower())


def _contains_phrase(title_words, phrase):
    target = words(phrase)
    n = len(target)
    return n > 0 and any(title_words[i:i + n] == target for i in range(len(title_words) - n + 1))


def judge_rule(posting, resume):
    title_words = words(posting.get("title", ""))
    keywords = resume["search"]["title_keywords"]
    excludes = resume["search"]["exclude_title_terms"]

    keyword_hit = next((i for i, k in enumerate(keywords) if _contains_phrase(title_words, k)), None)
    level_hit = next((j for j, t in enumerate(excludes) if _contains_phrase(title_words, t)), None)

    # No keyword hit cites the whole keyword list: that absence is what decides the verdict.
    resume_fields = [f"search.title_keywords[{keyword_hit}]" if keyword_hit is not None else "search.title_keywords"]
    if level_hit is not None:
        resume_fields.append(f"search.exclude_title_terms[{level_hit}]")

    relevant = keyword_hit is not None and level_hit is None
    if relevant:
        reason = f"title matches '{keywords[keyword_hit]}' and has no seniority term"
    elif keyword_hit is None:
        reason = "title matches no keyword in search.title_keywords"
    else:
        reason = f"title matches '{keywords[keyword_hit]}' but has seniority term '{excludes[level_hit]}'"
    if keyword_hit is None and level_hit is not None:
        reason += f" (it also has seniority term '{excludes[level_hit]}')"

    return {
        "id": posting["id"],
        "kind": "record",
        "verdict": "relevant" if relevant else "not_relevant",
        "resume_fields": resume_fields,
        "posting_fields": ["title"],
        "reason": reason,
    }
