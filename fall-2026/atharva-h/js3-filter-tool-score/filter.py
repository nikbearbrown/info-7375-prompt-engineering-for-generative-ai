"""The JS3 filter, exactly as FILTER.md describes it: reject rules R1-R4, a score, and a threshold.

    python3 filter.py run [VERSION]         score every corpus posting; write state/filter/verdicts_vVERSION.json
    python3 filter.py show KEY [VERSION]    print one posting's verdict and the evidence for it

VERSION is "1.2" (current, the default) or "1.0". v1.0 stays callable so the reject audit and every
measurement made against it can be rerun exactly. v1.2 differs in three places (FILTER.md v1.2):
- R4 also matches "does not provide sponsorship"                                  (F1)
- R2 takes the highest of the stated requirements' lowest numbers, not the lowest (F4)
- the skill word "reporting" does not count before "to" / "directly to"           (F5)

The filter is two-valued: "keep" or "reject". It never calls a model. Every rule records the exact words
that fired it, so a verdict can be checked against the posting text.

The two wrong versions from FILTER.md ("Wrong versions") live here too, as functions the tests run, so the
tests can show the real filter is not either of them. They are never used to produce a verdict.
"""
import json
import re
import sys

VERSION = "1.2"
VERSIONS = ("1.0", "1.2")
THRESHOLD = 4

SENIORITY = re.compile(r"\b(senior|sr|lead|principal|staff|manager|director|head|vp|vice president|chief)\b", re.I)
ROLE = re.compile(r"\b(data analyst|bi analyst|business intelligence analyst|business analyst|reporting analyst|"
                  r"analytics analyst)\b", re.I)
ANALYST = re.compile(r"\banalyst\b", re.I)
SKILLS = {"SQL": r"sql", "Tableau": r"tableau", "Power BI": r"power\s+bi", "Excel": r"excel", "Python": r"python",
          "dashboard(s)": r"dashboards?", "reporting": r"reporting"}
SKILL_RE = {name: re.compile(r"\b" + pat + r"\b", re.I) for name, pat in SKILLS.items()}
NO_SPONSOR = re.compile(r"unable to sponsor|will not sponsor|does not sponsor|no visa sponsorship|"
                        r"without sponsorship now or in the future", re.I)

# R2. A stated requirement is a number of years followed, within a short span, by "experience". Numbers above
# 15 are left out ("20 years of experience building products" is about the company, not the candidate).
YEARS = re.compile(r"\b(?:at least|minimum(?: of)?|min\.?)?\s*(\d{1,2})\s*(?:\+|(?:-|–|to)\s*\d{1,2}\+?)?\s*"
                   r"(?:years?|yrs?)\b[^.\n;]{0,50}?\bexperience\b", re.I)
YEARS_MAX = 15

# v1.2 (F1, F5)
NO_SPONSOR_V12 = re.compile(NO_SPONSOR.pattern + r"|does not provide sponsorship", re.I)
REPORTING_V12 = re.compile(r"\breporting\b(?!\s+(?:directly\s+)?to\b)", re.I)

# R3. Each location is US, outside the US, or unknown ("Remote", "Hybrid", Stripe's literal "LOCATION"). An
# unknown location is a missing field, and a missing field never rejects.
STATE_NAMES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
               "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
               "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
               "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
               "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
               "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
               "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "District of Columbia"]
US_CITIES = ["NYC", "San Francisco", "Seattle", "Boston", "Chicago", "Austin", "Denver", "Los Angeles", "Atlanta",
             "Miami", "Philadelphia", "Palo Alto", "Mountain View", "Menlo Park", "San Jose", "San Diego",
             "Portland", "Dallas", "Houston", "Nashville", "Raleigh", "Pittsburgh", "Phoenix", "Salt Lake City",
             "Minneapolis", "Detroit", "Foster City", "Redwood City", "Sunnyvale", "Brooklyn", "Jersey City",
             "Washington, D.C.", "Washington DC", "Las Vegas", "SF",
             "San Francsico"]  # "San Francsico" is a typo in one Stripe posting
CODES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH "
         "OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
US = re.compile(r"\bUnited States\b|\bUSA\b|\bU\.S\.|\bUS\b|\b(" + "|".join(STATE_NAMES + US_CITIES)
                + r")\b|, (" + "|".join(CODES) + r")\b")
# Regions that include the US but are not only the US ("Americas", "NAMER") are unknown, not US.
UNKNOWN = re.compile(r"^(?:remote|hybrid|anywhere|location|locations|flexible|global|worldwide|multiple|"
                     r"various|in[- ]office|on[- ]?site|office|tbd|n/?a|americas?|amer|namer|north america|sea|"
                     r"west coast|east coast|preferred|[\s,;/()\-–|&]|and|or)*$", re.I)
US_COUNTRY = {"us", "usa", "united states", "united states of america"}


def place(location):
    """'us', 'non-us', or 'unknown' for one location string."""
    if US.search(location):
        return "us"
    return "unknown" if UNKNOWN.match(location.strip()) else "non-us"


