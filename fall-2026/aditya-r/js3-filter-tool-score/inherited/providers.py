"""Provider adapters: build the board URL from validated config, and validate and normalize a 200 body.

Postings are normalized to the Greenhouse shape that the inherited rule, judge and validator read
(id, title, content as entity-escaped HTML, location.name, departments[].name, absolute_url).
"""
import html
import re

from .board import BoardError, decode_body, parse_jobs


class SuspectEmpty(BoardError):
    """An empty jobs array from a selected board (GATE.md §4): a failure, never 'zero new'."""


class Greenhouse:
    name = "greenhouse"
    token_re = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")

    @staticmethod
    def url(board):
        return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"

    @staticmethod
    def parse(body):
        jobs = parse_jobs(decode_body(body))  # integer ids, duplicates, meta / meta.total checks
        if not jobs:
            raise SuspectEmpty("suspect-empty: the jobs array is empty for a board previously observed nonempty")
        return [(str(j["id"]), j) for j in jobs]


class Ashby:
    name = "ashby"
    token_re = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")

    @staticmethod
    def url(board):
        return f"https://api.ashbyhq.com/posting-api/job-board/{board}"

    @staticmethod
    def parse(body):
        data = decode_body(body)
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise BoardError("board response has no 'jobs' array")
        out, seen = [], set()
        for i, job in enumerate(data["jobs"]):
            if not isinstance(job, dict):
                raise BoardError(f"jobs[{i}] is not an object")
            jid = job.get("id")
            if not isinstance(jid, str) or not jid.strip():
                raise BoardError(f"jobs[{i}] has a missing or non-string id (Ashby ids are an observed dependency)")
            if jid in seen:
                raise BoardError(f"duplicate posting id {jid}")
            seen.add(jid)
            dept = job.get("department")
            out.append((jid, {
                "id": jid,
                "title": job.get("title"),
                "content": html.escape(job.get("descriptionHtml") or ""),
                "location": {"name": job.get("location")},
                "departments": [{"name": dept}] if dept else [],
                "absolute_url": job.get("jobUrl"),
            }))
        if not out:
            raise SuspectEmpty("suspect-empty: the jobs array is empty for a board previously observed nonempty")
        return out


PROVIDERS = {"greenhouse": Greenhouse, "ashby": Ashby}
