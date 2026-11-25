"""FILTER.md v1 as code. The word lists and numbers come from a filter file (filter-v1.json), so a
change to the filter is a change to one file. How each phrase of FILTER.md became a check, and what is
inherited unchanged from JS2's rule (jsagent/rule.py), is in FILTER-NOTES.md.

Each rule gives one of three outcomes: pass, fail, or "cannot tell" (only where FILTER.md says to:
answers 6a, 6b and follow-up A). Each outcome carries its evidence: quotes copied from the posting's
own fields, which verify_quotes() checks. The verdict: any fail is Not Relevant; otherwise any
"cannot tell" is I cannot tell; otherwise Relevant. A closest call fails exactly one rule and passes
all the others (answer 10)."""
import json
import pathlib
import re

from jsagent import rule as js2
from js3 import corpus, sections

PASS, FAIL, UNSURE = "pass", "fail", "cannot tell"
NAMES = {1: "title", 2: "department", 3: "location", 4: "skills", 5: "experience", 6: "exclusions"}
LIST_FIELDS = ("departments", "offices")

# Rule 3. The country part is case-sensitive, so the word "us" ("work with us") is not the US.
US_WIDE_RE = re.compile(
    r"\b(?i:reside|residing|located|based|live|living|work|working|remote|remotely)\s+(?i:anywhere\s+)?"
    r"(?i:in|within|from|across)\s+(?i:the\s+)?(?:United States|U\.S\.A?\.?|USA|US)\b"
    r"|\b(?i:anywhere in the)\s+(?:United States|U\.S\.?|US)\b|\b(?:US|U\.S\.)[- ](?i:based)\b")
REMOTE_AD_RE = re.compile(
    r"(?i)\b(?:fully remote|100% remote|remote[- ]first|work (?:fully )?remotely|"
    r"(?:this|the) (?:role|position|job) (?:is|can be) (?:fully )?remote|"
    r"(?:is|as) an? (?:fully )?remote (?:position|role|job)|"
    r"remote (?:within|in|from|across) the (?:US|U\.S\.|United States)|open to remote)\b")
WORKPLACE_CUE = r"(?:based|located|work(?:ing)? (?:from|out of|in|at)|office|hub|hybrid|on[- ]?site|in[- ]office|commut\w*)"
# Rule 6, follow-up C: the ad itself says the job is not full-time and permanent.
NOT_PERMANENT_RE = re.compile(r"(?i)\b(?:is|as) an? (?:part[- ]time|temporary|seasonal|fixed[- ]term) "
                              r"(?:position|role|job|contract|assignment|opportunity)\b")


def load_config(path):
    return json.loads(pathlib.Path(path).read_text())


def from_raw(ats, token, job):
    """A raw job object (as a board returned it) as the posting the rules read."""
    return corpus.parse_job(ats, token, job)


def quote(field, text):
    return {"field": field, "quote": text}


