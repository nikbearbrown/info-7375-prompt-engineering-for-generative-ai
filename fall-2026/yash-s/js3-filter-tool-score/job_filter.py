"""The JS3 filter: FILTER.md Version 1.1 as code. Standard library only.

Every function names the FILTER.md rule it implements. The word lists live in
rules/*.json; this file holds only the logic. Nothing here contacts a network
or writes a file.
"""
import json
import re
from pathlib import Path

import postings as P

HERE = Path(__file__).resolve().parent
RULES_DIR = HERE / "rules"

ROLE_CATEGORIES = ("target", "related", "special_review", "excluded", "none")


# --------------------------------------------------------------- loading rules

def load_rules(rules_dir=RULES_DIR, persona=None):
    """Read the three rules files and Priya's résumé into one dict."""
    rules_dir = Path(rules_dir)
    filt = json.loads((rules_dir / "filter_rules.json").read_text(encoding="utf-8"))
    loc = json.loads((rules_dir / "us_locations.json").read_text(encoding="utf-8"))
    bp_path = rules_dir / "boilerplate.json"
    boiler = json.loads(bp_path.read_text(encoding="utf-8")) if bp_path.exists() else {"sentences": []}
    if persona is None:
        persona, _ = P.load_persona()
    return {"filter": filt, "locations": loc, "boilerplate": boiler,
            "skills": counted_skills(persona, filt),
            "approved_boilerplate": approved_boilerplate(boiler)}


def counted_skills(persona, filt):
    """Rule 3: the four main résumé skill groups, minus Databricks and Unity Catalog (Rule 4).
    The familiar-only group (Ray, Kubeflow) is never read."""
    sk = filt["skills"]
    out = []
    for group in sk["counted_groups"]:
        for skill in persona["skills"].get(group, []):
            if skill not in sk["excluded"] and skill not in out:
                out.append(skill)
    return out


def approved_boilerplate(boiler):
    """Rule 4: a sentence is removed only after I have reviewed it and approved it as
    company boilerplate. Frequency alone never removes a sentence."""
    out = {}
    for s in boiler.get("sentences", []):
        if s.get("label") == "company boilerplate" and s.get("reviewed_on"):
            out.setdefault(s["board"], set()).add(s["sentence"])
    return out


# ------------------------------------------------------- whole-word matching

_compiled = {}


def phrase_re(phrase):
    r = _compiled.get(phrase)
    if r is None:
        body = r"\s+".join(re.escape(w) for w in phrase.split())
        r = _compiled[phrase] = re.compile(r"(?<!\w)" + body + r"(?!\w)", re.IGNORECASE)
    return r


def has(phrase, text):
    """Whole word or phrase, ignoring case (Rules 1-5: never arbitrary substrings)."""
    return phrase_re(phrase).search(text or "") is not None


def first(phrases, text):
    return next((p for p in phrases if has(p, text)), None)


# ------------------------------------------------------------------ Rule 1

def title_role(title, rules):
    """Rule 1, Steps 1-4 by title. 'related_candidate' still needs a Rule 2 topic
    in the job-specific text to become 'related'."""
    t = rules["filter"]["titles"]
    w = first(t["excluded"], title)
    if w:
        return "excluded", w
    w = first(t["special_review"], title)
    if w:
        return "special_review", w
    w = first(t["target"], title)
    if w:
        return "target", w
    if has(t["research_engineer_phrase"], title):
        w = first(t["research_engineer_topic_words"], title)
        if w:
            return "target", f"{t['research_engineer_phrase']} + {w}"
    w = first(t["related_title_words"], title)
    if w:
        return "related_candidate", w
    return "none", None


# ------------------------------------------------------------------ Rules 5, 6

def seniority_in_title(title, rules):
    return first(rules["filter"]["seniority"]["title_words"], title)


def seniority_in_description(job_sentences, rules):
    """Rule 5: only these patterns describe the advertised position itself."""
    for pat in rules["filter"]["seniority"]["description_patterns"]:
        rx = re.compile(pat, re.IGNORECASE)
        for s in job_sentences:
            if rx.search(s["text"]):
                return s["text"]
    return None


def special_program(title, rules):
    return first(rules["filter"]["programs"]["title_words"], title)


# ------------------------------------------------------------------ Rules 2, 3

