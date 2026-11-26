"""Helpers for the Job-Search Agent 3 tests.

Every posting and board body built here is a CONSTRUCTED test fixture, not a board result.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RESUME = ROOT / "resumes" / "aarav-patel.json"


def resume():
    return json.loads(RESUME.read_text())


def _escape(html):
    # Greenhouse sends `content` as entity-escaped HTML.
    return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gh_job(job_id, title="Software Engineer", location="Boston, MA",
           content="<p>Backend API services in Python, SQL and Docker on AWS.</p>", url=True):
    job = {"id": job_id, "title": title, "location": {"name": location}, "content": _escape(content)}
    if url:
        job["absolute_url"] = f"https://example.invalid/gh/{job_id}"
    return job


def gh_body(*jobs):
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode()


def lever_posting(posting_id, text="Software Engineer, Backend", location="United States",
                  description="<div>Backend API services in Python and PostgreSQL.</div>",
                  workplace_type="remote", lists=(), additional=""):
    return {"id": posting_id, "text": text,
            "categories": {"location": location, "team": "Engineering"},
            "description": description, "lists": [{"text": "x", "content": c} for c in lists],
            "additional": additional, "workplaceType": workplace_type,
            "hostedUrl": f"https://example.invalid/lever/{posting_id}"}


def lever_body(*postings):
    return json.dumps(list(postings)).encode()
