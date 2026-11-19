"""FILTER.md v1: JS2's rule (F1-F6, exactly as agent/rule.py runs it) plus F7 and F8.

Plain functions, no I/O. Nothing in rule.py is copied: C1, C2 and C3 pass or
fail as rule.judge says, with the terms it matched, and F1's cleanup is
rule.posting_field. This module adds only what FILTER.md v1 adds:

- F7, missing fields: a field is missing when it is absent, null (or not
  text: rule.posting_field reads it as None), or empty after F1's cleanup.
  A text that is only whitespace after cleanup is empty (FILTER.md v1.1).
- the score (F5) and the verdict under F7;
- closest calls (FILTER.md §1);
- F8, the ranking.

A posting with no missing field gets rule.py's verdict, by construction;
tools/filter_run.py checks that on every posting it judges.

Options (candidate changes for FILTER v2, measured by tools/measure.py, not
rules yet). judge(posting, persona) with no options, or with the defaults,
is exactly v1, record included:

- skills_needed (default 2): C3 passes when the score is at least this. With
  0, C3 passes whenever the text is present; a missing text is still missing.
- seniority_words (default none) and max_years (default none): a fourth
  condition, C4 (level). It fails when the cleaned title holds one of the
  words as a whole word, or when the cleaned text states a minimum number of
  years above max_years (YEARS, below). With either one set, the record
  gains C4, C4_reason and years_matched, and a failed C4 makes the verdict
  not_relevant like any failed condition.

closest_call stays FILTER.md §1's v1 flag under every option (decision
2026-11-19): C1 and C2 as the gates, the threshold 2, and C4 not read.
"""

import re

from . import rule

PASS, FAIL, MISSING = "pass", "fail", "missing"
RELEVANT, NOT_RELEVANT, CANNOT_TELL = "relevant", "not_relevant", "cannot_tell"
CONDITIONS = ("C1", "C2", "C3")
# (condition, F7's name for the field, rule.py's name for it)
FIELDS = (("C1", "title", "title"), ("C2", "location", "location.name"), ("C3", "text", "content"))
THRESHOLD = rule.SKILLS_NEEDED  # F6: a score of 2 or more

# FILTER.md §5's seniority words, the list the level option is measured with.
SENIORITY_WORDS = ("Senior", "Staff", "Lead", "Group", "Principal", "Director", "Head of")
DEFAULT_OPTIONS = {"skills_needed": THRESHOLD, "seniority_words": None, "max_years": None}
# FILTER.md v2: F6 (v2), the skills threshold is 0, so C3 only asks that the text exist; F9, level by
# title (the seniority words); F10, level by text (a stated minimum above 3 years). v1 stays the default.
V2_OPTIONS = {"skills_needed": 0, "seniority_words": SENIORITY_WORDS, "max_years": 3}

# The years pattern (option max_years). A stated minimum is a number of one or two digits, then
# optionally "+" or a range to a second number (hyphen, en dash, em dash or "to", spaces allowed,
# and a "+" after the second number), then "year" or "years". The minimum is the first number.
# Case-insensitive. Matched: "5+ years", "5 years", "5-8 years", "5–8 years", "5—8 years",
# "5 to 8 years", "6–10+ years", "1 year". Not matched: a number in words ("five years"),
# "5 or more years", "5yrs" and "5 yrs", "5-year" (as in "a 5-year plan"), a number inside a longer
# number or a decimal ("100 years", "2.5 years"), and "years: 5". The pattern does not read the
# sentence around a match, so company history such as "over the past 10 years" matches "10 years"
# and, with max_years 3, fails C4: a known false positive.
YEARS = re.compile(r"(?<![\d.])\b(\d{1,2})(?:\s*\+|\s*(?:-|–|—|to)\s*\d{1,2}\s*\+?)?\s*years?\b", re.IGNORECASE)


def cleaned_fields(posting):
    """{"title", "location", "text"}: F1's cleaned value, or None when F7 calls the field missing."""
    fields = {}
    for _, name, rule_name in FIELDS:
        value = rule.posting_field(posting, rule_name)
        fields[name] = value if value is not None and value.strip() else None
    return fields


def verdict_of(statuses):
    """F7: not_relevant if any present condition fails; else cannot_tell if any is missing; else relevant.

    statuses holds C1-C3, and C4 when a level option is set.
    """
    values = list(statuses.values())
    if FAIL in values:
        return NOT_RELEVANT
    if MISSING in values:
        return CANNOT_TELL
    return RELEVANT


def is_closest_call(statuses, score):
    """FILTER.md §1: one step from flipping. Never when a condition is missing."""
    if MISSING in (statuses[condition] for condition in CONDITIONS):
        return False
    gates = (statuses["C1"], statuses["C2"])
    if gates == (PASS, PASS):
        return score in (1, 2)  # one skill short of the threshold, or exactly on it
    return score >= THRESHOLD and sorted(gates) == [FAIL, PASS]  # exactly one gate fails, the other passes


