"""The deterministic relevance rule (CONTRACT.md §4 with revisions R1, R2).

Its output is the RECORD: anyone holding the posting JSON and the résumé JSON can
recompute it by hand.
"""
import html
import re
from html.parser import HTMLParser

ELIGIBLE_PHRASES = (
    "software engineer",
    "data engineer",
    "machine learning engineer",
    "ai engineer",
    "analytics engineer",
)
EXCLUDED_TERMS = (
    "senior", "sr", "staff", "principal", "lead", "manager",
    "director", "head", "vp", "chief", "distinguished", "architect",
)
TARGET_SKILLS = ("python", "sql", "spark", "databricks", "langgraph")
SKILL_FIELDS = (
    "skills.languages",
    "skills.data_bi",
    "skills.backend_automation",
    "skills.database_cloud",
)
MIN_SHARED_SKILLS = 2


def normalize(text):
    """§4 steps 2-4: lowercase, non-alphanumeric runs -> one space, trim."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).split())


def contains_phrase(normalized_text, normalized_phrase):
    """§4 step 5: whole-word / contiguous whole-word phrase match."""
    if not normalized_phrase:
        return False
    return f" {normalized_phrase} " in f" {normalized_text} "


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def html_to_text(raw):
    """§4 step 1. Greenhouse `content` is entity-escaped HTML (`&lt;p&gt;`), so it is
    unescaped once to recover the markup, then parsed (which decodes the remaining
    entities such as `&nbsp;`) with script/style content dropped."""
    if not raw:
        return ""
    parser = _TextExtractor()
    parser.feed(html.unescape(raw))
    parser.close()
    return " ".join(" ".join(parser.parts).split())


def posting_text_fields(posting):
    """The two posting fields the rule reads, normalized."""
    return {
        "title": normalize(posting.get("title")),
        "description": normalize(html_to_text(posting.get("content"))),
    }


def resume_skill_entries(resume):
    """{field path: [entries]} for the four permitted arrays (other fields are ignored)."""
    return {path: list(resume["skills"][path.split(".", 1)[1]]) for path in SKILL_FIELDS}


def resume_fields_with_skill(resume, skill):
    """R1: fields where `skill` matches a whole word/phrase inside a single entry."""
    return [
        path
        for path, entries in resume_skill_entries(resume).items()
        if any(contains_phrase(normalize(entry), skill) for entry in entries)
    ]


def evaluate(posting, resume):
    """Return the RECORD for one posting. Every condition is evaluated and reported."""
    fields = posting_text_fields(posting)
    title, description = fields["title"], fields["description"]
    missing = [f"posting.{name}" for name in ("title", "description") if not fields[name]]

    a_matched = [p for p in ELIGIBLE_PHRASES if contains_phrase(title, p)]
    b_found = [t for t in EXCLUDED_TERMS if contains_phrase(title, t)]

    shared, not_shared = [], {}
    for skill in TARGET_SKILLS:
        in_resume = resume_fields_with_skill(resume, skill)
        in_posting = [f"posting.{n}" for n in ("title", "description") if contains_phrase(fields[n], skill)]
        if in_resume and in_posting:
            shared.append({"skill": skill, "resume_fields": in_resume, "posting_fields": in_posting})
        elif not in_resume:
            not_shared[skill] = "absent from the four résumé skill arrays"
        else:
            not_shared[skill] = "absent from posting.title and posting.description"

    checks = {
        "A_role_phrase": {"pass": bool(a_matched), "matched": a_matched, "field": "posting.title"},
        "B_no_excluded_term": {"pass": not b_found, "found": b_found, "field": "posting.title"},
        "C_shared_skills": {
            "pass": len(shared) >= MIN_SHARED_SKILLS,
            "shared": shared,
            "not_shared": not_shared,
            "threshold": MIN_SHARED_SKILLS,
        },
    }
    relevant = not missing and all(c["pass"] for c in checks.values())
    return {
        "kind": "RECORD",
        "posting_id": posting.get("id"),
        "verdict": "relevant" if relevant else "not_relevant",
        "missing": missing,
        "checks": checks,
        "explanation": _explain(posting, checks, missing, relevant),
    }


def _explain(posting, checks, missing, relevant):
    a, b, c = checks["A_role_phrase"], checks["B_no_excluded_term"], checks["C_shared_skills"]
    parts = []
    if missing:
        parts.append(f"{' and '.join(missing)} missing or empty after normalization: insufficient evidence")
    if a["pass"]:
        parts.append(f"A pass: posting.title contains '{a['matched'][0]}'")
    else:
        parts.append(f"A fail: posting.title {posting.get('title')!r} contains none of the eligible role phrases")
    if b["pass"]:
        parts.append("B pass: no excluded term in posting.title")
    else:
        parts.append(f"B fail: posting.title contains excluded term(s) {', '.join(b['found'])}")
    cited = "; ".join(
        f"{s['skill']} [{', '.join(s['resume_fields'])} / {', '.join(s['posting_fields'])}]" for s in c["shared"]
    )
    parts.append(
        f"C {'pass' if c['pass'] else 'fail'}: {len(c['shared'])} shared target skill(s) "
        f"(need {c['threshold']}){': ' + cited if cited else ''}; searched résumé "
        f"{', '.join(SKILL_FIELDS)} and posting.title, posting.description"
    )
    return f"{'relevant' if relevant else 'not_relevant'} — " + ". ".join(parts) + "."
