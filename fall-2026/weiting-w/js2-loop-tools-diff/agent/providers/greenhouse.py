"""Greenhouse board listing — the provider JS1 was built against.

`GET https://boards-api.greenhouse.io/v1/boards/<token>/jobs`

Two things JS1 established about this provider the hard way and that are
preserved here: the listing endpoint returns **no** `departments` key, and the
discipline signal is the `metadata` entry named `"Job Family"` — on the board
JS1 watched, 10 of 161 postings carried that entry with a null value.
"""

from __future__ import annotations

from ..errors import SchemaFailure
from .base import Posting, Provider

JOB_FAMILY_KEY = "Job Family"


class Greenhouse(Provider):
    name = "greenhouse"
    host = "boards-api.greenhouse.io"

    def url_for(self, token: str) -> str:
        return f"https://{self.host}/v1/boards/{token}/jobs"

    def parse(self, board: str, payload) -> list[Posting]:
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
            raise SchemaFailure(
                f"{board}: greenhouse payload has no 'jobs' array "
                f"(top level is {type(payload).__name__})"
            )
        out: list[Posting] = []
        for job in payload["jobs"]:
            if not isinstance(job, dict) or "id" not in job:
                raise SchemaFailure(f"{board}: a greenhouse posting has no 'id'")
            family, family_path = self._job_family(job)
            location = ""
            loc = job.get("location")
            if isinstance(loc, dict):
                location = self._text(loc.get("name"))
            out.append(
                Posting(
                    board=board,
                    provider=self.name,
                    posting_id=str(job["id"]),
                    title=self._text(job.get("title")),
                    location=location,
                    job_family=family,
                    url=self._text(job.get("absolute_url")),
                    provider_field={
                        "title": "title",
                        "location": "location.name",
                        "job_family": family_path,
                    },
                    raw=job,
                )
            )
        return out

    @staticmethod
    def _job_family(job: dict) -> tuple[str | None, str]:
        metadata = job.get("metadata")
        if isinstance(metadata, list):
            for i, entry in enumerate(metadata):
                if isinstance(entry, dict) and entry.get("name") == JOB_FAMILY_KEY:
                    value = entry.get("value")
                    if isinstance(value, str) and value.strip():
                        return value, f"metadata[{i}].value"
                    # present but null: 10 of 161 real postings on the JS1 board
                    return None, f"metadata[{i}].name"
        return None, "metadata"
