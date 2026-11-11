"""Ashby job board — the third applicant-tracking system.

`GET https://api.ashbyhq.com/posting-api/job-board/<token>`

Ashby returns `{"jobs": [...]}` like Greenhouse but with flat fields, and it
publishes an `isListed` flag. Unlisted postings are dropped here rather than
reported, and the count of dropped postings is returned to the caller so the
loop can record it — a posting the adapter silently removed would otherwise
look to the cross-check like a posting that disappeared from the board.
"""

from __future__ import annotations

from ..errors import SchemaFailure
from .base import Posting, Provider


class Ashby(Provider):
    name = "ashby"
    host = "api.ashbyhq.com"

    def url_for(self, token: str) -> str:
        return f"https://{self.host}/posting-api/job-board/{token}"

    def parse(self, board: str, payload) -> list[Posting]:
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
            raise SchemaFailure(
                f"{board}: ashby payload has no 'jobs' array "
                f"(top level is {type(payload).__name__})"
            )
        out: list[Posting] = []
        self.dropped_unlisted = 0
        for job in payload["jobs"]:
            if not isinstance(job, dict) or "id" not in job:
                raise SchemaFailure(f"{board}: an ashby posting has no 'id'")
            if job.get("isListed") is False:
                self.dropped_unlisted += 1
                continue
            family, family_path = self._job_family(job)
            out.append(
                Posting(
                    board=board,
                    provider=self.name,
                    posting_id=str(job["id"]),
                    title=self._text(job.get("title")),
                    location=self._text(job.get("location")),
                    job_family=family,
                    url=self._text(job.get("jobUrl")) or self._text(job.get("applyUrl")),
                    provider_field={
                        "title": "title",
                        "location": "location",
                        "job_family": family_path,
                    },
                    raw=job,
                )
            )
        return out

    @staticmethod
    def _job_family(job: dict) -> tuple[str | None, str]:
        for key in ("department", "team"):
            value = job.get(key)
            if isinstance(value, str) and value.strip():
                return value, key
        return None, "department"
