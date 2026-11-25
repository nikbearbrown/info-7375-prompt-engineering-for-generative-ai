"""Constructed postings for the JS3 tests. CONSTRUCTED: none of these is a real posting.

Each builder returns a raw job shaped like the board's API (Greenhouse sends `content` as
escaped HTML; Ashby sends `descriptionHtml` and `descriptionPlain`), so the tests also
exercise how agent3 reads each field. The modules under test are imported lazily so
that, before agent3 exists, every test fails on its own.
"""
import html
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Neutral filler: no role word, skill, location, visa, remote, hybrid, onsite or office word.
FILLER = " ".join(["The team ships careful work for customers every week."] * 7)  # 377 chars


def flt():
    return importlib.import_module("agent3.filter")


def sl():
    return importlib.import_module("agent3.shortlist")


def resume():
    return json.loads((ROOT / "data" / "resume.example.json").read_text(encoding="utf-8"))


def skills():
    return flt().shipped_skills(resume())


def body(extra=""):
    """Posting text long enough not to abstain, plus any sentence a test needs."""
    return f"<p>{FILLER}</p><p>{extra}</p>"


def gh_job(title="Data Scientist", location="New York City, NY", content=None, job_id=1, drop=()):
    """A Greenhouse-shaped job. drop names top-level fields to remove entirely."""
    job = {"id": job_id, "title": title, "location": {"name": location},
           "content": html.escape(body() if content is None else content)}
    for field in drop:
        job.pop(field, None)
    return job


def ashby_job(title="Data Scientist", location="US California - Remote", html_text=None,
              plain_text=None, job_id="a-1"):
    job = {"id": job_id, "title": title, "location": location,
           "descriptionHtml": body() if html_text is None else html_text,
           "descriptionPlain": FILLER if plain_text is None else plain_text}
    return job


def gh(title="Data Scientist", location="New York City, NY", content=None, board_status="ok", drop=()):
    return flt().make_posting("greenhouse", "faire", gh_job(title, location, content, drop=drop),
                              board_status=board_status)


def ashby(title="Data Scientist", location="US California - Remote", html_text=None, plain_text=None):
    return flt().make_posting("ashby", "poshmark", ashby_job(title, location, html_text, plain_text))


def verdict(posting):
    return flt().evaluate(posting, skills())


def claim(posting, number, skill=None):
    """The single label dict for C1, C3 or C4, or C2 for one named skill."""
    s = sl()
    if number == 1:
        return s.label_c1(posting)
    if number == 2:
        return s.label_c2(posting, skill)
    if number == 3:
        return s.label_c3(posting)
    if number == 4:
        return s.label_c4(posting)
    raise ValueError(number)
