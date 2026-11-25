"""The four-condition relevance rule (CONTRACT.md 'The relevance rule').

Its output is a record: every condition, the résumé fields and posting field it read,
and what matched, so anyone can recompute the verdict by hand."""

from jobwatch.normalize import contains_phrase, find_phrase, tokens

EXCERPT_RADIUS = 4


def _quoted(values):
    return ", ".join(f'"{v}"' for v in values)


def _excerpt(text_tokens, phrase):
    start = find_phrase(text_tokens, phrase)
    end = start + len(tokens(phrase))
    left, right = max(0, start - EXCERPT_RADIUS), min(len(text_tokens), end + EXCERPT_RADIUS)
    words = " ".join(text_tokens[left:right])
    return ("… " if left else "") + words + (" …" if right < len(text_tokens) else "")


def _condition(name, passed, resume_fields, posting_field, posting_value, matched, explanation):
    return {
        "condition": name,
        "passed": passed,
        "resume_fields": resume_fields,
        "posting_field": posting_field,
        "posting_value": posting_value,
        "matched": matched,
        "explanation": explanation,
    }


def _engineering_role(prefs, title, title_tokens):
    word = prefs["title_word"]
    words = [word] if contains_phrase(title_tokens, word) else []
    focus = [t for t in prefs["focus_terms"] if contains_phrase(title_tokens, t)]
    if words and focus:
        why = (f'posting.title "{title}" contains resume.preferences.title_word "{word}" '
               f"and resume.preferences.focus_terms {_quoted(focus)}.")
    else:
        gaps = []
        if not words:
            gaps.append(f'lacks resume.preferences.title_word "{word}"')
        if not focus:
            gaps.append("contains none of resume.preferences.focus_terms")
        why = f'posting.title "{title}" ' + " and ".join(gaps) + "."
    return _condition("engineering_role", bool(words and focus),
                      ["resume.preferences.title_word", "resume.preferences.focus_terms"],
                      "posting.title", title,
                      {"resume.preferences.title_word": words, "resume.preferences.focus_terms": focus}, why)


def _title_seniority(prefs, title, title_tokens):
    excluded = [w for w in prefs["excluded_title_words"] if contains_phrase(title_tokens, w)]
    if excluded:
        why = f'posting.title "{title}" contains resume.preferences.excluded_title_words {_quoted(excluded)}.'
    else:
        why = f'posting.title "{title}" contains none of resume.preferences.excluded_title_words.'
    return _condition("title_seniority", not excluded, ["resume.preferences.excluded_title_words"],
                      "posting.title", title, {"resume.preferences.excluded_title_words": excluded}, why)


def _location(prefs, location):
    places = [t for t in prefs["location_terms"] if contains_phrase(tokens(location), t)]
    if places:
        why = f'posting.location.name "{location}" contains resume.preferences.location_terms {_quoted(places)}.'
    elif not location.strip():
        why = "posting.location.name is empty, which fails the location condition."
    else:
        why = f'posting.location.name "{location}" contains none of resume.preferences.location_terms.'
    return _condition("location", bool(places), ["resume.preferences.location_terms"],
                      "posting.location.name", location, {"resume.preferences.location_terms": places}, why)


def _skills(resume, content_tokens):
    found = [s for s in resume["skills"] if contains_phrase(content_tokens, s)]
    has_python = contains_phrase(content_tokens, "python")
    others = [s for s in found if tokens(s) != ["python"]]
    if has_python and others:
        why = f"posting.content contains python and resume.skills {_quoted(others)}."
    elif has_python:
        why = "posting.content contains python but no other item from resume.skills."
    else:
        why = "posting.content does not contain python as a whole word."
    excerpts = {s: _excerpt(content_tokens, s) for s in found}
    return _condition("skills", bool(has_python and others), ["resume.skills"],
                      "posting.content", excerpts, {"resume.skills": found}, why)


def rule_verdict(resume, posting):
    prefs = resume["preferences"]
    title_tokens = tokens(posting.title)
    conditions = [
        _engineering_role(prefs, posting.title, title_tokens),
        _title_seniority(prefs, posting.title, title_tokens),
        _location(prefs, posting.location_name),
        _skills(resume, tokens(posting.content)),
    ]
    failed = [c["condition"] for c in conditions if not c["passed"]]
    verdict = "not_relevant" if failed else "relevant"
    headline = ("relevant: all four conditions passed." if not failed
                else f"not_relevant: failed {', '.join(failed)}.")
    return {
        "kind": "record",
        "posting_id": posting.id,
        "verdict": verdict,
        "failed_conditions": failed,
        "conditions": conditions,
        "justification": " ".join([headline] + [c["explanation"] for c in conditions]),
    }
