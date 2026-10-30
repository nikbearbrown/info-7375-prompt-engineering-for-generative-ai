"""The written rule from CONTRACT.md (Revision 2), applied literally.

judge(title, location) returns a record anyone can recompute by hand:
the verdict, which check decided it, and a justification that names the
posting fields (title, location) and Priya's résumé target fields used.
All matching is case-insensitive and whole-word, as the contract says.
"""
import re

RELEVANT = "relevant"
NOT_RELEVANT = "not relevant"

POSTING_FIELDS = ("posting.title", "posting.location.name")
RESUME_FIELDS = (
    "targets.target_role.primary",
    "targets.target_role.secondary",
    "targets.geography.current_location",
    "targets.geography.open_to_remote",
)

ROLE_TERMS = ("Machine Learning", "ML", "AI", "GenAI", "Artificial Intelligence", "Data Engineer",
              "Data Engineering", "Data Scientist", "Data Science", "Analytics", "Analyst")
EARLY_CAREER_TERMS = ("New Grad", "Early Career", "Entry", "Associate")
SENIOR_TERMS = ("Senior", "Sr.", "Sr", "Staff", "Principal", "Manager", "Director", "Head", "Lead",
                "Leader", "Intern", "Internship")
US_TERMS = ("United States", "USA", "US")
US_STATES = (
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming",
)
# Used only for "Remote without naming a non-US country" (check 3).
NON_US_COUNTRIES = (
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia",
    "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Belarus",
    "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana",
    "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon",
    "Canada", "Chad", "Chile", "China", "Colombia", "Congo", "Costa Rica", "Croatia", "Cuba",
    "Cyprus", "Czech Republic", "Czechia", "Denmark", "Dominican Republic", "Ecuador", "Egypt",
    "El Salvador", "Estonia", "Ethiopia", "Finland", "France", "Gabon", "Germany", "Ghana",
    "Greece", "Guatemala", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia",
    "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan",
    "Kenya", "Kuwait", "Latvia", "Lebanon", "Lithuania", "Luxembourg", "Malaysia", "Malta",
    "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
    "Myanmar", "Namibia", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Nigeria",
    "North Macedonia", "Norway", "Oman", "Pakistan", "Panama", "Paraguay", "Peru",
    "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda",
    "Saudi Arabia", "Senegal", "Serbia", "Singapore", "Slovakia", "Slovenia", "South Africa",
    "South Korea", "Korea", "Spain", "Sri Lanka", "Sweden", "Switzerland", "Taiwan",
    "Tanzania", "Thailand", "Tunisia", "Turkey", "Türkiye", "Uganda", "Ukraine",
    "United Arab Emirates", "UAE", "United Kingdom", "UK", "Uruguay", "Uzbekistan",
    "Venezuela", "Vietnam", "Zambia", "Zimbabwe",
)


def _pattern(term):
    body = r"\s+".join(re.escape(word) for word in term.split())
    return re.compile(r"(?<!\w)" + body + r"(?!\w)", re.IGNORECASE)


_PATTERNS = {}


def find_terms(text, terms):
    """Return the terms that occur in text as whole words, in list order."""
    found = []
    for term in terms:
        if term not in _PATTERNS:
            _PATTERNS[term] = _pattern(term)
        if _PATTERNS[term].search(text or ""):
            found.append(term)
    return found


def check_role(title):
    role = find_terms(title, ROLE_TERMS)
    early = find_terms(title, EARLY_CAREER_TERMS)
    if role:
        return True, "1(a)", role
    if early and find_terms(title, ("Software Engineer",)):
        return True, "1(b)", ["Software Engineer"] + early
    return False, None, []


def check_seniority(title):
    senior = find_terms(title, SENIOR_TERMS)
    return not senior, senior


def check_location(location):
    us = find_terms(location, US_TERMS + US_STATES)
    if us:
        return True, "names " + ", ".join(repr(t) for t in us)
    if find_terms(location, ("Remote",)):
        foreign = find_terms(location, NON_US_COUNTRIES)
        if foreign:
            return False, "Remote but names non-US country " + ", ".join(repr(t) for t in foreign)
        return True, "Remote without naming a non-US country"
    return False, "names neither the United States, a US state, nor Remote"


def judge(title, location, targets=None):
    if targets is None:
        from persona import load_persona
        targets = load_persona()[1]
    role_ok, role_path, role_hits = check_role(title)
    senior_ok, senior_hits = check_seniority(title)
    location_ok, location_reason = check_location(location)
    early = find_terms(title, EARLY_CAREER_TERMS)
    verdict = RELEVANT if role_ok and senior_ok and location_ok else NOT_RELEVANT

    role = targets["target_role"]
    geo = targets["geography"]
    if role_ok:
        role_text = f"check 1 passes via {role_path} on {', '.join(repr(t) for t in role_hits)}"
    else:
        role_text = "check 1 fails: no 1(a) term and no 1(b) 'Software Engineer' + early-career pair"
    senior_text = ("check 2 passes: no seniority or internship term" if senior_ok else
                   f"check 2 fails on {', '.join(repr(t) for t in senior_hits)}")
    location_text = f"check 3 {'passes' if location_ok else 'fails'}: {location_reason}"
    parts = [
        f"{verdict.upper()}.",
        f"posting.title={title!r}: {role_text}; {senior_text}.",
        f"Compared with targets.target_role.primary={role['primary']!r} and "
        f"targets.target_role.secondary={role['secondary']!r}.",
        f"posting.location.name={location!r}: {location_text}.",
        f"Compared with targets.geography.current_location={geo['current_location']!r} and "
        f"targets.geography.open_to_remote={str(geo['open_to_remote']).lower()}.",
    ]
    if early:
        parts.append(f"Early-career signal in posting.title: {', '.join(repr(t) for t in early)}.")
    return {
        "verdict": verdict,
        "source": "written rule (record)",
        "checks": {"role": role_ok, "role_path": role_path, "not_too_senior": senior_ok,
                   "location": location_ok},
        "cited_posting_fields": list(POSTING_FIELDS),
        "cited_resume_fields": list(RESUME_FIELDS),
        "justification": " ".join(parts),
    }


def justification_errors(result):
    """Wrong version 2: reject a justification that cites no posting or résumé fields."""
    errors = []
    text = result.get("justification") or ""
    posting = [f for f in result.get("cited_posting_fields") or [] if f in text]
    resume = [f for f in result.get("cited_resume_fields") or [] if f in text]
    if not posting:
        errors.append("justification names no posting field")
    if not resume:
        errors.append("justification names no résumé field")
    return errors
