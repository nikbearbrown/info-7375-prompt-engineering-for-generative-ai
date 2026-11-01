"""Constructed test postings — NOT real Stripe postings. Shaped like Greenhouse's /jobs?content=true."""

import html
import json
from pathlib import Path

PERSONA = Path(__file__).resolve().parent.parent / "persona" / "rohan-desai.resume.example.json"


def job(id, title, location, body, published="2026-10-20T10:00:00-04:00"):
    return {
        "id": id,
        "title": title,
        "location": {"name": location},
        "departments": [{"id": 1, "name": "Engineering"}],
        "absolute_url": f"https://example.invalid/jobs/{id}",
        "first_published": published,
        "content": html.escape(f"<div><p>{body}</p></div>"),  # Greenhouse double-escapes HTML
    }


RELEVANT = job(101, "Software Engineer, New Grad", "San Francisco, Seattle, New York",
               "You have experience with Java or Python and have deployed services on AWS.")
ONE_SKILL = job(102, "Software Engineer, Intern", "New York", "Comfortable in Java. Go build things with us.")
NON_US = job(103, "Software Engineer, New Grad", "Dublin", "Python, Java and Kubernetes experience.")
EARLY_CAREER = job(104, "Software Engineer, Early Career — Immediate Start", "Seattle", "Python, Go and SQL.")
SENIOR = job(105, "Staff Software Engineer, Payments", "US-Remote", "Golang, PostgreSQL, Docker.")
INTERNAL = job(106, "Software Engineer, Internal Identity", "Chicago", "Java, SQL and AWS.")

ALL = [RELEVANT, ONE_SKILL, NON_US, EARLY_CAREER, SENIOR, INTERNAL]
EXPECTED = {"101": "RELEVANT", "102": "NOT RELEVANT", "103": "NOT RELEVANT",
            "104": "NOT RELEVANT", "105": "NOT RELEVANT", "106": "NOT RELEVANT"}


def response(jobs):
    return json.dumps({"jobs": jobs, "meta": {"total": len(jobs)}}).encode()


def persona():
    return json.loads(PERSONA.read_text())