def topics(job_text, rules):
    """Rule 2: distinct topic categories, each with the phrase that matched."""
    out = {}
    for category, phrases in rules["filter"]["topics"].items():
        if category.startswith("_"):
            continue
        w = first(phrases, job_text)
        if w:
            out[category] = w
    return out


def skills(job_text, rules):
    """Rule 3: distinct counted résumé skills found in the job-specific text."""
    return [s for s in rules["skills"] if has(s, job_text)]


# ------------------------------------------------------------------ Rule 7

_PART_SPLIT = re.compile(r"\s*[;|·]\s*")


def classify_location_part(part, rules):
    L = rules["locations"]
    p = part.strip()
    if any(has(m, p) for m in L["us_markers"]):
        return "us"
    if p in L["us_exact"]:
        return "us"
    if any(has(s, p) for s in L["us_states"]):
        return "us"
    m = re.search(r",\s*([A-Z]{2})\s*$", p)
    if m and m.group(1) in L["us_postal_codes"]:
        return "us"
    if p.lower() in {c.lower() for c in L["us_cities"]["names"]}:
        return "us"
    if any(has(c, p) for c in L["non_us_countries"]["names"]):
        return "non_us"
    bare = re.sub(r"\s*-\s*Remote\s*$", "", p, flags=re.IGNORECASE).strip()
    if bare.lower() in {c.lower() for c in L["non_us_bare_cities"]["names"]}:
        return "non_us"
    return "unknown"


def location(loc_string, rules):
    """Rule 7: US if any part is US; non-US only if every part is non-US; else unknown."""
    parts = [x.strip() for x in _PART_SPLIT.split(loc_string or "") if x.strip()]
    classified = [[p, classify_location_part(p, rules)] for p in parts]
    kinds = {c for _, c in classified}
    if "us" in kinds:
        status = "us"
    elif classified and kinds == {"non_us"}:
        status = "non_us"
    else:
        status = "unknown"
    return {"status": status, "parts": classified}


# ------------------------------------------------------------------ Rule 8

_NUM = r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
YEAR_RE = re.compile(
    r"(?<![\w.$])" + _NUM + r"\s*(\+|plus)?\s*(?:(?:-|–|—|to)\s*" + _NUM + r"\s*\+?)?\s*(?:or more\s+)?years?(?!\w)",
    re.IGNORECASE)
_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
          "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _num(s):
    return int(s) if s.isdigit() else _WORDS[s.lower()]


def year_counts(sentence_text, heading, rules):
    """All year counts in one sentence, each marked as a qualification, preferred, or
    ignored (with the reason). Rule 8, 'Which year counts are qualifications'."""
    E = rules["filter"]["experience"]
    out, prev_end = [], 0
    for m in YEAR_RE.finditer(sentence_text):
        lo = _num(m.group(1))
        hi = _num(m.group(3)) if m.group(3) else None
        c = {"text": m.group(0), "min": lo, "max": hi, "start": m.start(), "end": m.end(), "kind": "mandatory", "why": ""}
        before, after = sentence_text[:m.start()], sentence_text[m.end():]
        if lo > E["ignore_numbers_above"]:
            c["kind"], c["why"] = "ignored", f"number above {E['ignore_numbers_above']}"
        else:
            for pat in E["unrelated_patterns"]:
                if (not pat["before"] or re.search(pat["before"], before, re.IGNORECASE)) and \
                   (not pat["after"] or re.search(pat["after"], after, re.IGNORECASE)):
                    c["kind"], c["why"] = "ignored", pat["name"]
                    break
        if c["kind"] == "mandatory":
            window = sentence_text[prev_end:m.start()]
            word = first(E["preferred_words"], window)
            hword = first(E["preferred_heading_words"], heading)
            if word or hword:
                c["kind"] = "preferred"
                c["why"] = f"'{word}' before it" if word else f"under the heading '{heading}'"
        out.append(c)
        prev_end = m.end()
    return out


def connector(between, rules):
    """Rule 8: how two year counts in one sentence are connected, first row that applies."""
    E = rules["filter"]["experience"]
    if any(has(w, between) for w in E["and_words"]):
        return "AND"
    has_or, has_and = has("or", between), has("and", between)
    if has_or and not has_and:
        return "OR"
    if has_or and has_and:
        return "AMBIGUOUS"
    return "AND"


