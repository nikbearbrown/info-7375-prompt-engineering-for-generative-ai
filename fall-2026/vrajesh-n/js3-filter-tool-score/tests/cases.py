"""CONSTRUCTED postings for FILTER.md v1 (not from any board). Each case: (name, posting, verdict, failed_check).
Written before the rule code. Shared by the real rule's tests and by the wrong-version tests."""


def posting(title, location="Boston, MA, United States", country="USA",
            desc="Build and ship web services with the team."):
    address = {"postalAddress": {"addressCountry": country}} if country else None
    return {"id": "c-" + title.lower().replace(" ", "-")[:40], "title": title, "location": location,
            "address": address, "descriptionPlain": desc}


ROLE_TITLES = [  # Vrajesh's list, FILTER.md section 1
    "Backend Engineer", "Java Engineer", "Python Engineer", ".NET Engineer", "Full Stack Engineer",
    "Frontend Software Engineer", "React Developer", "UI/UX Developer", "AI Engineer", "LLM Engineer",
    "Solutions Architect", "Forward Deployed Engineer",
]

CASES = [(f"role: {t}", posting(t), "relevant", None) for t in ROLE_TITLES] + [
    # R1 and the ML exclusion
    ("ML engineer is not wanted", posting("Machine Learning Engineer"), "not_relevant", "R1"),
    ("ML in a software title is not wanted", posting("Software Engineer, Machine Learning"), "not_relevant", "R1"),
    ("non-engineering title", posting("Recruiter"), "not_relevant", "R1"),
    # W2: 'training' in the description must never make a posting relevant
    ("training in description only", posting("Recruiter", desc="Run training and onboarding programs for AI teams."),
     "not_relevant", "R1"),
    # W1: seniority
    ("Senior in title", posting("Senior Software Engineer"), "not_relevant", "R2"),
    ("Staff in title", posting("Staff Backend Engineer"), "not_relevant", "R2"),
    ("3+ years in description", posting("Software Engineer", desc="You have 5+ years of experience."),
     "not_relevant", "R2"),
    # W3: clearance
    ("clearance required", posting("Software Engineer", desc="Active TS/SCI security clearance required."),
     "not_relevant", "R5"),
    ("clearance negated", posting("Software Engineer", desc="No security clearance is required."),
     "relevant", None),
    # R3, R4
    ("non-US location", posting("Software Engineer", location="Toronto, Canada", country=None),
     "not_relevant", "R3"),
    ("cannot sponsor", posting("Software Engineer", desc="We are unable to sponsor visas."),
     "not_relevant", "R4"),
    # cannot_tell: location or description not mentioned
    ("location missing", posting("Software Engineer", location=None, country=None), "cannot_tell", None),
    ("description missing", posting("Software Engineer", desc=""), "cannot_tell", None),
    ("title rejects even when description missing", posting("Recruiter", desc=""), "not_relevant", "R1"),
]
