"""Shared helpers for the tests. Every posting built here is CONSTRUCTED for testing,
not a real Oscar posting; real postings only come from runs/raw/."""
import html
import json
import pathlib

FOLDER = pathlib.Path(__file__).resolve().parent.parent
PERSONA_PATH = FOLDER / "persona" / "alex_morgan.json"

RESUME_FIELDS = {"target_roles", "experience_years", "skills", "location", "remote_ok", "exclusions"}
POSTING_FIELDS = {"id", "title", "departments", "location", "offices", "content"}


def load_persona():
    return json.loads(PERSONA_PATH.read_text())


def make_job(job_id, title="Software Engineer", department="Engineering",
             location="Boston, Massachusetts, United States", offices=("Boston, MA",),
             content="<p>We use Python and Docker. 2+ years of experience required.</p>"):
    """A Greenhouse-shaped job (content escaped once, as the real API does)."""
    return {
        "id": job_id,
        "title": title,
        "departments": [{"name": department}] if department else [],
        "location": {"name": location},
        "offices": [{"name": o} for o in offices],
        "content": html.escape(content),
        "absolute_url": f"https://example.com/jobs/{job_id}",
        "updated_at": "2026-10-28T00:00:00-04:00",
    }


def board_payload(jobs):
    return json.dumps({"jobs": jobs, "meta": {"total": len(jobs)}}).encode()


def cites_real_fields(line):
    """True when a justification line names at least one real resume field and one
    real posting field, written as resume.<field> and posting.<field>."""
    has_resume = any(f"resume.{f}" in line for f in RESUME_FIELDS)
    has_posting = any(f"posting.{f}" in line for f in POSTING_FIELDS)
    return has_resume and has_posting


def justification_ok(record):
    lines = [l for l in record["justification"].splitlines() if l.strip()]
    return bool(lines) and all(cites_real_fields(l) for l in lines)
