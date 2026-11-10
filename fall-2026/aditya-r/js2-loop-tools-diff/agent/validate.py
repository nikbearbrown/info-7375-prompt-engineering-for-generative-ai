"""Validator for Claude's JUDGMENT (CONTRACT.md §2, revision R4).

Rejects anything that is not exactly the fixed format, and any citation that the supplied
inputs do not support. Passing says the judgment is well-formed and its evidence exists;
it does not say the judgment is correct.
"""
import json

from .rules import (
    ELIGIBLE_PHRASES,
    EXCLUDED_TERMS,
    MIN_SHARED_SKILLS,
    SKILL_FIELDS,
    TARGET_SKILLS,
    contains_phrase,
    normalize,
    posting_text_fields,
    resume_fields_with_skill,
)

TOP_KEYS = {"posting_id", "verdict", "role_phrase", "excluded_terms", "shared_skills", "explanation"}
SKILL_KEYS = {"skill", "resume_field", "posting_field", "quote"}
MAX_QUOTE = 400
MAX_EXPLANATION = 1500


def _no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate keys {sorted(k for k in set(keys) if keys.count(k) > 1)}")
    return dict(pairs)


def parse_strict(text):
    """The whole response must be one JSON object (surrounding whitespace allowed)."""
    if not isinstance(text, str):
        raise ValueError("response is not text")
    stripped = text.strip()
    if not stripped.startswith("{") or not stripped.endswith("}"):
        raise ValueError("response is not a bare JSON object (prose or code fences present)")
    return json.loads(stripped, object_pairs_hook=_no_duplicate_keys)


def validate_judgment(text, posting, resume):
    """Return (ok, errors, parsed). `posting` is the board object the request was built from."""
    try:
        data = parse_strict(text)
    except ValueError as e:  # json.JSONDecodeError is a ValueError
        return False, [f"format: {e}"], None
    errors = []

    def err(msg):
        errors.append(msg)

    if not isinstance(data, dict):
        return False, ["format: top level is not an object"], None
    if set(data) != TOP_KEYS:
        err(f"format: keys {sorted(data)} != {sorted(TOP_KEYS)}")
        return False, errors, data

    fields = posting_text_fields(posting)

    # Association: the response must be about the posting it was requested for (wrong version 1).
    pid = data["posting_id"]
    if not isinstance(pid, int) or isinstance(pid, bool):
        err("format: posting_id is not an integer")
    elif pid != posting.get("id"):
        err(f"association: posting_id {pid} does not match requested posting {posting.get('id')}")

    if data["verdict"] not in ("relevant", "not_relevant"):
        err(f"format: verdict {data['verdict']!r} not in allowed values")

    rp = data["role_phrase"]
    if not (isinstance(rp, dict) and set(rp) == {"pass", "matched"} and isinstance(rp["pass"], bool)):
        err("format: role_phrase must be {pass: bool, matched: str|null}")
        rp = None
    elif rp["pass"]:
        m = rp["matched"]
        if m not in ELIGIBLE_PHRASES:
            err(f"evidence: role_phrase.matched {m!r} is not an eligible phrase")
        elif not contains_phrase(fields["title"], m):
            err(f"evidence: role_phrase.matched {m!r} does not occur in posting.title")
    elif rp["matched"] is not None:
        err("consistency: role_phrase.matched must be null when pass is false")

    ex = data["excluded_terms"]
    if not (isinstance(ex, dict) and set(ex) == {"pass", "found"} and isinstance(ex["pass"], bool)
            and isinstance(ex["found"], list) and all(isinstance(t, str) for t in ex["found"])):
        err("format: excluded_terms must be {pass: bool, found: [str]}")
        ex = None
    else:
        for t in ex["found"]:
            if t not in EXCLUDED_TERMS:
                err(f"evidence: excluded term {t!r} is not on the exclusion list")
            elif not contains_phrase(fields["title"], t):
                err(f"evidence: excluded term {t!r} does not occur in posting.title")
        if ex["pass"] != (len(ex["found"]) == 0):
            err("consistency: excluded_terms.pass must be true exactly when found is empty")

    ss = data["shared_skills"]
    if not (isinstance(ss, dict) and set(ss) == {"pass", "skills"} and isinstance(ss["pass"], bool)
            and isinstance(ss["skills"], list)):
        err("format: shared_skills must be {pass: bool, skills: [...]}")
        ss = None
    else:
        seen = set()
        for i, s in enumerate(ss["skills"]):
            if not (isinstance(s, dict) and set(s) == SKILL_KEYS and all(isinstance(s[k], str) for k in SKILL_KEYS)):
                err(f"format: shared_skills.skills[{i}] must have string keys {sorted(SKILL_KEYS)}")
                continue
            skill = s["skill"]
            if skill not in TARGET_SKILLS:
                err(f"evidence: skills[{i}].skill {skill!r} is not a target skill")
                continue
            if skill in seen:
                err(f"consistency: skill {skill!r} listed more than once")
            seen.add(skill)
            # R4: the cited résumé field must actually contain the skill, not merely exist.
            if s["resume_field"] not in SKILL_FIELDS:
                err(f"evidence: skills[{i}].resume_field {s['resume_field']!r} is not a permitted résumé array")
            elif s["resume_field"] not in resume_fields_with_skill(resume, skill):
                err(f"evidence: {skill!r} is not in résumé field {s['resume_field']}")
            if s["posting_field"] not in ("title", "description"):
                err(f"evidence: skills[{i}].posting_field {s['posting_field']!r} must be title or description")
                continue
            quote = normalize(s["quote"])
            if not quote or len(s["quote"]) > MAX_QUOTE:
                err(f"evidence: skills[{i}].quote is empty or longer than {MAX_QUOTE} characters")
            elif not contains_phrase(fields[s["posting_field"]], quote):
                err(f"evidence: skills[{i}].quote not found in posting.{s['posting_field']} (wrong version 2)")
            elif not contains_phrase(quote, skill):
                err(f"evidence: skills[{i}].quote does not contain the skill {skill!r}")
        if ss["pass"] != (len(seen) >= MIN_SHARED_SKILLS):
            err(f"consistency: shared_skills.pass must be true exactly when ≥{MIN_SHARED_SKILLS} distinct skills are listed")

    if rp and ex and ss and data["verdict"] in ("relevant", "not_relevant"):
        all_pass = rp["pass"] and ex["pass"] and ss["pass"]
        if (data["verdict"] == "relevant") != all_pass:
            err("consistency: verdict must be relevant exactly when all three checks pass")

    expl = data["explanation"]
    if not isinstance(expl, str) or not expl.strip() or len(expl) > MAX_EXPLANATION:
        err("format: explanation must be a nonempty string")
    elif not any(w in expl.lower() for w in ("title", "description")):
        err("format: explanation must name the posting field(s) it used (title/description)")

    return (not errors), errors, data
