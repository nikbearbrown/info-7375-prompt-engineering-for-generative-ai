"""The RECORD rule from Job-Search Agent 1, copied unchanged.

Source: fall-2026/yash-s/js1-contract-and-watch/judge.py at commit 73260d2: the RECORD
constants and the functions clean_text, has_phrase, counted_skills and record_verdict.
Nothing below this docstring and the imports was edited. The JUDGMENT (Claude) half of
judge.py is deliberately not copied: the JS2 loop calls no model.
"""
import html
import re

# RECORD rule, CONTRACT.md v3 section 4
TITLE_PHRASES = ("AI Engineer", "ML Engineer", "Machine Learning Engineer",
                 "Applied AI Engineer", "Data Engineer", "GenAI Engineer")
SWE_PHRASE = "Software Engineer"
SWE_WORDS = ("AI", "ML", "GenAI", "Machine Learning")
SKILL_GROUPS = ("languages", "data_bi", "backend_automation", "database_cloud")
EXCLUDED_SKILLS = ("Databricks", "Unity Catalog")       # the company's own product names
MIN_SKILLS = 2
BLOCKER = "security clearance"


def clean_text(content):
    """Greenhouse sends entity-escaped HTML: unescape, drop tags, unescape again."""
    t = html.unescape(content or "")
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def has_phrase(phrase, text):
    """Whole word or whole phrase, ignoring capital letters."""
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text or "", re.I) is not None


def counted_skills(resume):
    """(résumé field path, skill) for every skill Rule 2 counts, each skill once."""
    excluded = {s.lower() for s in EXCLUDED_SKILLS}
    out, seen = [], set()
    for g in SKILL_GROUPS:
        for s in resume["skills"].get(g, []):
            if s.lower() not in excluded and s.lower() not in seen:
                seen.add(s.lower())
                out.append((f"skills.{g}", s))
    return out


def record_verdict(posting, resume):
    title = posting.get("title") or ""
    text = clean_text(posting.get("content"))

    phrases = [p for p in TITLE_PHRASES if has_phrase(p, title)]
    swe_words = [w for w in SWE_WORDS if has_phrase(w, title)] if has_phrase(SWE_PHRASE, title) else []
    rule1 = bool(phrases) or bool(swe_words)

    skills = counted_skills(resume)
    hits = [{"skill": s, "resume_field": f} for f, s in skills if has_phrase(s, text)]
    rule2 = len(hits) >= MIN_SKILLS

    found_in = [name for name, t in (("title", title), ("content", text)) if has_phrase(BLOCKER, t)]
    rule3 = not found_in

    verdict = "relevant" if rule1 and rule2 and rule3 else "not relevant"
    t = title.strip()
    if phrases:
        r1 = f"title {t!r} contains {', '.join(repr(p) for p in phrases)} (rule 1 passed)"
    elif swe_words:
        r1 = f"title {t!r} contains 'Software Engineer' with {', '.join(repr(w) for w in swe_words)} (rule 1 passed)"
    else:
        r1 = f"title {t!r} contains none of the rule 1 phrases (rule 1 failed)"
    if hits:
        found = ", ".join(f"{h['skill']} ({h['resume_field']})" for h in hits)
        r2 = f"content contains {len(hits)} of {len(skills)} counted résumé skills: {found}"
    else:
        r2 = f"content contains 0 of {len(skills)} counted résumé skills from {', '.join(f'skills.{g}' for g in SKILL_GROUPS)}"
    r2 += f" (rule 2 {'passed' if rule2 else 'failed'}, needs {MIN_SKILLS})"
    r3 = (f"{BLOCKER!r} not found in title or content (rule 3 passed)" if rule3
          else f"{BLOCKER!r} found in {' and '.join(found_in)} (rule 3 failed)")

    return {
        "judge": "RECORD",
        "posting_id": posting["id"],
        "verdict": verdict,
        "checks": {
            "rule1_title": {"posting_field": "title", "passed": rule1,
                            "matched_phrases": phrases, "software_engineer_with": swe_words},
            "rule2_skills": {"posting_field": "content", "passed": rule2, "needed": MIN_SKILLS,
                             "matched": hits, "excluded": list(EXCLUDED_SKILLS)},
            "rule3_blocker": {"posting_fields": ["title", "content"], "passed": rule3,
                              "phrase": BLOCKER, "found_in": found_in},
        },
        "reason": "; ".join([r1, r2, r3]),
    }


def location_name(posting):
    return ((posting.get("location") or {}).get("name") or "").strip()
