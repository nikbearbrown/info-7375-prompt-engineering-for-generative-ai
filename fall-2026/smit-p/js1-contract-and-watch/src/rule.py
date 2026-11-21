"""rule.py — the written relevance rule from CONTRACT.md, and the justification validator.

A verdict is a dict:
    {"posting_id": int, "verdict": "relevant" | "not_relevant", "source": "rule",
     "citations": [{"resume_field", "resume_value", "posting_field", "posting_text", "effect"}]}

Every citation pairs a résumé field path with the posting field and the exact posting
text it matched (or the text that failed a check). `validate_verdict` re-finds each one.
"""
import html
import re

SENIORITY_WORDS = ("senior", "sr", "staff", "principal", "manager")
MIN_SKILLS = 2
EXCLUDED_SKILL_GROUPS = {"familiar_with_not_shipped"}


# ---------------------------------------------------------------- text helpers
def plain_text(raw):
    """Greenhouse `content` is HTML that is itself entity-escaped. Decode, strip tags."""
    text = html.unescape(html.unescape(raw or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_whole(term, text):
    """Case-insensitive match of `term` not preceded/followed by a letter or digit.
    Returns the matched span text as it appears in `text`, or None."""
    m = re.search(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", text, re.I)
    return m.group(0) if m else None


# ---------------------------------------------------------------- résumé fields
def role_keywords(resume):
    """[(field_path, keyword)] — experience titles with the parenthesised part removed."""
    out, seen = [], set()
    for i, job in enumerate(resume.get("experience", [])):
        kw = re.sub(r"\s*\([^)]*\)", "", job.get("title", "")).strip()
        if kw and kw.lower() not in seen:
            seen.add(kw.lower())
            out.append((f"experience[{i}].title", kw))
    return out


def resume_skills(resume):
    """[(field_path, skill)] — every string in every list under `skills`, except the
    groups in EXCLUDED_SKILL_GROUPS. Duplicates (case-insensitive) count once."""
    out, seen = [], set()
    for group, values in resume.get("skills", {}).items():
        if group in EXCLUDED_SKILL_GROUPS or not isinstance(values, list):
            continue
        for i, skill in enumerate(values):
            if isinstance(skill, str) and skill.lower() not in seen:
                seen.add(skill.lower())
                out.append((f"skills.{group}[{i}]", skill))
    return out


def resume_value(resume, path):
    """Resolve a path like `skills.languages[1]` or `experience[0].title`; None if absent."""
    cur = resume
    for part in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        try:
            cur = cur[int(part[1:-1])] if part.startswith("[") else cur[part]
        except (KeyError, IndexError, TypeError, ValueError):
            return None
    return cur


# ---------------------------------------------------------------- the rule
def judge(posting, resume):
    title = posting.get("title", "")
    content = plain_text(posting.get("content", ""))
    cites = []

    # 1. title check
    title_hit = None
    for path, kw in role_keywords(resume):
        hit = find_whole(kw, title)
        if hit:
            title_hit = (path, kw, hit)
            break
    if title_hit:
        cites.append({"resume_field": title_hit[0], "resume_value": title_hit[1],
                      "posting_field": "title", "posting_text": title_hit[2], "effect": "title check passed"})

    # 2. seniority check
    senior_hit = None
    for word in SENIORITY_WORDS:
        hit = find_whole(word, title)
        if hit:
            senior_hit = hit
            break

    # 3. skill check — title first, then content; each skill counted once
    skill_hits = []
    for path, skill in resume_skills(resume):
        for field, text in (("title", title), ("content", content)):
            hit = find_whole(skill, text)
            if hit:
                skill_hits.append((path, skill, field, hit))
                break
    for path, skill, field, hit in skill_hits:
        cites.append({"resume_field": path, "resume_value": skill,
                      "posting_field": field, "posting_text": hit, "effect": "skill found"})

    if not title_hit:
        failed = "title check: no résumé role keyword in posting title"
        kws = role_keywords(resume)
        cites.insert(0, {"resume_field": kws[0][0] if kws else "experience",
                         "resume_value": kws[0][1] if kws else "",
                         "posting_field": "title", "posting_text": title,
                         "effect": "title check FAILED — keyword absent from this title"})
    elif senior_hit:
        failed = f"seniority check: title contains «{senior_hit}»"
        cites.insert(1, {"resume_field": title_hit[0], "resume_value": title_hit[1],
                         "posting_field": "title", "posting_text": senior_hit,
                         "effect": "seniority check FAILED — excluded word in title"})
    elif len(skill_hits) < MIN_SKILLS:
        failed = f"skill check: {len(skill_hits)} distinct résumé skill(s) found, need {MIN_SKILLS}"
    else:
        failed = None

    return {
        "posting_id": posting["id"],
        "posting_title": title,
        "verdict": "not_relevant" if failed else "relevant",
        "source": "rule",
        "label": "RECORD (rule, recomputable)",
        "failed_check": failed,
        "skills_matched": len(skill_hits),
        "citations": cites,
    }


# ---------------------------------------------------------------- validator
class JustificationError(ValueError):
    pass


def validate_verdict(verdict, posting, resume):
    """Reject a verdict that cites nothing, or cites something that is not there.
    `posting` must be the posting whose id the verdict claims (wrong version 1 fails here)."""
    if verdict.get("verdict") not in ("relevant", "not_relevant"):
        raise JustificationError(f"verdict must be relevant|not_relevant, got {verdict.get('verdict')!r}")
    if verdict.get("posting_id") != posting.get("id"):
        raise JustificationError(f"verdict is for posting {verdict.get('posting_id')}, checked against {posting.get('id')}")
    if "posting_title" in verdict and verdict["posting_title"] != posting.get("title", ""):
        raise JustificationError(f"posting {posting.get('id')}: verdict was made for «{verdict['posting_title']}», not «{posting.get('title', '')}»")
    cites = verdict.get("citations") or []
    if not cites:
        raise JustificationError(f"posting {posting.get('id')}: justification cites nothing")
    fields = {"title": posting.get("title", ""), "content": plain_text(posting.get("content", ""))}
    has_resume = has_posting = False
    for c in cites:
        rf, pf, pt = c.get("resume_field"), c.get("posting_field"), c.get("posting_text")
        if rf:
            if resume_value(resume, rf) is None:
                raise JustificationError(f"posting {posting.get('id')}: résumé field {rf!r} does not exist")
            has_resume = True
        if pf:
            if pf not in fields:
                raise JustificationError(f"posting {posting.get('id')}: unknown posting field {pf!r}")
            if not pt or find_whole(pt, fields[pf]) is None:
                raise JustificationError(f"posting {posting.get('id')}: cited text {pt!r} not found in {pf}")
            has_posting = True
    if not (has_resume and has_posting):
        raise JustificationError(f"posting {posting.get('id')}: needs at least one résumé field AND one posting field")
    return True