def experience(job_sentences, rules):
    """Rule 8: read the job-specific sentences and return one experience status."""
    E = rules["filter"]["experience"]
    cutoff = E["screening_cutoff_years"]
    sents = [s for s in job_sentences if E["anthropic_boilerplate"].lower() not in s["text"].lower()]

    mandatory, preferred, ignored = [], [], []
    for i, s in enumerate(sents):
        for c in year_counts(s["text"], s["heading"], rules):
            c["sentence"], c["index"] = s["text"], i
            {"mandatory": mandatory, "preferred": preferred, "ignored": ignored}[c["kind"]].append(c)

    # Join consecutive mandatory counts into units (an OR group is one unit).
    units = []
    for c in mandatory:
        link = "AND"
        if units:
            last = units[-1]["counts"][-1]
            if last["index"] == c["index"]:
                link = connector(c["sentence"][last["end"]:c["start"]], rules)
            elif c["index"] == last["index"] + 1 and re.search(r"(?<!\w)or\s*$", last["sentence"], re.IGNORECASE) \
                    and c is next(x for x in mandatory if x["index"] == c["index"]):
                link = "OR"
        if link == "AND":
            units.append({"counts": [c], "links": []})
        else:
            units[-1]["counts"].append(c)
            units[-1]["links"].append(link)

    for u in units:
        u["ambiguous"] = ""
        if "AMBIGUOUS" in u["links"]:
            u["ambiguous"] = "both 'or' and 'and' between year counts"
        elif "OR" in u["links"]:
            texts = {c["sentence"] for c in u["counts"]}
            d = next((w for w in E["degree_words"] for t in texts if has(w, t)), None)
            if d:
                u["ambiguous"] = f"an alternative depends on a degree ('{d}')"
        u["min"] = None if u["ambiguous"] else min(c["min"] for c in u["counts"])
        u["kind"] = "OR" if "OR" in u["links"] or "AMBIGUOUS" in u["links"] else "single"

    detail = {
        "units": [{"kind": u["kind"], "min": u["min"], "ambiguous": u["ambiguous"],
                   "counts": [c["text"] for c in u["counts"]], "sentence": u["counts"][0]["sentence"]} for u in units],
        "preferred": [{"text": c["text"], "why": c["why"], "sentence": c["sentence"]} for c in preferred],
        "ignored": [{"text": c["text"], "why": c["why"], "sentence": c["sentence"]} for c in ignored],
    }

    above = [u for u in units if u["min"] is not None and u["min"] > cutoff]
    if above:
        top = max(u["min"] for u in above)
        return {"status": "above_cutoff", "decisive_min": top,
                "reason": f"mandatory requirement of {top}+ years is above the {cutoff}-year cutoff", **detail}
    if any(u["ambiguous"] for u in units):
        why = next(u["ambiguous"] for u in units if u["ambiguous"])
        return {"status": "unknown", "decisive_min": None, "reason": f"ambiguous requirement: {why}", **detail}
    if not units:
        text = " ".join(s["text"] for s in sents)
        if any(re.search(p, text, re.IGNORECASE) for p in E["no_experience_patterns"]):
            return {"status": "compatible", "decisive_min": 0,
                    "reason": "the posting says no professional experience is required and states no year count", **detail}
        if re.search(r"(?<![\w.])\d+\s*\+?\s*months?(?!\w)", text, re.IGNORECASE):
            return {"status": "unknown", "decisive_min": None, "reason": "experience stated only in months", **detail}
        return {"status": "unknown", "decisive_min": None, "reason": "no mandatory year count", **detail}
    decisive = max(u["min"] for u in units)
    if decisive == 0:
        return {"status": "compatible", "decisive_min": 0, "reason": "decisive minimum is 0 years", **detail}
    return {"status": "within_cutoff", "decisive_min": decisive,
            "reason": f"minimum of {decisive} year(s) is within the {cutoff}-year cutoff, but Priya has "
                      f"{E['priya_experience_months']} months and does not meet it", **detail}


# ------------------------------------------------------- one posting, Section 4

def job_specific(posting, rules):
    """All sentences, and the job-specific ones: approved boilerplate removed (Rule 4)."""
    sents = P.sentences(posting["markup"])
    approved = rules["approved_boilerplate"].get(posting["board"], set())
    job = [s for s in sents if s["text"] not in approved]
    return sents, job


