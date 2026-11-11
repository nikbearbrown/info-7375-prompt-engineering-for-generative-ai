"""Lever postings — the second applicant-tracking system.

`GET https://api.lever.co/v0/postings/<token>?mode=json`

Three differences from Greenhouse that the normalisation has to absorb, and
that are worth naming because each one is a place a careless adapter would
invent a value:

* the payload is a bare JSON **array**, not an object with a `jobs` key;
* the title lives in `text`, not `title`;
* there is no "Job Family". The nearest honest equivalent is
  `categories.team`, and `categories.department` when there is no team. Where
  neither exists the normalised `job_family` is `None` — **not** a guess, and
  not the empty string, because the rule's G3 treats absent and present
  differently.
"""

from __future__ import annotations

from ..errors import SchemaFailure
from .base import Posting, Provider


class Lever(Provider):
    name = "lever"
    host = "api.lever.co"

    def url_for(self, token: str) -> str:
        return f"https://{self.host}/v0/postings/{token}?mode=json"

    def parse(self, board: str, payload) -> list[Posting]:
        if not isinstance(payload, list):
            raise SchemaFailure(
                f"{board}: lever payload is {type(payload).__name__}, expected a JSON array"
            )
        out: list[Posting] = []
        for job in payload:
            if not isinstance(job, dict) or "id" not in job:
                raise SchemaFailure(f"{board}: a lever posting has no 'id'")
            categories = job.get("categories")
            categories = categories if isinstance(categories, dict) else {}
            family, family_path = self._job_family(categories)
            out.append(
                Posting(
                    board=board,
                    provider=self.name,
                    posting_id=str(job["id"]),
                    title=self._text(job.get("text")),
                    location=self._text(categories.get("location")),
                    job_family=family,
                    url=self._text(job.get("hostedUrl")),
                    provider_field={
                        "title": "text",
                        "location": "categories.location",
                        "job_family": family_path,
                    },
                    raw=job,
                )
            )
        return out

    @staticmethod
    def _job_family(categories: dict) -> tuple[str | None, str]:
        for key in ("team", "department"):
            value = categories.get(key)
            if isinstance(value, str) and value.strip():
                return value, f"categories.{key}"
        return None, "categories"
