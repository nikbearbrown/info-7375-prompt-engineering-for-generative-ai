"""Reading the Ashby board response (CONTRACT.md, In: what counts as a broken board answer)."""

from __future__ import annotations

import json

from .errors import BrokenInput


def parse(status: int, body: bytes) -> list:
    """Return the board's jobs, or raise BrokenInput for any answer the contract calls broken."""
    if status != 200:
        raise BrokenInput(f"the board answered HTTP {status}, not 200")
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise BrokenInput(f"the board's answer is not JSON ({type(exc).__name__})") from None
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BrokenInput("the board's answer has no jobs list")
    jobs = data["jobs"]
    if not jobs:
        raise BrokenInput("the board's jobs list is empty")
    for index, job in enumerate(jobs):
        if not isinstance(job, dict):
            raise BrokenInput(f"job {index} is not an object")
        for key in ("id", "title"):
            value = job.get(key)
            if not isinstance(value, str) or not value.strip():
                raise BrokenInput(f"job {index} has no {key}")
    return jobs
