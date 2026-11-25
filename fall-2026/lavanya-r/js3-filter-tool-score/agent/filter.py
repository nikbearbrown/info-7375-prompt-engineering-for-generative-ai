"""FILTER.md as code. config/filter.json holds the words and numbers;
FILTER.md section 1 is the source (tests/test_filter.py checks they agree).

evaluate(posting) -> a record anyone can recompute by hand:
    verdict        "keep" | "reject" | "cannot_tell"
    rejected_by    every hard rule that fired (R1..R5), or ["below_threshold"]
    cannot_tell_because   which inputs were missing
    score, score_parts {"S1","S2","S3"}, matched {rule: [words]}

Every rule is always computed (no short-circuit), so a record lists every
rule that fired, not just the first.
"""

import functools
import json
import pathlib
import re

from agent.rule import US_MARKERS, NO_SPONSOR_PHRASES, find_terms, \
    resume_skills

HERE = pathlib.Path(__file__).resolve().parent.parent
YEARS = re.compile(r"(\d+)\s*\+?\s*(?:(?:-|–|to)\s*\d+\s*)?\+?\s*years?",
                   re.IGNORECASE)
BARE_REMOTE = re.compile(r"^\s*remote\s*$", re.IGNORECASE)


@functools.lru_cache(maxsize=None)
def default_config():
    return json.loads((HERE / "config" / "filter.json").read_text())


@functools.lru_cache(maxsize=None)
def default_skills():
    resume = json.loads((HERE / "persona" / "priya-nair.resume.json")
                        .read_text())
    return tuple(s for _, s in resume_skills(resume))


def location_parts(locations):
    """Each location string, split on ';' and '|' (Databricks and OpenAI
    pack several places into one string)."""
    out = []
    for loc in locations or []:
        out += [p.strip() for p in re.split(r"[;|]", loc) if p.strip()]
    return out


def us_parts(parts, cfg):
    codes = "|".join(cfg["us_state_codes"])
    state_code = re.compile(r",\s*(?:%s)(?![A-Za-z])" % codes)
    canada = cfg.get("canadian_places", [])  # v1.1: "Ontario, CA" is Canada
    return [p for p in parts
            if find_terms(p, US_MARKERS + cfg["us_cities"])
            or (state_code.search(p) and not find_terms(p, canada))]


def years_asked(text, cfg):
    return [int(n) for n in YEARS.findall(text) if int(n) < cfg["years_cap"]]


def evaluate(posting, cfg=None, skills=None):
    cfg = cfg or default_config()
    skills = default_skills() if skills is None else skills
    title = posting.get("title") or ""
    text = posting.get("text") or ""
    parts = location_parts(posting.get("locations"))

    missing = []
    text_ok = len(text) >= cfg["min_text_chars"]
    if not text_ok:
        missing.append("text_under_%d_chars" % cfg["min_text_chars"])
    if not parts:
        missing.append("no_location")
    elif all(BARE_REMOTE.match(p) for p in parts):
        missing.append("only_bare_remote")
    loc_ok = not any(m in missing for m in ("no_location", "only_bare_remote"))

    matched = {
        "R1": find_terms(title, cfg["seniority_words"]),
        "R2": find_terms(title, cfg["not_my_role_words"]),
        "R3": us_parts(parts, cfg) if loc_ok else [],
        "R4": find_terms(text, NO_SPONSOR_PHRASES) if text else [],
        "R5": sorted(set(years_asked(text, cfg))) if text else [],
        "S1": find_terms(title, cfg["role_words"]),
        "S2": find_terms(text, cfg["topic_words"]),
        "S3": find_terms(text, list(skills)),
    }
    fired = []
    if matched["R1"]:
        fired.append("R1")
    if matched["R2"]:
        fired.append("R2")
    if loc_ok and not matched["R3"]:
        fired.append("R3")
    if matched["R4"]:
        fired.append("R4")
    if matched["R5"] and min(matched["R5"]) > cfg["max_years_asked"]:
        fired.append("R5")

    score_parts = {
        "S1": cfg["role_points"] if matched["S1"] else 0,
        "S2": min(cfg["topic_max"], len(matched["S2"])),
        "S3": min(cfg["skill_max"], len(matched["S3"])),
    }
    score = sum(score_parts.values())

    if fired:
        verdict, rejected_by = "reject", fired
    elif missing:
        verdict, rejected_by = "cannot_tell", []
    elif score >= cfg["threshold"]:
        verdict, rejected_by = "keep", []
    else:
        verdict, rejected_by = "reject", ["below_threshold"]

    return {"key": posting.get("key"), "title": title,
            "locations": posting.get("locations") or [],
            "filter_version": cfg["version"], "verdict": verdict,
            "rejected_by": rejected_by, "cannot_tell_because": missing,
            "score": score, "score_parts": score_parts,
            "threshold": cfg["threshold"], "matched": matched}
