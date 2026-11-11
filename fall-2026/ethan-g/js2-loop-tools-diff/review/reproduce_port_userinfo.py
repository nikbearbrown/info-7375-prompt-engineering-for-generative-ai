"""Reproduce the review-packet defect offline: does the URL check accept a non-443 port or user information?

    python3 review/reproduce_port_userinfo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jsagent import fetch, policy  # noqa: E402

HOSTS = {"boards-api.greenhouse.io", "api.lever.co"}
URLS = [
    ("expected allow", "https://boards-api.greenhouse.io/v1/boards/samsara/jobs"),
    ("expected allow", "https://boards-api.greenhouse.io:443/v1/boards/samsara/jobs"),
    ("expected deny ", "https://boards-api.greenhouse.io:8443/v1/boards/samsara/jobs"),
    ("expected deny ", "https://user:pw@boards-api.greenhouse.io/v1/boards/samsara/jobs"),
    ("expected deny ", "https://user@api.lever.co/v0/postings/palantir?mode=json"),
    ("expected deny ", "https://boards-api.greenhouse.io.evil.com/v1/boards/samsara/jobs"),
]


def decide(fn, url):
    try:
        fn(url, HOSTS)
        return "ALLOWED"
    except (fetch.HostNotAllowed, policy.PolicyViolation):
        return "refused"


wrong = 0
for expected, url in URLS:
    got = decide(policy.check_url, url)
    bad = (expected.strip() == "expected deny" and got == "ALLOWED") or (expected.strip() == "expected allow" and got != "ALLOWED")
    wrong += bad
    print(f"{expected}  policy.check_url -> {got:8} {'<-- DEFECT' if bad else ''}  {url}")
print(f"{wrong} URL(s) decided against GATE.md section 5")
sys.exit(1 if wrong else 0)
