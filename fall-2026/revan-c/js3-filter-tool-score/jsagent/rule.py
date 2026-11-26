"""The written rule: five conditions, all must pass (CONTRACT.md, The rule)."""
from .text import contains_sequence, find_original, normalize, strip_html

COUNTED_SKILL_CATEGORIES = ("languages", "backend_automation", "database_cloud", "devops_cicd")
SENIORITY_WORDS = ("senior", "sr", "principal", "staff", "lead", "director", "manager")
ROLE_TYPE_WORDS = ("frontend", "front end", "mobile", "ios", "android")
MIN_SKILLS = 2


def _entry(condition, passed, resume_field, resume_value, posting_field, posting_value):
    return {
        "condition": condition,
        "passed": passed,
        "resume_field": resume_field,
        "resume_value": resume_value,
        "posting_field": posting_field,
        "posting_value": posting_value,
    }


def _title(resume, title):
    # Condition 1 is a plain lowercase substring test, as the contract words it.
    matched = [t for t in resume["target_titles"] if t.lower() in title.lower()]
    return _entry("title", bool(matched), "target_titles",
                  matched[0] if matched else resume["target_titles"], "title", title)


def _location(resume, location):
    city = resume["personal"]["location"].split(",")[0]
    loc = normalize(location)
    passed = contains_sequence(loc, normalize(city)) or contains_sequence(loc, "remote")
    return _entry("location", passed, "personal.location", resume["personal"]["location"],
                  "location.name", location)


def _skills(resume, content_text):
    content = normalize(content_text)
    paths, matched, quoted, seen = [], [], [], set()
    for category in COUNTED_SKILL_CATEGORIES:
        for skill in resume["skills"][category]:
            key = normalize(skill)
            if key in seen or not contains_sequence(content, key):
                continue
            seen.add(key)
            paths.append(f"skills.{category}")
            matched.append(skill)
            quoted.append(find_original(content_text, skill) or skill)
    # Parallel lists: resume_field[i], resume_value[i], posting_value[i] describe one matched skill.
    return _entry("skills", len(matched) >= MIN_SKILLS, paths, matched, "content", quoted)


def _excluded_words(condition, words, title, resume_field, resume_value):
    norm_title = normalize(title)
    hits = [w for w in words if contains_sequence(norm_title, normalize(w))]
    # On failure, quote the offending words as they appear in the title; on a pass, the title.
    posting_value = [find_original(title, w) or w for w in hits] if hits else title
    return _entry(condition, not hits, resume_field, resume_value, "title", posting_value)


def judge_posting(resume, posting):
    title = posting["title"]
    content_text = strip_html(posting["content"])
    entries = [
        _title(resume, title),
        _location(resume, posting["location"]["name"]),
        _skills(resume, content_text),
        _excluded_words("seniority", SENIORITY_WORDS, title,
                        "years_experience", resume["years_experience"]),
        _excluded_words("role_type", ROLE_TYPE_WORDS, title,
                        "target_role.excluded", resume["target_role"]["excluded"]),
    ]
    verdict = "relevant" if all(e["passed"] for e in entries) else "not_relevant"
    return {"rule_verdict": verdict, "rule_justification": entries}


def judge_postings(resume, postings):
    """Verdicts keyed by posting id, never by position."""
    return {posting["id"]: judge_posting(resume, posting) for posting in postings}