def evaluate(posting, rules):
    """Score one posting and decide it in the fixed order of FILTER.md section 4."""
    S = rules["filter"]["scoring"]
    sents, job = job_specific(posting, rules)
    job_text = "\n".join(s["text"] for s in job)

    role, role_match = title_role(posting["title"], rules)
    found_topics = topics(job_text, rules)
    if role == "related_candidate":
        role = "related" if found_topics else "none"
    role_points = S["role_points"].get(role, 0)
    topic_points = S["topic_points"]["two_or_more"] if len(found_topics) >= 2 else \
        S["topic_points"]["one"] if found_topics else 0
    found_skills = skills(job_text, rules)
    skill_points = S["skill_points"]["two_or_more"] if len(found_skills) >= 2 else \
        S["skill_points"]["one"] if found_skills else 0
    loc = location(posting["location"], rules)
    loc_points = S["us_location_points"] if loc["status"] == "us" else 0
    exp = experience(job, rules)
    exp_points = S["experience_compatible_points"] if exp["status"] == "compatible" else 0
    score = role_points + topic_points + skill_points + loc_points + exp_points

    # Step 1: hard exclusions. All that apply are recorded; any one rejects.
    hard = []
    if role == "excluded":
        hard.append(f"excluded title word '{role_match}'")
    w = seniority_in_title(posting["title"], rules)
    if w:
        hard.append(f"seniority word '{w}' in title")
    sd = seniority_in_description(job, rules)
    if sd:
        hard.append(f"seniority statement in description: \"{sd[:160]}\"")
    w = special_program(posting["title"], rules)
    if w:
        hard.append(f"special program ('{w}' in title)")
    if role == "none":
        hard.append("no matching role")
    if loc["status"] == "non_us":
        hard.append("every location part is outside the US")
    if exp["status"] == "above_cutoff":
        hard.append(exp["reason"])

    description_present = bool(sents)
    review = []
    if hard:
        decision, step = "rejected", 1
    elif score < S["threshold"]:
        decision, step = "rejected", 2
    else:
        # Step 3: potentially relevant but not confirmable.
        if role == "special_review":
            review.append(f"special review role ('{role_match}')")
        if exp["status"] == "unknown":
            review.append(f"experience unknown: {exp['reason']}")
        if loc["status"] == "unknown":
            review.append("location unknown")
        if exp["status"] == "within_cutoff":
            review.append(f"minimum experience {exp['decisive_min']} year(s): within the screening cutoff, above Priya's 8 months")
        if not found_skills:
            review.append("matches no résumé skill")
        if review:
            decision, step = "review", 3
        else:
            # Step 4: every confirmed-shortlist condition, with a safety net.
            failed = []
            if score < S["threshold"]:
                failed.append("score below threshold")
            if role not in ("target", "related"):
                failed.append("not a target or related role")
            if not found_skills:
                failed.append("no résumé skill")
            if loc["status"] != "us":
                failed.append("no clearly supported US location")
            if exp["status"] != "compatible":
                failed.append("experience not explicitly compatible")
            if not description_present:
                failed.append("description missing or empty")
            if failed:
                decision, step = "review", 4
                review = [f"failed confirmed-shortlist condition: {f}" for f in failed]
            else:
                decision, step = "confirmed", 4

    return {
        "board": posting["board"], "id": posting["id"], "title": posting["title"],
        "location": posting["location"], "url": posting["url"],
        "source_run": posting["source_run"], "source_file": posting["source_file"],
        "decision": decision, "decision_step": step,
        "score": score,
        "points": {"role": role_points, "topics": topic_points, "skills": skill_points,
                   "location": loc_points, "experience": exp_points},
        "role": role, "role_match": role_match,
        "topics": found_topics, "skills": found_skills,
        "location_status": loc["status"], "location_parts": loc["parts"],
        "experience_status": exp["status"], "experience_reason": exp["reason"],
        "experience_detail": {k: exp[k] for k in ("units", "preferred", "ignored")},
        "hard_exclusions": hard, "review_reasons": review,
        "description_present": description_present,
        "sentences_total": len(sents), "boilerplate_sentences_removed": len(sents) - len(job),
    }


# ------------------------------------------------------------ the two lists

def review_candidates(results, rules):
    """Section 4: top N review-queue postings by descending score, then board, then ID as text.
    Drawn only from the review queue, so it never overlaps the confirmed shortlist."""
    n = rules["filter"]["review_candidates"]["size"]
    queue = [r for r in results if r["decision"] == "review"]
    return sorted(queue, key=lambda r: (-r["score"], r["board"], str(r["id"])))[:n]


def confirmed_shortlist(results):
    return [r for r in results if r["decision"] == "confirmed"]