def lowest_years(text):
    """(lowest stated required years, the words that stated it), or (None, None)."""
    found = [(int(m.group(1)), m.group(0).strip()) for m in YEARS.finditer(text) if int(m.group(1)) <= YEARS_MAX]
    return min(found) if found else (None, None)


def highest_requirement(text):
    """v1.2 (F4): every stated requirement must hold, so the highest of their lowest numbers counts."""
    found = [(int(m.group(1)), m.group(0).strip()) for m in YEARS.finditer(text) if int(m.group(1)) <= YEARS_MAX]
    return max(found) if found else (None, None)


def skills(text, skill_re=None):
    skill_re = skill_re or SKILL_RE
    return {name: rx.search(text).group(0) for name, rx in skill_re.items() if rx.search(text)}


def evaluate(p, version=VERSION):
    """The verdict of one filter version for one posting, with the words behind every rule and point.
    Module-level names are read at call time, so a test or a measurement can replace one of them."""
    if version == "1.0":
        no_sponsor, skill_re, years = NO_SPONSOR, SKILL_RE, lowest_years
    elif version == "1.2":
        no_sponsor, skill_re, years = NO_SPONSOR_V12, dict(SKILL_RE, reporting=REPORTING_V12), highest_requirement
    else:
        raise ValueError(f"unknown filter version {version!r}")
    title, text = p.get("title") or "", p.get("text") or ""
    fired = {}
    m = SENIORITY.search(title)
    if m:
        fired["R1"] = m.group(0)
    if text:
        low, words = years(text)
        if low is not None and low >= 3:
            fired["R2"] = words
        m = no_sponsor.search(text)
        if m:
            fired["R4"] = m.group(0)
    locations = [loc for loc in (p.get("locations") or ([p["location"]] if p.get("location") else [])) if loc]
    places = {loc: place(loc) for loc in locations}
    us_country = (p.get("country") or "").strip().lower() in US_COUNTRY
    known = [v for v in places.values() if v != "unknown"]
    if known and not us_country and all(v == "non-us" for v in known):
        fired["R3"] = "; ".join(loc for loc, v in places.items() if v == "non-us")
    role = ROLE.search(title)
    if role:
        title_points, title_signal = 4, role.group(0)
    elif ANALYST.search(title):
        title_points, title_signal = 1, "analyst"
    else:
        title_points, title_signal = 0, None
    found = skills(text, skill_re) if title_points else {}
    score = title_points + len(found)
    keep = not fired and score >= THRESHOLD
    return {"key": p.get("key"), "version": version, "verdict": "keep" if keep else "reject", "score": score,
            "threshold": THRESHOLD, "rejected_by": fired, "title_signal": title_signal, "skills": found,
            "places": places}


# --- FILTER.md "Wrong versions": kept only so the tests can tell them apart from the real filter ---

def wrong_substring(p):
    """Wrong version 1: role and skill words matched as raw substrings, with no word boundaries."""
    title, text = (p.get("title") or "").lower(), (p.get("text") or "").lower()
    title_points = 4 if any(r in title for r in ("data analyst", "bi analyst", "business analyst")) else (
        1 if "analyst" in title else 0)
    found = [n for n, pat in (("SQL", "sql"), ("Tableau", "tableau"), ("Power BI", "bi"), ("Excel", "excel"),
                              ("Python", "python"), ("dashboard(s)", "dashboard"), ("reporting", "reporting"))
             if pat in text] if title_points else []
    return title_points + len(found)


def wrong_title_only(p):
    """Wrong version 2: only the title is read, so R2 and R4 and the skill points never apply."""
    title = p.get("title") or ""
    if SENIORITY.search(title):
        return "reject"
    return "keep" if ROLE.search(title) else "reject"


def main(argv):
    import corpus
    from policy import Policy
    from tools import Tools
    tools = Tools(Policy())
    run, postings = corpus.load(tools)
    if argv[1:2] == ["show"] and len(argv) in (3, 4):
        [p] = [p for p in postings if p["key"] == argv[2]]
        print(json.dumps(dict(evaluate(p, *argv[3:]), title=p["title"]), indent=1))
        return 0
    if argv[1:2] != ["run"] or len(argv) > 3 or argv[2:] and argv[2] not in VERSIONS:
        print(__doc__)
        return 2
    version = argv[2] if len(argv) == 3 else VERSION
    verdicts = [dict(evaluate(p, version), corpus=p["corpus"], title=p["title"]) for p in postings]
    kept = [v for v in verdicts if v["verdict"] == "keep"]
    tools.write_text(f"state/filter/verdicts_v{version}.json",
                     json.dumps({"version": version, "run": run, "postings": len(verdicts), "kept": len(kept),
                                 "verdicts": verdicts}, indent=1) + "\n")
    print(f"v{version}: {len(verdicts)} postings, {len(kept)} kept")
    for v in sorted(kept, key=lambda v: -v["score"]):
        print(f"  {v['score']}  {v['key']}  {v['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
