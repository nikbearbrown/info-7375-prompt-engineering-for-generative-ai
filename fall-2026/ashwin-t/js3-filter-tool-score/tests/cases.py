"""Hand-written posting cases for FILTER.md v1.0. Expected values come from reading FILTER.md, not from running the filter.

Each case: name, posting, expected decision, expected score (None = not checked), and the wrong
version(s) it is meant to catch.
"""

BODY_3 = "<p>We use Python, PostgreSQL and Docker every day.</p>"           # 3 topic groups
BODY_2 = "<p>You will write Python services backed by Redis.</p>"           # 2 groups


def posting(title="Software Engineer", location="Boston, MA", offices=(), content=BODY_2, key=None, **extra):
    p = {"key": key or f"greenhouse/test/{abs(hash((title, location, content))) % 10**8}",
         "provider": "greenhouse", "board": "test", "id": "1", "title": title,
         "location": {"name": location}, "offices": [{"name": o} for o in offices],
         "content": content, "absolute_url": "https://example.invalid/job", "structured": {}}
    p.update(extra)
    return p


CASES = [
    # name, posting, decision, score, catches
    ("boston, 2 groups -> 3+2+2=7 keep", posting(), "KEEP", 7, []),
    ("other US city, 2 groups -> 6 reject (needs 3)", posting(location="Denver, CO"), "REJECT", 6, []),
    ("other US city, 3 groups -> 7 keep", posting(location="New York, NY", content=BODY_3), "KEEP", 7, []),
    ("1 group in Boston -> reject on minimum groups", posting(content="<p>Python only.</p>"), "REJECT", 6, []),
    ("topic cap 4: 7 groups still adds 4",
     posting(content="python java postgres redis docker kubernetes distributed systems"), "KEEP", 9, []),
    ("JavaScript is not Java (W1)",
     posting(location="Denver, CO", content="<p>Python and JavaScript, PostgreSQL.</p>"), "REJECT", 6, ["W1"]),
    ("SRE does not contain the term sr (W1)",
     posting(title="Software Engineer, SRE Tooling", content=BODY_3), "KEEP", 8, ["W1"]),
    ("support role with many tools stays rejected (W2)",
     posting(title="Support Engineer", content="python java postgres redis docker kubernetes"), "REJECT", None, ["W2"]),
    ("Remote, Global -> REVIEW, not keep (W3)", posting(location="Remote, Global", content=BODY_3), "REVIEW", None, ["W3"]),
    ("no location at all -> REVIEW (W3)", posting(location=None, content=BODY_3), "REVIEW", None, ["W3"]),
    ("missing description -> REVIEW, not reject (W4)", posting(content=""), "REVIEW", None, ["W4"]),
    ("Boston in boilerplate, London job -> reject (W5)",
     posting(location="London, United Kingdom", content="<p>Python, Redis, Docker. HQ in Boston.</p>"),
     "REJECT", None, ["W5"]),
    ("python + python3 count once (W6)",
     posting(location="Denver, CO", content="<p>python3 and Python and PostgreSQL</p>"), "REJECT", 6, ["W6"]),
    ("forward deployed software engineer excluded (W8)",
     posting(title="Forward Deployed Software Engineer", content=BODY_3), "REJECT", None, ["W8"]),
    ("level II attached to role excluded", posting(title="Software Engineer II - Recommendations"), "REJECT", None, []),
    ("senior excluded even with high score", posting(title="Senior Software Engineer", content=BODY_3), "REJECT", None, []),
    ("hyphenated full-stack matches", posting(title="Full-Stack Engineer"), "KEEP", 7, []),
    ("US remote is preferred (2)", posting(location="Remote - USA"), "KEEP", 7, []),
    ("Boston office alternative wins over London primary",
     posting(location="London, UK", offices=["Boston, MA"]), "KEEP", 7, []),
    ("all non-US alternatives -> reject on location", posting(location="Dublin, Ireland", content=BODY_3), "REJECT", None, []),
    ("non-US primary + ambiguous alternative -> REVIEW",
     posting(location="Dublin, Ireland", offices=["North America"], content=BODY_3), "REVIEW", None, []),
    ("exclusion beats ambiguous location",
     posting(title="Staff Software Engineer", location="Remote, Global", content=BODY_3), "REJECT", None, []),
]
