"""The written rule (CONTRACT: The rule, id title-us-v1). Produces a record, not a judgment."""
import html
import re

RULE_ID = "title-us-v1"
TITLE_PHRASES = ("product manager", "product analyst", "product strategy", "product operations", "product owner")
US_MARKERS = ("US", "USA", "United States", "Remote-US", "US-Remote", "US Remote", "San Francisco", "SF",
              "New York", "New-York", "NYC", "NY", "Seattle", "SEA", "Chicago", "Atlanta", "Boston")


def phrase_match(phrase, text):
    """Case-insensitive match not immediately preceded or followed by a letter."""
    return re.search(r"(?<![A-Za-z])" + re.escape(phrase) + r"(?![A-Za-z])", text, re.IGNORECASE) is not None


def _plain(content):
    return re.sub(r"<[^>]+>", " ", html.unescape(html.unescape(content or "")))


def _skill_values(resume):
    out = []
    for key, val in (resume.get("skills") or {}).items():
        if isinstance(val, list):
            out += [(f"skills.{key}[{i}]", v) for i, v in enumerate(val) if isinstance(v, str)]
    return out


def check_title(posting):
    title = " ".join((posting.get("title") or "").lower().split())
    if not title:
        return {"pass": False, "matched": None, "reason": "title missing"}
    for p in TITLE_PHRASES:
        if phrase_match(p, title):
            return {"pass": True, "matched": p, "reason": f'title contains "{p}"'}
    return {"pass": False, "matched": None, "reason": "title has none of the product-family phrases"}


def check_location(posting):
    offices = posting.get("offices") or []
    for i, o in enumerate(offices):
        name = (o or {}).get("name") or ""
        if name == "US" or name.startswith("US-"):
            return {"pass": True, "via": "offices", "field": f"offices[{i}].name", "value": name,
                    "reason": f'office "{name}" is US'}
    loc = ((posting.get("location") or {}).get("name") or "").strip()
    if loc and loc.upper() != "N/A":
        for m in US_MARKERS:
            if phrase_match(m, loc):
                return {"pass": True, "via": "location", "field": "location.name", "value": loc,
                        "reason": f'location.name contains US marker "{m}"'}
    return {"pass": False, "via": None, "field": None, "value": None, "reason": "location not US / unknown"}


def judge(posting, resume):
    t = check_title(posting)
    loc = check_location(posting)
    verdict = "relevant" if t["pass"] and loc["pass"] else "not_relevant"

    resume_fields = {"personal.location": resume["personal"]["location"]}
    for i, e in enumerate(resume.get("experience", [])):
        resume_fields[f"experience[{i}].title"] = e["title"]
    posting_fields = {"title": posting.get("title")}
    if loc["pass"]:
        posting_fields[loc["field"]] = loc["value"]
    else:
        if "location" in posting and isinstance(posting["location"], dict) and "name" in posting["location"]:
            posting_fields["location.name"] = posting["location"]["name"]
        for i, o in enumerate(posting.get("offices") or []):
            if isinstance(o, dict) and "name" in o:
                posting_fields[f"offices[{i}].name"] = o["name"]

    body = _plain(posting.get("content")).lower()
    skills = [v for _, v in _skill_values(resume) if body and phrase_match(v.lower(), body)]

    reason = (f"Title check {'passed' if t['pass'] else 'failed'}: {t['reason']}. "
              f"Location check {'passed' if loc['pass'] else 'failed'}: {loc['reason']}.")
    return {
        "posting_id": posting.get("id"),
        "judge": "rule",
        "kind": "record",
        "rule_id": RULE_ID,
        "verdict": verdict,
        "checks": {"title": t, "location": loc},
        "resume_fields": resume_fields,
        "posting_fields": posting_fields,
        "skills_in_content": skills,
        "reason": reason,
    }


def judge_all(postings, resume):
    return [judge(p, resume) for p in postings]