def resolve_options(options):
    """The defaults updated with options. Anything unknown or malformed is a ValueError."""
    merged = dict(DEFAULT_OPTIONS)
    if options:
        unknown = sorted(set(options) - set(DEFAULT_OPTIONS))
        if unknown:
            raise ValueError(f"unknown filter options: {', '.join(unknown)}")
        merged.update(options)
    needed = merged["skills_needed"]
    if isinstance(needed, bool) or not isinstance(needed, int) or needed < 0:
        raise ValueError("skills_needed must be a whole number, 0 or more")
    words = merged["seniority_words"]
    if words is not None and (isinstance(words, str) or not all(isinstance(w, str) and w.strip() for w in words)):
        raise ValueError("seniority_words must be a list of non-empty strings")
    years = merged["max_years"]
    if years is not None and (isinstance(years, bool) or not isinstance(years, int) or years < 0):
        raise ValueError("max_years must be a whole number, 0 or more")
    return merged


def _whole_word(word):
    """A whole word or phrase, case-insensitive; the space in "Head of" matches any whitespace run."""
    return re.compile(r"\b" + r"\s+".join(re.escape(part) for part in word.split()) + r"\b", re.IGNORECASE)


def level(fields, seniority_words, max_years):
    """C4 (level): (status, reasons, years_matched).

    Fails on a seniority word in the title, or on a stated minimum above
    max_years in the text (the first such span is the reason). Missing when
    a check could not run because its field is missing and nothing failed;
    the condition reading that field (C1 or C3) is then missing too.
    """
    reasons, unchecked, years_matched = [], False, []
    if seniority_words:
        if fields["title"] is None:
            unchecked = True
        else:
            for word in seniority_words:
                match = _whole_word(word).search(fields["title"])
                if match:
                    reasons.append(f'title has "{match.group(0)}"')
    if max_years is not None:
        if fields["text"] is None:
            unchecked = True
        else:
            matches = list(YEARS.finditer(fields["text"]))
            years_matched = [match.group(0) for match in matches]
            failing = next((match for match in matches if int(match.group(1)) > max_years), None)
            if failing:
                reasons.append(f'text states "{failing.group(0)}", a minimum above {max_years} years')
    status = FAIL if reasons else MISSING if unchecked else PASS
    return status, reasons, years_matched


def judge(posting, persona, options=None):
    """One posting under F1-F8, and the options. Returns its record; the caller adds "board_key" before rank().

    The record holds the cleaned title and location but never the text.
    title_match, location_match and skills_found are the résumé terms rule.py
    matched, in persona order; score is None when the text is missing.
    """
    settings = resolve_options(options)
    _, justification = rule.judge(posting, persona)
    conditions = justification["conditions"]
    fields = cleaned_fields(posting)
    statuses = {}
    for condition, name, _ in FIELDS:
        if fields[name] is None:
            statuses[condition] = MISSING
        else:
            statuses[condition] = PASS if conditions[condition]["result"] else FAIL
    present = {condition: statuses[condition] != MISSING for condition in CONDITIONS}
    score = conditions["C3"]["distinct_skills_found"] if present["C3"] else None
    if present["C3"]:
        # skills_needed 2 is rule.py's own threshold, so the default gives rule.judge's C3.
        statuses["C3"] = PASS if score >= settings["skills_needed"] else FAIL
    record = {
        "posting_id": posting.get("posting_id"),
        "title": fields["title"],
        "location": fields["location"],
        "verdict": None,
        "C1": statuses["C1"],
        "C2": statuses["C2"],
        "C3": statuses["C3"],
        "score": score,
        "title_match": list(conditions["C1"]["matched_resume_values"]) if present["C1"] else [],
        "location_match": list(conditions["C2"]["matched_resume_values"]) if present["C2"] else [],
        "skills_found": list(conditions["C3"]["matched_resume_values"]) if present["C3"] else [],
        "missing": [name for condition, name, _ in FIELDS if statuses[condition] == MISSING],
        "closest_call": is_closest_call(statuses, score),  # v1's flag, whatever the options
    }
    if settings["seniority_words"] or settings["max_years"] is not None:
        statuses["C4"], reasons, years_matched = level(fields, settings["seniority_words"], settings["max_years"])
        record.update({"C4": statuses["C4"], "C4_reason": "; ".join(reasons), "years_matched": years_matched})
    record["verdict"] = verdict_of(statuses)
    return record


def rank(records):
    """F8: the relevant records only, by score high to low, then board key, then posting id.

    Board keys and ids are compared as strings (GATE §3), so "10" comes before
    "9". No date is read: §4's rule never uses posting date (W7).
    """
    relevant = [record for record in records if record["verdict"] == RELEVANT]
    return sorted(relevant, key=lambda r: (-r["score"], str(r["board_key"]), str(r["posting_id"])))