def around(content, start, end, width=180):
    """An exact slice of content around [start, end), cut at spaces, at most about `width` chars."""
    a = max(0, start - width // 2)
    b = min(len(content), end + width // 2)
    while a > 0 and not content[a - 1].isspace() and a > start - width:
        a -= 1
    while b < len(content) and not content[b].isspace() and b < end + width:
        b += 1
    return content[a:b].strip()


def sentence_with(content, start, end):
    """The sentence (or line) around [start, end), as an exact slice of content."""
    a = max(content.rfind(". ", 0, start) + 2, content.rfind("\n", 0, start) + 1, 0)
    stops = [i for i in (content.find(". ", end), content.find("\n", end)) if i >= 0]
    b = min(stops) + 1 if stops else len(content)
    s = content[a:b].strip()
    return s if len(s) <= 300 else around(content, start, end)


def line(n, outcome, detail, evidence=()):
    return {"n": n, "rule": NAMES[n], "outcome": outcome, "detail": detail, "evidence": list(evidence)}


# ---- Rule 1, title (answer 4) ------------------------------------------------------------------

def r1_title(p, persona, cfg):
    if not p["title"]:
        return line(1, FAIL, "posting.title is missing")
    hits = js2.find_terms(cfg["rule1_title_phrases"], p["title"])
    if hits:
        return line(1, PASS, f"the title contains the role phrase {hits[0]!r}", [quote("title", p["title"])])
    return line(1, FAIL, "the title contains none of the nine role phrases", [quote("title", p["title"])])


# ---- Rule 2, department (answer 5, review/19) --------------------------------------------------

def r2_department(p, persona, cfg):
    if not p["departments"]:
        return line(2, FAIL, "posting.departments is missing")
    wanted = {d.lower(): d for d in cfg["rule2_departments"]}
    aliases = cfg.get("rule2_department_aliases", {}).get(p["board"], {})
    for d in p["departments"]:
        if d.strip().lower() in wanted:
            return line(2, PASS, f"the department {d!r} is on the list", [quote("departments", d)])
        if d.strip() in aliases:
            return line(2, PASS, f"the department {d!r} counts as {aliases[d.strip()]!r} on the {p['board']} board "
                                 "only (FILTER.md answer 5)", [quote("departments", d)])
    return line(2, FAIL, f"none of the departments {p['departments']} is on the list",
                [quote("departments", d) for d in p["departments"]])


# ---- Rule 3, location (answer 6, 6a, 6b, follow-up A) ------------------------------------------

def has_city(text, city):
    return bool(js2.term_re(city).search(text or ""))


def remote_tagged(p):
    places = [p["location"]] + p["offices"]
    return any(js2.term_re("Remote").search(x or "") for x in places) or (p.get("workplace_type") or "").lower() == "remote"


def tag_states(p):
    states = set()
    for place in [p["location"]] + p["offices"]:
        for m in re.finditer(r"Remote\s*\(([^)]+)\)", place or ""):
            if m.group(1).strip() in js2.US_STATES:
                states.add(m.group(1).strip())
    return states


RESIDE_RE = re.compile(r"(?i)\b(?:reside|resides|residing|residents?\s+of|live|living)\s+(?:in|within|of)\b[:\s]*([^.]{0,160})")


def ad_states(content, p=None, cfg=None):
    """States a 'reside in / located in ...' list in the ad limits the job to. JS2's reading: a list
    counts when it names at least two states. FILTER.md v1.1 (A4, when the filter file sets
    rule3_single_state_residence): a residence line ("reside in", "live in", "residents of") that names
    ONE state also counts, outside the benefits and legal text."""
    found_all, quotes = set(), []
    for m in js2.STATE_LIST_RE.finditer(content):
        found = {s for s in js2.US_STATES if js2.term_re(s).search(m.group(1))}
        if len(found) >= 2:
            found_all |= found
            quotes.append(sentence_with(content, m.start(), m.end()))
    if cfg and cfg.get("rule3_single_state_residence") and p is not None:
        text = sections.text_outside(content, p.get("blocks") or [], {"perk", "legal"})
        for m in RESIDE_RE.finditer(text):
            found = {s for s in js2.US_STATES if js2.term_re(s).search(m.group(1))}
            if len(found) == 1 and found - found_all:
                found_all |= found
                quotes.append(sentence_with(content, m.start(), m.end()))
    return found_all, quotes


def first(rx, text):
    return rx.search(text or "")


def workplace_mentions(content, city):
    """Sentences in the ad that name `city` together with a workplace word (based, office, hybrid...)."""
    out = []
    for m in js2.term_re(city).finditer(content):
        s = sentence_with(content, m.start(), m.end())
        if re.search(r"(?i)" + WORKPLACE_CUE, s):
            out.append(s)
    return out


def r3_location(p, persona, cfg):
    city, state = cfg["rule3_home_city"], cfg["rule3_home_state"]
    loc, offices, content = p["location"], p["offices"], p["content"]
    if not loc and not offices:
        return line(3, FAIL, "posting.location and posting.offices are missing")
    ev_places = ([quote("location", loc)] if loc else []) + [quote("offices", o) for o in offices]
    remote = remote_tagged(p)
    loc_home = has_city(loc, city)
    off_home = any(has_city(o, city) for o in offices)

    if loc_home or off_home:
        if loc and offices and loc_home != off_home:
            # 6b: the location field and the office list disagree about Boston; check the description.
            others = [x for x in ([loc] + offices) if x and not has_city(x, city) and not js2.term_re("Remote").search(x)]
            other_cities = sorted({x.split(",")[0].strip() for x in others if x.split(",")[0].strip()})
            home_says = workplace_mentions(content, city)
            other_says = [s for c in other_cities for s in workplace_mentions(content, c)]
            ev = ev_places + [quote("content", s) for s in (home_says + other_says)[:3]]
            if home_says and not other_says:
                return line(3, PASS, f"posting.location {loc!r} and posting.offices {offices} disagree about {city}; "
                                     f"the description places the job in {city} (FILTER.md 6b)", ev)
            if not remote:
                if other_says and not home_says:
                    return line(3, FAIL, f"posting.location {loc!r} and posting.offices {offices} disagree; the description "
                                         f"places the job in {', '.join(other_cities)}, not {city} (FILTER.md 6b)", ev)
                return line(3, UNSURE, f"posting.location {loc!r} and posting.offices {offices} disagree about {city}, and "
                                       "the description does not settle it (FILTER.md 6b)", ev)
            # remote-tagged: the remote reading below decides
        else:
            where = loc if loc_home else next(o for o in offices if has_city(o, city))
            return line(3, PASS, f"the job is in {city} ({where!r})", ev_places)

    if remote:
        hybrid = first(js2.HYBRID_RE, content)
        wt = (p.get("workplace_type") or "").lower()
        if hybrid or wt in ("hybrid", "onsite", "on-site"):
            why = [quote("content", sentence_with(content, hybrid.start(), hybrid.end()))] if hybrid else \
                  [quote("workplace_type", p.get("workplace_type"))]
            also_remote = first(REMOTE_AD_RE, content)
            if also_remote:
                ev = ev_places + why + [quote("content", sentence_with(content, also_remote.start(), also_remote.end()))]
                return line(3, UNSURE, "a Remote tag, an ad that says hybrid or on-site, and an ad that also says "
                                       "remote: still unclear (FILTER.md follow-up A)", ev)
            return line(3, FAIL, f"posting has a Remote tag but the ad says hybrid or on-site and the job is not in "
                                 f"{city}; the description wins (FILTER.md follow-up A)", ev_places + why)
        tagged = tag_states(p)
        listed, list_quotes = ad_states(content, p, cfg)
        us_wide = first(US_WIDE_RE, content)
        us_q = [quote("content", sentence_with(content, us_wide.start(), us_wide.end()))] if us_wide else []
        lq = [quote("content", s) for s in list_quotes]
        if tagged and state not in tagged:
            if us_wide or (listed and state in listed):
                return line(3, UNSURE, f"the office tag limits remote work to {sorted(tagged)} but the ad says "
                                       f"otherwise; they disagree (FILTER.md 6a)", ev_places + us_q + lq)
            return line(3, FAIL, f"remote work is limited to {sorted(tagged)} by the office tag; {state} is not one of "
                                 "them (FILTER.md wrong version 1)", ev_places)
        if listed and state not in listed:
            if tagged and state in tagged:
                return line(3, UNSURE, f"the office tag allows {state} but the ad limits remote work to "
                                       f"{sorted(listed)}; they disagree (FILTER.md 6a)", ev_places + lq)
            return line(3, FAIL, f"the ad limits remote work to {sorted(listed)}; {state} is not one of them "
                                 "(FILTER.md wrong version 1)", ev_places + lq)
        if state in tagged or state in listed:
            return line(3, PASS, f"remote work is open to {state}", ev_places + lq)
        if js2.names_us(p) or us_wide:
            us_ev = us_q or [quote("content", sentence_with(content, m.start(), m.end()))
                             for m in [re.search(r"United States|U\.S\.|\bUSA\b|\bUS\b", content)] if m]
            places_us = [e for e in ev_places if re.search(r"United States|U\.S\.|\bUSA\b|\bUS\b", e["quote"])]
            return line(3, PASS, "remote within the United States, with no state limit that leaves out "
                                 f"{state}", ev_places + ([] if places_us else us_ev[:1]))
        return line(3, FAIL, "the posting says Remote but does not name the United States", ev_places)

    says_remote = first(REMOTE_AD_RE, content)
    if says_remote and cfg.get("rule3_single_state_residence"):
        listed, list_quotes = ad_states(content, p, cfg)
        if listed and state not in listed:
            return line(3, FAIL, f"the ad says remote, but only for residents of {sorted(listed)}; {state} is not one of "
                                 "them (FILTER.md v1.1, A4)", ev_places + [quote("content", s) for s in list_quotes])
    if says_remote:
        return line(3, UNSURE, f"posting.location {loc!r} is not {city} and not remote, but the ad says remote work is "
                               "possible; the tag and the ad disagree (FILTER.md 6a)",
                    ev_places + [quote("content", sentence_with(content, says_remote.start(), says_remote.end()))])
    return line(3, FAIL, f"the job is not in {city} and not remote", ev_places)


# ---- Rule 4, skills (answer 7, wrong version 2) ------------------------------------------------

def r4_skills(p, persona, cfg):
    if not p["content"]:
        return line(4, FAIL, "posting.content is missing")
    text = sections.text_outside(p["content"], p.get("blocks") or [], set(cfg["rule4_ignore_sections"]))
    hits, ev = [], []
    aliases = cfg.get("rule4_skill_aliases", {})
    for skill in persona["skills"]:
        m = js2.term_re(skill).search(text)
        for alias in ([] if m else aliases.get(skill, [])):  # FILTER.md v1.1, A2: a skill counts once
            m = js2.term_re(alias).search(text)
            if m:
                break
        if m:
            hits.append(skill)
            ev.append(quote("content", around(p["content"], m.start(), m.end())))
    ignored = [s for s in persona["skills"] if s not in hits and js2.term_re(s).search(p["content"])]
    note = f"; named only under a benefits heading, so not counted: {ignored}" if ignored else ""
    ok = len(hits) >= cfg["rule4_min_skills"]
    return line(4, PASS if ok else FAIL, f"the description names {len(hits)} of Alex's skills {hits} "
                                         f"({'at least' if ok else 'fewer than'} {cfg['rule4_min_skills']}){note}", ev)


# ---- Rule 5, experience (answer 8, follow-up B) ------------------------------------------------

def r5_experience(p, persona, cfg):
    mandatory = [(n, phrase) for cls, n, phrase in js2.year_phrases(p["content"]) if cls == "mandatory"]
    if not mandatory:
        return line(5, PASS, "experience not stated: the description gives no required minimum "
                             "(passes without assuming a match; FILTER.md follow-up B)")
    years, phrase = max(mandatory)
    ok = years <= cfg["rule5_max_years"]
    return line(5, PASS if ok else FAIL, f"the description requires {years} years; Alex has "
                                         f"{persona['experience_years']}", [quote("content", phrase)])


# ---- Rule 6, exclusions (answer 9, follow-up C) ------------------------------------------------

def r6_exclusions(p, persona, cfg, in_home_city):
    title, content = p["title"], p["content"]
    reasons, ev = [], []
    w = js2.find_terms(cfg["rule6_title_words"], title)
    if w:
        reasons.append(f"the title has the excluded word {w[0]!r}")
        ev.append(quote("title", title))
    w = js2.find_terms(cfg["rule6_not_full_time_title_words"], title)
    if w:
        reasons.append(f"the title says {w[0]!r}: not a full-time permanent job")
        ev.append(quote("title", title))
    et = p.get("employment_type")
    if et and et not in cfg["rule6_full_time_values"]:
        reasons.append(f"the board lists the employment type {et!r}: not a full-time permanent job")
        ev.append(quote("employment_type", et))
    kept_text = sections.text_outside(content, p.get("blocks") or [], {"perk"})
    m = NOT_PERMANENT_RE.search(kept_text)
    if m:
        reasons.append("the ad says it is not a full-time permanent job")
        ev.append(quote("content", sentence_with(content, m.start(), m.end())))
    m = js2.term_re("unpaid").search(title + " " + content)
    if m:
        reasons.append("the posting says unpaid")
        src = "title" if m.start() < len(title) else "content"
        ev.append(quote(src, title if src == "title" else around(content, m.start() - len(title) - 1, m.end() - len(title) - 1)))
    if js2.find_terms(["Contract", "Contractor"], title):
        reasons.append("the title says contract")
        ev.append(quote("title", title))
    m = js2.CONTRACT_TEXT_RE.search(content)
    if m:
        reasons.append("the ad says contract-only")
        ev.append(quote("content", sentence_with(content, m.start(), m.end())))
    m = js2.RELOCATION_RE.search(content)
    if m and not in_home_city:
        reasons.append("the ad requires relocation and the job is not in Boston")
        ev.append(quote("content", sentence_with(content, m.start(), m.end())))
    if reasons:
        return line(6, FAIL, "; ".join(reasons), ev)
    ev = [quote("title", title)] + ([quote("employment_type", et)] if et else [])
    return line(6, PASS, "no excluded title word, no sign of an internship, part-time, temporary, contract, unpaid "
                         "or relocation requirement", ev)


# ---- The verdict (answer 10) -------------------------------------------------------------------

def evaluate(p, persona, cfg):
    lines = [r1_title(p, persona, cfg), r2_department(p, persona, cfg), r3_location(p, persona, cfg),
             r4_skills(p, persona, cfg), r5_experience(p, persona, cfg)]
    lines.append(r6_exclusions(p, persona, cfg, in_home_city=lines[2]["outcome"] == PASS
                               and has_city(p["location"] + " " + " ".join(p["offices"]), cfg["rule3_home_city"])))
    failed = [l["n"] for l in lines if l["outcome"] == FAIL]
    unsure = [l["n"] for l in lines if l["outcome"] == UNSURE]
    verdict = "Not Relevant" if failed else ("I cannot tell" if unsure else "Relevant")
    return {"key": p.get("key") or f"{p['board']}:{p['id']}", "board": p["board"], "id": p["id"],
            "title": p["title"], "url": p.get("url"), "open_in_latest_run": p.get("open_in_latest_run"),
            "filter_version": cfg["version"], "verdict": verdict, "failed": failed, "unsure": unsure,
            "closest_call": len(failed) == cfg["closest_call_fails"] and not unsure, "rules": lines}


def squash(s):
    return re.sub(r"\s+", " ", s or "").strip()


def verify_quotes(record, p):
    """Every quote must be in the posting field it names (whitespace squashed on both sides).
    Returns the problems; [] means every quote is real (FILTER.md wrong version 4)."""
    problems = []
    for l in record["rules"]:
        for e in l["evidence"]:
            field, q = e["field"], squash(e["quote"])
            value = p.get(field)
            if field in LIST_FIELDS:
                ok = any(q in squash(v) for v in value or [])
            else:
                ok = bool(q) and q in squash(value if isinstance(value, str) else "")
            if not ok:
                problems.append(f"rule {l['n']}: quote {e['quote'][:60]!r} is not in posting.{field}")
    return problems


def run(postings, manifest, persona, cfg):
    """The filter over a corpus, with a per-board count. A board that failed in the latest run has no
    counts at all (FILTER.md wrong version 5)."""
    records = [evaluate(p, persona, cfg) for p in postings]
    boards = {}
    for name, b in manifest["boards_in_latest_run"].items():
        if b["status"] == "ok":
            mine = [r for r in records if r["board"] == name]
            boards[name] = {"status": "ok", "checked": True, "postings": len(mine),
                            "open": sum(1 for r in mine if r["open_in_latest_run"]),
                            "kept": sum(r["verdict"] == "Relevant" for r in mine),
                            "cannot_tell": sum(r["verdict"] == "I cannot tell" for r in mine),
                            "closest_calls": sum(r["closest_call"] for r in mine),
                            "rejected": sum(r["verdict"] == "Not Relevant" for r in mine)}
        elif b["status"] == "empty":
            boards[name] = {"status": "empty", "checked": True, "postings": 0}
        else:
            boards[name] = {"status": b["status"], "checked": False, "error": b.get("error")}
    counts = {v: sum(r["verdict"] == v for r in records) for v in ("Relevant", "I cannot tell", "Not Relevant")}
    counts["closest_calls"] = sum(r["closest_call"] for r in records)
    return {"filter_version": cfg["version"], "records": records, "boards": boards, "counts": counts}
